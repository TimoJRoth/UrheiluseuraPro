"""Lähteiden yhdistäminen: havainnot → master-tietue."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TypeVar
from uuid import uuid4

from urheiluseurapro.models.club import (
    Club,
    ClubActivity,
    ClubContact,
    ClubContactPerson,
    ClubExternalIds,
    ClubIdentity,
    ClubLegal,
    ClubLocation,
    ClubQuality,
    ClubSports,
)
from urheiluseurapro.models.enums import FieldSource
from urheiluseurapro.models.observation import ClubObservation
from urheiluseurapro.models.provenance import ClubSourceLink, FieldProvenance
from urheiluseurapro.models.source import Source

# Oletusprioriteetit (0–100), jos Source.merge_priority puuttuu
_DEFAULT_SOURCE_PRIORITY: dict[str, int] = {
    "prh": 95,
    "ytj": 95,
    "suomisport": 90,
    "laji-fi": 85,
    "palloliitto": 80,
    "finhockey": 80,
}


def _source_priority(source: Source | None, source_id: str) -> int:
    if source:
        return source.merge_priority
    return _DEFAULT_SOURCE_PRIORITY.get(source_id, 50)


T = TypeVar("T")


def _pick_best(
    current: T | None,
    candidate: T | None,
    current_priority: int,
    candidate_priority: int,
) -> tuple[T | None, int, bool]:
    """Palauttaa (arvo, prioriteetti, muuttui_ko)."""
    if candidate is None:
        return current, current_priority, False
    if current is None:
        return candidate, candidate_priority, True
    if candidate_priority > current_priority:
        return candidate, candidate_priority, True
    return current, current_priority, False


def observation_to_club(
    observation: ClubObservation,
    *,
    club_id: str | None = None,
    canonical_key: str | None = None,
) -> Club:
    """Luo uusi master-tietue yhdestä havainnosta (ensimmäinen lähde)."""
    now = datetime.now(timezone.utc)
    new_id = club_id or str(uuid4())
    sports = observation.sports_normalized or observation.sports_raw
    primary = observation.primary_sport or (sports[0] if sports else None)

    return Club(
        id=new_id,
        canonical_key=canonical_key,
        identity=ClubIdentity(
            name=observation.name_raw.strip(),
            name_official=observation.name_official,
            name_short=observation.name_short,
            name_normalized=observation.name_normalized,
            aliases=list(observation.aliases_raw),
        ),
        sports=ClubSports(
            sports=sports,
            primary_sport=primary,
            is_multi_sport=len(sports) > 1,
        ),
        legal=ClubLegal(
            business_id=observation.business_id_normalized,
            legal_form=observation.legal_form,
            club_type=observation.club_type,
        ),
        location=ClubLocation(
            municipality=observation.municipality_normalized or observation.municipality_raw,
            municipality_code=observation.municipality_code,
            region=observation.region_normalized or observation.region_raw,
            postal_code=observation.postal_code,
            address_street=observation.address_normalized or observation.address_raw,
            address_full=observation.address_normalized or observation.address_raw,
        ),
        contact=ClubContact(
            website=observation.website_normalized or observation.website_raw,
            email=observation.email_normalized or observation.email_raw,
            phone=observation.phone_normalized or observation.phone_raw,
        ),
        contact_person=ClubContactPerson(
            name=observation.contact_person_name,
            role=observation.contact_person_role,
            email=observation.contact_person_email,
            phone=observation.contact_person_phone,
        ),
        external_ids=ClubExternalIds(
            suomisport_id=observation.suomisport_id,
            federation_ids=(
                {observation.source_id: observation.federation_id}
                if observation.federation_id
                else {}
            ),
        ),
        activity=ClubActivity(
            status=observation.status,
            founded_year=observation.founded_year,
            member_count=observation.member_count,
        ),
        quality=ClubQuality(source_count=1),
        source_links=[
            ClubSourceLink(
                master_club_id=new_id,
                source_id=observation.source_id,
                observation_id=observation.observation_id,
                external_id=observation.source_record_key,
                source_url=str(observation.source_url) if observation.source_url else None,
                is_primary_source=True,
            )
        ],
        created_at=now,
        updated_at=now,
        last_merged_at=now,
        last_seen_at=observation.collected_at,
    )


def merge_observation_into_club(
    club: Club,
    observation: ClubObservation,
    source: Source | None = None,
) -> Club:
    """
    Yhdistä uusi havainto olemassa olevaan master-tietueeseen.

    Kenttävalinta perustuu lähteen merge-prioriteettiin.
    Konfliktit merkitään provenienssiin.
    """
    priority = _source_priority(source, observation.source_id)
    now = datetime.now(timezone.utc)
    provenance: list[FieldProvenance] = list(club.field_provenance)

    def merge_field(
        field_name: str,
        current: str | None,
        candidate: str | None,
    ) -> str | None:
        best, _, changed = _pick_best(current, candidate, 50, priority)
        if changed and candidate is not None:
            provenance.append(
                FieldProvenance(
                    field_name=field_name,
                    source_id=observation.source_id,
                    observation_id=observation.observation_id,
                    value_at_merge=candidate,
                    merge_method=FieldSource.MERGED,
                )
            )
        return best

    identity = club.identity.model_copy()
    identity.name = merge_field("name", identity.name, observation.name_raw) or identity.name
    identity.name_official = merge_field(
        "name_official", identity.name_official, observation.name_official
    )
    identity.name_short = merge_field("name_short", identity.name_short, observation.name_short)
    if observation.name_normalized:
        identity.name_normalized = observation.name_normalized
    for alias in observation.aliases_raw:
        if alias not in identity.aliases:
            identity.aliases.append(alias)

    location = club.location.model_copy()
    location.municipality = merge_field(
        "municipality",
        location.municipality,
        observation.municipality_normalized or observation.municipality_raw,
    )
    location.region = merge_field(
        "region", location.region, observation.region_normalized or observation.region_raw
    )
    location.postal_code = merge_field("postal_code", location.postal_code, observation.postal_code)
    location.address_full = merge_field(
        "address_full",
        location.address_full,
        observation.address_normalized or observation.address_raw,
    )

    contact = club.contact.model_copy()
    contact.website = merge_field(
        "website", str(contact.website) if contact.website else None,
        observation.website_normalized or observation.website_raw,
    )
    contact.email = merge_field(
        "email", contact.email, observation.email_normalized or observation.email_raw
    )
    contact.phone = merge_field(
        "phone", contact.phone, observation.phone_normalized or observation.phone_raw
    )

    legal = club.legal.model_copy()
    legal.business_id = merge_field(
        "business_id", legal.business_id, observation.business_id_normalized
    )

    external_ids = club.external_ids.model_copy()
    if observation.suomisport_id and not external_ids.suomisport_id:
        external_ids.suomisport_id = observation.suomisport_id
    if observation.federation_id:
        external_ids.federation_ids[observation.source_id] = observation.federation_id

    sports = club.sports.model_copy()
    for sport in observation.sports_normalized or observation.sports_raw:
        if sport not in sports.sports:
            sports.sports.append(sport)
    sports.is_multi_sport = len(sports.sports) > 1
    if not sports.primary_sport and observation.primary_sport:
        sports.primary_sport = observation.primary_sport

    source_links = list(club.source_links)
    source_links.append(
        ClubSourceLink(
            master_club_id=club.id,
            source_id=observation.source_id,
            observation_id=observation.observation_id,
            external_id=observation.source_record_key,
            source_url=str(observation.source_url) if observation.source_url else None,
            last_seen_at=observation.collected_at,
        )
    )

    quality = club.quality.model_copy()
    quality.source_count = len(source_links)
    quality.merge_version += 1

    merged = club.model_copy(
        update={
            "identity": identity,
            "location": location,
            "contact": contact,
            "legal": legal,
            "external_ids": external_ids,
            "sports": sports,
            "source_links": source_links,
            "field_provenance": provenance,
            "quality": quality,
            "updated_at": now,
            "last_merged_at": now,
            "last_seen_at": max(filter(None, [club.last_seen_at, observation.collected_at])),
        }
    )
    merged.quality.completeness_score = _calculate_completeness(merged)
    return merged


def _calculate_completeness(club: Club) -> float:
    """Karkea täydellisyysprosentti (0–1)."""
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
