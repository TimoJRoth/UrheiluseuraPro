"""
Ingestion-orchestraatio: havainnot → master-tietokanta.

Ei vaadi tietokantaa – toimii listoilla kehitysvaiheessa.
"""

from __future__ import annotations

from urheiluseurapro.deduplication.matcher import build_canonical_key, match_observation_to_club
from urheiluseurapro.merge.engine import merge_observation_into_club, observation_to_club
from urheiluseurapro.models.club import Club
from urheiluseurapro.models.enums import MatchStatus
from urheiluseurapro.models.observation import ClubObservation
from urheiluseurapro.models.source import Source
from urheiluseurapro.normalization.fields import normalize_observation_fields


def apply_normalization(observation: ClubObservation) -> ClubObservation:
    """Täytä normalisoidut kentät havainnolle."""
    normalized = normalize_observation_fields(
        name_raw=observation.name_raw,
        municipality_raw=observation.municipality_raw,
        business_id_raw=observation.business_id_raw,
        email_raw=observation.email_raw,
        phone_raw=observation.phone_raw,
        website_raw=observation.website_raw,
        sports_raw=observation.sports_raw,
        region_raw=observation.region_raw,
        address_raw=observation.address_raw,
    )
    return observation.model_copy(update=normalized)


def ingest_observations(
    observations: list[ClubObservation],
    existing_clubs: list[Club],
    sources: dict[str, Source] | None = None,
) -> tuple[list[Club], list[ClubObservation]]:
    """
    Prosessoi havainnot master-tietueiksi.

    Palauttaa:
    - päivitetyn master-listan
    - havainnot match_statuksineen
    """
    sources = sources or {}
    clubs: list[Club] = list(existing_clubs)
    processed: list[ClubObservation] = []

    for raw_observation in observations:
        observation = apply_normalization(raw_observation)
        match = match_observation_to_club(observation, clubs)

        if match.master_club_id:
            idx = next(i for i, c in enumerate(clubs) if c.id == match.master_club_id)
            source = sources.get(observation.source_id)
            clubs[idx] = merge_observation_into_club(
                clubs[idx], observation, source, sources=sources
            )
            processed.append(
                observation.model_copy(
                    update={
                        "match_status": MatchStatus.MATCHED,
                        "match_confidence": match.confidence,
                        "matched_master_club_id": match.master_club_id,
                        "match_score": match.score,
                        "match_reason": match.reason,
                    }
                )
            )
            continue

        canonical_key = build_canonical_key(observation)
        source = sources.get(observation.source_id)
        new_club = observation_to_club(
            observation,
            canonical_key=canonical_key,
            source=source,
            sources=sources,
        )
        clubs.append(new_club)
        processed.append(
            observation.model_copy(
                update={
                    "match_status": MatchStatus.UNMATCHED,
                    "match_confidence": match.confidence,
                    "matched_master_club_id": new_club.id,
                    "match_score": match.score,
                    "match_reason": "new_master_record",
                }
            )
        )

    return clubs, processed
