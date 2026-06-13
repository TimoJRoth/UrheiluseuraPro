"""Yhteyshenkilöhavaintojen merge – append-only, roolikohtainen master."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from urheiluseurapro.merge.priorities import resolve_source_priority
from urheiluseurapro.models.club import Club, ClubContactPerson
from urheiluseurapro.models.contact_person import (
    ContactPersonObservation,
    MasterContactPerson,
    ObservationContactPerson,
)
from urheiluseurapro.models.enums import ContactPersonRole
from urheiluseurapro.models.observation import ClubObservation
from urheiluseurapro.models.source import Source
from urheiluseurapro.normalization.fields import (
    normalize_club_name,
    normalize_email,
    normalize_phone,
    normalize_text,
)

_ROLE_ALIASES: dict[str, str] = {
    "puheenjohtaja": ContactPersonRole.CHAIR.value,
    "pj": ContactPersonRole.CHAIR.value,
    "chair": ContactPersonRole.CHAIR.value,
    "sihteeri": ContactPersonRole.SECRETARY.value,
    "toiminnanjohtaja": ContactPersonRole.MANAGING_DIRECTOR.value,
    "toimihenkilö": ContactPersonRole.MANAGING_DIRECTOR.value,
    "rahastonhoitaja": ContactPersonRole.TREASURER.value,
    "taloudenhoitaja": ContactPersonRole.TREASURER.value,
    "junioripäällikkö": ContactPersonRole.JUNIOR_DIRECTOR.value,
    "junioripaallikko": ContactPersonRole.JUNIOR_DIRECTOR.value,
    "valmennuspäällikkö": ContactPersonRole.COACHING_DIRECTOR.value,
    "valmennuspaallikko": ContactPersonRole.COACHING_DIRECTOR.value,
    "yhteyshenkilö": ContactPersonRole.CONTACT.value,
    "yhteyshenkilo": ContactPersonRole.CONTACT.value,
    "contact": ContactPersonRole.CONTACT.value,
    "muu": ContactPersonRole.OTHER.value,
}


def normalize_contact_role(role: str | None) -> str:
    """Normalisoi rooli standardiavaimeksi."""
    if not role:
        return ContactPersonRole.CONTACT.value
    text = normalize_text(role)
    if not text:
        return ContactPersonRole.CONTACT.value
    key = text.lower()
    if key in _ROLE_ALIASES:
        return _ROLE_ALIASES[key]
    for role_enum in ContactPersonRole:
        if key == role_enum.value:
            return role_enum.value
    return ContactPersonRole.OTHER.value


def _normalize_emails(emails: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for email in emails:
        normalized = normalize_email(email)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def _normalize_phones(phones: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for phone in phones:
        normalized = normalize_phone(phone)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def extract_contact_persons_from_observation(
    observation: ClubObservation,
) -> list[ObservationContactPerson]:
    """Poimi yhteyshenkilöt havainnosta (uusi lista + legacy-kentät)."""
    persons: list[ObservationContactPerson] = list(observation.contact_persons)

    if observation.contact_person_name:
        legacy_emails = (
            [observation.contact_person_email]
            if observation.contact_person_email
            else []
        )
        legacy_phones = (
            [observation.contact_person_phone]
            if observation.contact_person_phone
            else []
        )
        legacy = ObservationContactPerson(
            full_name=observation.contact_person_name,
            role=observation.contact_person_role,
            emails=legacy_emails,
            phones=legacy_phones,
        )
        if not any(
            p.full_name.strip().lower() == legacy.full_name.strip().lower()
            and normalize_contact_role(p.role) == normalize_contact_role(legacy.role)
            for p in persons
        ):
            persons.append(legacy)

    return persons


def _contact_person_fingerprint(
    observation_id: str,
    role: str,
    normalized_name: str,
) -> tuple[str, str, str]:
    return (observation_id, role, normalized_name)


@dataclass(frozen=True)
class _ContactPersonGroup:
    normalized_name: str
    display_name: str
    observations: tuple[ContactPersonObservation, ...]


def append_contact_person_observations(
    club: Club,
    observation: ClubObservation,
) -> tuple[Club, list[ContactPersonObservation]]:
    """Lisää yhteyshenkilöhavainnot append-only -periaatteella."""
    existing_keys = {
        _contact_person_fingerprint(
            cp.observation_id,
            cp.role,
            normalize_club_name(cp.full_name) or cp.full_name.strip().lower(),
        )
        for cp in club.contact_person_observations
    }

    preserved: list[ContactPersonObservation] = list(club.contact_person_observations)
    added: list[ContactPersonObservation] = []
    seen_at = observation.collected_at

    for person in extract_contact_persons_from_observation(observation):
        role = normalize_contact_role(person.role)
        normalized_name = normalize_club_name(person.full_name) or person.full_name.strip().lower()
        fingerprint = _contact_person_fingerprint(
            observation.observation_id,
            role,
            normalized_name,
        )
        if fingerprint in existing_keys:
            continue

        record = ContactPersonObservation(
            id=str(uuid4()),
            role=role,
            role_raw=person.role,
            full_name=person.full_name.strip(),
            emails=_normalize_emails(person.emails),
            phones=_normalize_phones(person.phones),
            source_id=observation.source_id,
            observation_id=observation.observation_id,
            source_record_key=observation.source_record_key,
            source_url=str(observation.source_url) if observation.source_url else None,
            first_seen_at=seen_at,
            last_seen_at=seen_at,
            observation_confidence=person.observation_confidence,
        )
        preserved.append(record)
        existing_keys.add(fingerprint)
        added.append(record)

    if not added:
        return club, added

    return club.model_copy(update={"contact_person_observations": preserved}), added


def _observation_score(
    obs: ContactPersonObservation,
    sources: dict[str, Source],
) -> tuple[int, float]:
    priority = resolve_source_priority(sources.get(obs.source_id), obs.source_id)
    return (priority, obs.last_seen_at.timestamp())


def _group_by_name(
    observations: list[ContactPersonObservation],
) -> list[_ContactPersonGroup]:
    buckets: dict[str, list[ContactPersonObservation]] = defaultdict(list)
    display: dict[str, str] = {}

    for obs in observations:
        key = normalize_club_name(obs.full_name) or obs.full_name.strip().lower()
        buckets[key].append(obs)
        if key not in display:
            display[key] = obs.full_name

    return [
        _ContactPersonGroup(
            normalized_name=key,
            display_name=display[key],
            observations=tuple(group),
        )
        for key, group in buckets.items()
    ]


def _compute_contact_confidence(
    winner: _ContactPersonGroup,
    *,
    total_groups: int,
    sources: dict[str, Source],
) -> float:
    max_priority = max(
        resolve_source_priority(sources.get(obs.source_id), obs.source_id)
        for obs in winner.observations
    )
    agreement = len({obs.source_id for obs in winner.observations})
    has_conflict = total_groups > 1

    confidence = (max_priority / 100.0) * 0.65 + min(0.25, agreement * 0.08)

    confidences = [
        obs.observation_confidence
        for obs in winner.observations
        if obs.observation_confidence is not None
    ]
    if confidences:
        confidence += sum(confidences) / len(confidences) * 0.1

    if has_conflict:
        confidence *= 0.75

    return round(min(1.0, max(0.05, confidence)), 3)


def recompute_master_contact_persons(
    club: Club,
    sources: dict[str, Source],
) -> dict[str, MasterContactPerson]:
    """Laske roolikohtaiset master-yhteyshenkilöt kaikista havainnoista."""
    by_role: dict[str, list[ContactPersonObservation]] = defaultdict(list)
    for obs in club.contact_person_observations:
        by_role[obs.role].append(obs)

    masters: dict[str, MasterContactPerson] = {}
    now = datetime.now(timezone.utc)

    for role, observations in by_role.items():
        groups = _group_by_name(observations)
        if not groups:
            continue

        ranked = sorted(
            groups,
            key=lambda g: (
                max(_observation_score(obs, sources) for obs in g.observations),
                len({obs.source_id for obs in g.observations}),
            ),
            reverse=True,
        )
        winner = ranked[0]
        primary = max(winner.observations, key=lambda obs: _observation_score(obs, sources))

        conflicting = [
            g.display_name for g in ranked[1:] if g.normalized_name != winner.normalized_name
        ]

        all_emails = list(primary.emails)
        all_phones = list(primary.phones)

        masters[role] = MasterContactPerson(
            role=role,
            full_name=winner.display_name,
            emails=all_emails,
            phones=all_phones,
            confidence_score=_compute_contact_confidence(
                winner,
                total_groups=len(groups),
                sources=sources,
            ),
            supporting_sources=sorted({obs.source_id for obs in winner.observations}),
            supporting_observation_ids=[obs.id for obs in winner.observations],
            primary_source_id=primary.source_id,
            primary_contact_person_observation_id=primary.id,
            selected_at=now,
            has_conflict=bool(conflicting),
            conflicting_names=conflicting,
        )

    return masters


def _pick_primary_contact_person(
    masters: dict[str, MasterContactPerson],
    sources: dict[str, Source],
) -> MasterContactPerson | None:
    if not masters:
        return None
    if ContactPersonRole.CONTACT.value in masters:
        return masters[ContactPersonRole.CONTACT.value]

    return max(
        masters.values(),
        key=lambda m: resolve_source_priority(sources.get(m.primary_source_id), m.primary_source_id),
    )


def apply_contact_person_masters(
    club: Club,
    masters: dict[str, MasterContactPerson],
    sources: dict[str, Source],
) -> Club:
    """Päivitä master-yhteyshenkilöt ja legacy contact_person -näkymä."""
    primary = _pick_primary_contact_person(masters, sources)
    contact_person = ClubContactPerson()
    if primary:
        contact_person = ClubContactPerson(
            name=primary.full_name,
            role=primary.role,
            email=primary.emails[0] if primary.emails else None,
            phone=primary.phones[0] if primary.phones else None,
        )

    needs_review = club.quality.needs_review or any(m.has_conflict for m in masters.values())

    return club.model_copy(
        update={
            "master_contact_persons": masters,
            "contact_person": contact_person,
            "contact_person_observations": list(club.contact_person_observations),
            "quality": club.quality.model_copy(update={"needs_review": needs_review}),
        }
    )


def get_contact_person_observations(
    club: Club,
    *,
    role: str | None = None,
) -> list[ContactPersonObservation]:
    """Hae kaikki tai roolikohtaiset yhteyshenkilöhavainnot."""
    if role is None:
        return list(club.contact_person_observations)
    normalized_role = normalize_contact_role(role)
    return [cp for cp in club.contact_person_observations if cp.role == normalized_role]
