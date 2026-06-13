"""Lähteiden yhdistäminen: havainnot → master-tietue (append-only)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable
from uuid import uuid4

from urheiluseurapro.merge.contact_persons import (
    append_contact_person_observations,
    apply_contact_person_masters,
    recompute_master_contact_persons,
)
from urheiluseurapro.merge.priorities import resolve_source_priority
from urheiluseurapro.models.club import (
    Club,
    ClubActivity,
    ClubContact,
    ClubExternalIds,
    ClubIdentity,
    ClubLegal,
    ClubLocation,
    ClubQuality,
    ClubSports,
)
from urheiluseurapro.models.enums import FieldSource
from urheiluseurapro.models.merge_state import FieldObservation, MasterFieldValue
from urheiluseurapro.models.observation import ClubObservation
from urheiluseurapro.models.provenance import ClubSourceLink, FieldProvenance
from urheiluseurapro.models.source import Source
from urheiluseurapro.normalization.fields import (
    normalize_club_name,
    normalize_email,
    normalize_municipality,
    normalize_phone,
    normalize_text,
    normalize_website,
)

# Kentät joissa valitaan yksi aktiivinen master-arvo konfliktitilanteessa.
_SINGLE_VALUE_FIELDS: frozenset[str] = frozenset(
    {
        "name",
        "name_official",
        "name_short",
        "municipality",
        "region",
        "postal_code",
        "address_full",
        "website",
        "email",
        "phone",
        "business_id",
    }
)

# Kentät joissa kaikki eri havainnot säilytetään masterissa (union).
_ACCUMULATE_FIELDS: frozenset[str] = frozenset({"sport", "alias"})


@dataclass(frozen=True)
class _ValueGroup:
    normalized_key: str
    display_value: str
    observations: tuple[FieldObservation, ...]


def _normalize_field_value(field_name: str, value: str) -> str:
    normalizers: dict[str, Callable[[str | None], str | None]] = {
        "email": normalize_email,
        "phone": normalize_phone,
        "website": normalize_website,
        "name": normalize_club_name,
        "name_official": normalize_club_name,
        "name_short": normalize_club_name,
        "municipality": normalize_municipality,
        "alias": normalize_club_name,
        "sport": normalize_text,
    }
    normalizer = normalizers.get(field_name, normalize_text)
    normalized = normalizer(value)
    return normalized or value.strip()


def _extract_field_pairs(observation: ClubObservation) -> list[tuple[str, str, str | None]]:
    """Palauttaa (field_name, arvo, raw_arvo) -parit havainnosta."""
    pairs: list[tuple[str, str, str | None]] = []

    def add(field_name: str, normalized: str | None, raw: str | None) -> None:
        value = normalized or raw
        if value:
            pairs.append((field_name, value, raw))

    add("name", observation.name_normalized, observation.name_raw)
    add("name_official", observation.name_official, observation.name_official)
    add("name_short", observation.name_short, observation.name_short)
    add(
        "municipality",
        observation.municipality_normalized,
        observation.municipality_raw,
    )
    add("region", observation.region_normalized, observation.region_raw)
    add("postal_code", observation.postal_code, observation.postal_code)
    add("address_full", observation.address_normalized, observation.address_raw)
    add("website", observation.website_normalized, observation.website_raw)
    add("email", observation.email_normalized, observation.email_raw)
    add("phone", observation.phone_normalized, observation.phone_raw)
    add("business_id", observation.business_id_normalized, observation.business_id_raw)

    for alias in observation.aliases_raw:
        pairs.append(("alias", alias, alias))

    sports = observation.sports_normalized or observation.sports_raw
    for sport in sports:
        pairs.append(("sport", sport, sport))

    return pairs


def _observation_fingerprint(
    observation_id: str,
    field_name: str,
    normalized_key: str,
) -> tuple[str, str, str]:
    return (observation_id, field_name, normalized_key)


def append_observation_fields(
    club: Club,
    observation: ClubObservation,
    *,
    source: Source | None = None,
) -> tuple[Club, list[FieldObservation]]:
    """
    Lisää havainnon kentät club.field_observations -listaan.

    Olemassa olevia havaintoja ei poisteta eikä ylikirjoiteta.
    Palauttaa uuden Club-instanssin – syötettä ei mutatoida.
    """
    existing_keys = {
        _observation_fingerprint(
            obs.observation_id,
            obs.field_name,
            _normalize_field_value(obs.field_name, obs.value),
        )
        for obs in club.field_observations
    }

    preserved: list[FieldObservation] = list(club.field_observations)
    added: list[FieldObservation] = []
    for field_name, value, raw_value in _extract_field_pairs(observation):
        normalized_key = _normalize_field_value(field_name, value)
        fingerprint = _observation_fingerprint(
            observation.observation_id,
            field_name,
            normalized_key,
        )
        if fingerprint in existing_keys:
            continue

        record = FieldObservation(
            id=str(uuid4()),
            field_name=field_name,
            value=value,
            source_id=observation.source_id,
            observation_id=observation.observation_id,
            observed_at=observation.collected_at,
            source_record_key=observation.source_record_key,
            source_url=str(observation.source_url) if observation.source_url else None,
            raw_value=raw_value if raw_value != value else None,
        )
        preserved.append(record)
        existing_keys.add(fingerprint)
        added.append(record)

    if not added:
        return club, added

    return club.model_copy(update={"field_observations": preserved}), added


def _group_observations(
    observations: list[FieldObservation],
) -> list[_ValueGroup]:
    buckets: dict[str, list[FieldObservation]] = defaultdict(list)
    display: dict[str, str] = {}

    for obs in observations:
        key = _normalize_field_value(obs.field_name, obs.value)
        buckets[key].append(obs)
        if key not in display:
            display[key] = obs.value

    return [
        _ValueGroup(
            normalized_key=key,
            display_value=display[key],
            observations=tuple(group),
        )
        for key, group in buckets.items()
    ]


def _group_score(
    group: _ValueGroup,
    sources: dict[str, Source],
) -> tuple[int, float, int]:
    """Vertailuavain: (prioriteetti, tuoreus, yksimielisyys)."""
    priorities = [
        resolve_source_priority(sources.get(obs.source_id), obs.source_id)
        for obs in group.observations
    ]
    max_priority = max(priorities)
    newest = max(obs.observed_at for obs in group.observations).timestamp()
    agreement = len({obs.source_id for obs in group.observations})
    return (max_priority, newest, agreement)


def _compute_confidence(
    winner: _ValueGroup,
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

    confidence = (max_priority / 100.0) * 0.65
    confidence += min(0.25, agreement * 0.08)

    obs_confidences = [
        obs.observation_confidence
        for obs in winner.observations
        if obs.observation_confidence is not None
    ]
    if obs_confidences:
        confidence += sum(obs_confidences) / len(obs_confidences) * 0.1

    if has_conflict:
        confidence *= 0.75

    return round(min(1.0, max(0.05, confidence)), 3)


def select_master_for_field(
    field_name: str,
    observations: list[FieldObservation],
    sources: dict[str, Source],
) -> MasterFieldValue | None:
    """Valitse aktiivinen master-arvo kentälle havaintojen perusteella."""
    if not observations:
        return None

    if field_name in _ACCUMULATE_FIELDS:
        return None

    groups = _group_observations(observations)
    if not groups:
        return None

    ranked = sorted(groups, key=lambda g: _group_score(g, sources), reverse=True)
    winner = ranked[0]
    primary_obs = max(
        winner.observations,
        key=lambda obs: (
            resolve_source_priority(sources.get(obs.source_id), obs.source_id),
            obs.observed_at.timestamp(),
        ),
    )

    conflicting = [g.display_value for g in ranked[1:] if g.normalized_key != winner.normalized_key]
    now = datetime.now(timezone.utc)

    return MasterFieldValue(
        field_name=field_name,
        value=winner.display_value,
        confidence_score=_compute_confidence(
            winner,
            total_groups=len(groups),
            sources=sources,
        ),
        supporting_sources=sorted({obs.source_id for obs in winner.observations}),
        supporting_observation_ids=[obs.id for obs in winner.observations],
        primary_source_id=primary_obs.source_id,
        primary_observation_id=primary_obs.id,
        selected_at=now,
        has_conflict=bool(conflicting),
        conflicting_values=conflicting,
    )


def recompute_master_values(
    club: Club,
    sources: dict[str, Source],
) -> dict[str, MasterFieldValue]:
    """Laske master-arvot kaikista säilytetyistä havainnoista."""
    by_field: dict[str, list[FieldObservation]] = defaultdict(list)
    for obs in club.field_observations:
        by_field[obs.field_name].append(obs)

    masters: dict[str, MasterFieldValue] = {}
    for field_name in _SINGLE_VALUE_FIELDS:
        master = select_master_for_field(field_name, by_field.get(field_name, []), sources)
        if master:
            masters[field_name] = master

    return masters


def _apply_masters_to_club(
    club: Club,
    masters: dict[str, MasterFieldValue],
    sources: dict[str, Source],
) -> Club:
    """Päivitä aggregate-kentät master-valinnoista (havainnot säilyvät)."""
    identity = club.identity.model_copy()
    location = club.location.model_copy()
    contact = club.contact.model_copy()
    legal = club.legal.model_copy()
    sports = club.sports.model_copy()

    if "name" in masters:
        identity.name = masters["name"].value
    if "name_official" in masters:
        identity.name_official = masters["name_official"].value
    if "name_short" in masters:
        identity.name_short = masters["name_short"].value

    alias_obs = [o for o in club.field_observations if o.field_name == "alias"]
    identity.aliases = sorted({o.value for o in alias_obs})

    sport_obs = [o for o in club.field_observations if o.field_name == "sport"]
    sports.sports = sorted({o.value for o in sport_obs}, key=str.lower)
    sports.is_multi_sport = len(sports.sports) > 1

    if "municipality" in masters:
        location.municipality = masters["municipality"].value
    if "region" in masters:
        location.region = masters["region"].value
    if "postal_code" in masters:
        location.postal_code = masters["postal_code"].value
    if "address_full" in masters:
        location.address_full = masters["address_full"].value
    if "website" in masters:
        contact.website = masters["website"].value
    if "email" in masters:
        contact.email = masters["email"].value
    if "phone" in masters:
        contact.phone = masters["phone"].value
    if "business_id" in masters:
        legal.business_id = masters["business_id"].value

    # Toissijaiset yhteystiedot: seuraavaksi parhaat konfliktiarvot
    for field_name, secondary_attr in (
        ("email", "email_secondary"),
        ("phone", "phone_secondary"),
    ):
        field_obs = [o for o in club.field_observations if o.field_name == field_name]
        groups = _group_observations(field_obs)
        if len(groups) < 2:
            continue
        ranked = sorted(groups, key=lambda g: _group_score(g, sources), reverse=True)
        secondary_value = ranked[1].display_value
        setattr(contact, secondary_attr, secondary_value)

    return club.model_copy(
        update={
            "identity": identity,
            "location": location,
            "contact": contact,
            "legal": legal,
            "sports": sports,
            "field_observations": list(club.field_observations),
            "master_values": masters,
        }
    )


def _update_provenance(
    club: Club,
    masters: dict[str, MasterFieldValue],
) -> list[FieldProvenance]:
    """Lisää provenienssi master-valinnoista (historia säilyy field_observations:ssa)."""
    provenance = list(club.field_provenance)
    existing = {(p.field_name, p.observation_id) for p in provenance}

    for field_name, master in masters.items():
        key = (field_name, master.primary_observation_id)
        if key in existing:
            continue
        provenance.append(
            FieldProvenance(
                field_name=field_name,
                source_id=master.primary_source_id,
                observation_id=master.primary_observation_id,
                value_at_merge=master.value,
                merge_method=FieldSource.CONFLICT if master.has_conflict else FieldSource.MERGED,
            )
        )
    return provenance


def _upsert_source_link(
    club: Club,
    observation: ClubObservation,
) -> list[ClubSourceLink]:
    links = list(club.source_links)
    existing = next(
        (link for link in links if link.source_id == observation.source_id),
        None,
    )
    if existing:
        updated = existing.model_copy(
            update={
                "observation_id": observation.observation_id,
                "external_id": observation.source_record_key,
                "source_url": str(observation.source_url) if observation.source_url else None,
                "last_seen_at": observation.collected_at,
            }
        )
        links = [updated if link.source_id == observation.source_id else link for link in links]
    else:
        links.append(
            ClubSourceLink(
                master_club_id=club.id,
                source_id=observation.source_id,
                observation_id=observation.observation_id,
                external_id=observation.source_record_key,
                source_url=str(observation.source_url) if observation.source_url else None,
                last_seen_at=observation.collected_at,
                is_primary_source=len(links) == 0,
            )
        )
    return links


def observation_to_club(
    observation: ClubObservation,
    *,
    club_id: str | None = None,
    canonical_key: str | None = None,
    source: Source | None = None,
    sources: dict[str, Source] | None = None,
) -> Club:
    """Luo uusi master-tietue yhdestä havainnosta (ensimmäinen lähde)."""
    sources = sources or {}
    if source:
        sources = {**sources, source.source_id: source}

    now = datetime.now(timezone.utc)
    new_id = club_id or str(uuid4())

    club = Club(
        id=new_id,
        canonical_key=canonical_key,
        identity=ClubIdentity(name=observation.name_raw.strip()),
        quality=ClubQuality(source_count=1),
        source_links=[],
        created_at=now,
        updated_at=now,
        last_merged_at=now,
        last_seen_at=observation.collected_at,
    )

    club, _ = append_observation_fields(club, observation, source=source)
    club, _ = append_contact_person_observations(club, observation)
    masters = recompute_master_values(club, sources)
    master_contact_persons = recompute_master_contact_persons(club, sources)
    club = _apply_masters_to_club(club, masters, sources)
    club = apply_contact_person_masters(club, master_contact_persons, sources)

    if observation.name_normalized:
        identity = club.identity.model_copy(update={"name_normalized": observation.name_normalized})
        club = club.model_copy(update={"identity": identity})

    club = club.model_copy(
        update={
            "external_ids": ClubExternalIds(
                suomisport_id=observation.suomisport_id,
                federation_ids=(
                    {observation.source_id: observation.federation_id}
                    if observation.federation_id
                    else {}
                ),
            ),
            "activity": ClubActivity(
                status=observation.status,
                founded_year=observation.founded_year,
                member_count=observation.member_count,
            ),
            "location": club.location.model_copy(
                update={"municipality_code": observation.municipality_code}
            ),
            "source_links": _upsert_source_link(club, observation),
            "field_provenance": _update_provenance(club, masters),
            "field_observations": list(club.field_observations),
            "contact_person_observations": list(club.contact_person_observations),
            "master_contact_persons": dict(club.master_contact_persons),
        }
    )

    club.quality.completeness_score = _calculate_completeness(club)
    club.quality.confidence_score = _calculate_overall_confidence(club)
    club.quality.needs_review = (
        club.quality.needs_review or any(m.has_conflict for m in masters.values())
    )
    return club


def merge_observation_into_club(
    club: Club,
    observation: ClubObservation,
    source: Source | None = None,
    sources: dict[str, Source] | None = None,
) -> Club:
    """
    Yhdistä uusi havainto master-tietueeseen.

    Havainnot lisätään aina – mitään ei ylikirjoiteta eikä poisteta.
    Master-arvot lasketaan uudelleen kaikkien havaintojen perusteella.
    """
    sources = sources or {}
    if source:
        sources = {**sources, source.source_id: source}

    observation_count_before = len(club.field_observations)
    contact_person_count_before = len(club.contact_person_observations)

    club, added = append_observation_fields(club, observation, source=source)
    club, cp_added = append_contact_person_observations(club, observation)
    masters = recompute_master_values(club, sources)
    master_contact_persons = recompute_master_contact_persons(club, sources)
    merged = _apply_masters_to_club(club, masters, sources)
    merged = apply_contact_person_masters(merged, master_contact_persons, sources)

    identity = merged.identity.model_copy()
    if observation.name_normalized:
        identity.name_normalized = observation.name_normalized

    external_ids = merged.external_ids.model_copy()
    if observation.suomisport_id and not external_ids.suomisport_id:
        external_ids.suomisport_id = observation.suomisport_id
    if observation.federation_id:
        external_ids.federation_ids[observation.source_id] = observation.federation_id

    location = merged.location.model_copy()
    if observation.municipality_code and not location.municipality_code:
        location.municipality_code = observation.municipality_code

    now = datetime.now(timezone.utc)
    source_links = _upsert_source_link(merged, observation)
    quality = merged.quality.model_copy()
    quality.source_count = len(source_links)
    quality.merge_version += 1
    quality.needs_review = (
        quality.needs_review
        or any(m.has_conflict for m in masters.values())
        or any(m.has_conflict for m in master_contact_persons.values())
    )

    result = merged.model_copy(
        update={
            "identity": identity,
            "location": location,
            "external_ids": external_ids,
            "source_links": source_links,
            "field_provenance": _update_provenance(merged, masters),
            "field_observations": list(merged.field_observations),
            "contact_person_observations": list(merged.contact_person_observations),
            "master_contact_persons": dict(merged.master_contact_persons),
            "contact_person": merged.contact_person,
            "quality": quality,
            "updated_at": now,
            "last_merged_at": now,
            "last_seen_at": max(
                filter(None, [club.last_seen_at, observation.collected_at]),
                default=observation.collected_at,
            ),
        }
    )
    result.quality.confidence_score = _calculate_overall_confidence(result)
    result.quality.completeness_score = _calculate_completeness(result)

    assert len(result.field_observations) >= observation_count_before, (
        "Havaintoja ei saa poistaa merge-vaiheessa"
    )
    if added:
        assert len(result.field_observations) == observation_count_before + len(added), (
            "Uudet havainnot pitää säilyttää kokonaisuudessaan"
        )
    assert len(result.contact_person_observations) >= contact_person_count_before, (
        "Yhteyshenkilöhavaintoja ei saa poistaa merge-vaiheessa"
    )
    if cp_added:
        assert (
            len(result.contact_person_observations)
            == contact_person_count_before + len(cp_added)
        ), "Uudet yhteyshenkilöhavainnot pitää säilyttää kokonaisuudessaan"
    return result


def get_field_observations(
    club: Club,
    field_name: str | None = None,
) -> list[FieldObservation]:
    """Hae kaikki tai yhden kentän havainnot."""
    if field_name is None:
        return list(club.field_observations)
    return [obs for obs in club.field_observations if obs.field_name == field_name]


def _calculate_completeness(club: Club) -> float:
    checks = [
        bool(club.identity.name),
        bool(club.sports.sports),
        bool(club.location.municipality),
        bool(club.location.address_full),
        bool(club.contact.website),
        bool(club.contact.email),
        bool(club.contact.phone),
        bool(club.legal.business_id),
        bool(club.external_ids.suomisport_id),
        club.quality.source_count >= 2,
    ]
    return round(sum(checks) / len(checks), 2)


def _calculate_overall_confidence(club: Club) -> float:
    if not club.master_values:
        return 0.0
    return round(
        sum(m.confidence_score for m in club.master_values.values()) / len(club.master_values),
        3,
    )
