"""Deduplikointi: havainnot → master-seurat."""

from __future__ import annotations

from dataclasses import dataclass

from urheiluseurapro.models.club import Club
from urheiluseurapro.models.enums import MatchConfidence
from urheiluseurapro.models.observation import ClubObservation


@dataclass(frozen=True)
class MatchResult:
    """Deduplikointitulos yhdelle havainnolle."""

    master_club_id: str | None
    confidence: MatchConfidence
    score: float
    reason: str


def _sports_overlap(a: list[str], b: list[str]) -> bool:
    if not a or not b:
        return True
    return bool(set(a) & set(b))


def match_observation_to_club(
    observation: ClubObservation,
    candidates: list[Club],
) -> MatchResult:
    """
    Etsi paras master-osuma havainnolle.

    Sääntöjärjestys (korkeimmasta luotettavuudesta alhaimpaan):
    1. Y-tunnus täsmää
    2. Suomisport-ID täsmää
    3. Normalisoitu nimi + kunta + laji
    4. Normalisoitu nimi + kunta
    5. Fuzzy nimi + kunta (tulevaisuudessa)
    """
    if observation.business_id_normalized:
        for club in candidates:
            if club.legal.business_id == observation.business_id_normalized:
                return MatchResult(
                    master_club_id=club.id,
                    confidence=MatchConfidence.EXACT,
                    score=1.0,
                    reason="business_id_exact",
                )

    if observation.suomisport_id:
        for club in candidates:
            if club.external_ids.suomisport_id == observation.suomisport_id:
                return MatchResult(
                    master_club_id=club.id,
                    confidence=MatchConfidence.EXACT,
                    score=1.0,
                    reason="suomisport_id_exact",
                )

    if observation.name_normalized and observation.municipality_normalized:
        for club in candidates:
            club_name = club.identity.name_normalized
            club_muni = club.location.municipality
            if not club_name or not club_muni:
                continue
            if (
                club_name == observation.name_normalized
                and club_muni.lower() == observation.municipality_normalized.lower()
                and _sports_overlap(
                    observation.sports_normalized,
                    [s.lower() for s in club.sports.sports],
                )
            ):
                return MatchResult(
                    master_club_id=club.id,
                    confidence=MatchConfidence.HIGH,
                    score=0.9,
                    reason="name_municipality_sport",
                )

        for club in candidates:
            club_name = club.identity.name_normalized
            club_muni = club.location.municipality
            if not club_name or not club_muni:
                continue
            if (
                club_name == observation.name_normalized
                and club_muni.lower() == observation.municipality_normalized.lower()
            ):
                return MatchResult(
                    master_club_id=club.id,
                    confidence=MatchConfidence.MEDIUM,
                    score=0.75,
                    reason="name_municipality",
                )

    return MatchResult(
        master_club_id=None,
        confidence=MatchConfidence.NO_MATCH,
        score=0.0,
        reason="no_match",
    )


def build_canonical_key(observation: ClubObservation) -> str | None:
    """Deterministinen avain uuden master-tietueen luontiin."""
    if observation.business_id_normalized:
        return f"yt:{observation.business_id_normalized}"
    if observation.suomisport_id:
        return f"ss:{observation.suomisport_id}"
    if observation.name_normalized and observation.municipality_normalized:
        sport = observation.primary_sport or (observation.sports_normalized[0] if observation.sports_normalized else "")
        return f"name:{observation.name_normalized}|{observation.municipality_normalized.lower()}|{sport}"
    if observation.name_normalized:
        return f"name:{observation.name_normalized}"
    return None
