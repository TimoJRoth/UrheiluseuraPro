"""Entity resolution -päätöksenteko (ei vielä mergeä)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from urheiluseurapro.resolution.keys import (
    club_match_keys,
    normalize_org_name_for_matching,
)


@dataclass(frozen=True)
class MatchDecision:
    """Arvio siitä, kuvaavatko kaksi tietuetta todennäköisesti samaa seuraa."""

    confidence: float
    reasons: list[str]


def _field(record: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in record and record[name] not in (None, ""):
            return record[name]
    return None


def _names_match(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_name = normalize_org_name_for_matching(
        _field(left, "name", "name_raw", "name_normalized")
    )
    right_name = normalize_org_name_for_matching(
        _field(right, "name", "name_raw", "name_normalized")
    )
    return bool(left_name and right_name and left_name == right_name)


class MatchDecisionEngine:
    """
    Arvioi kahden seuratietueen samankaltaisuuden.

    Ei yhdistä dataa – palauttaa vain luottamusarvion ja perustelut.
    """

    def decide(self, left: dict[str, Any], right: dict[str, Any]) -> MatchDecision:
        return decide_match(left, right)


def decide_match(left: dict[str, Any], right: dict[str, Any]) -> MatchDecision:
    """Arvioi matchaus club_match_keys-leikkausjoukon ja nimen perusteella."""
    common_keys = set(club_match_keys(left)) & set(club_match_keys(right))

    reasons: list[str] = []
    confidence = 0.0

    if any(key.startswith("email:") for key in common_keys):
        reasons.append("same_email")
        confidence = max(confidence, 1.00)

    if any(key.startswith("website:") for key in common_keys):
        reasons.append("same_website")
        confidence = max(confidence, 0.95)

    if any(key.startswith("phone:") for key in common_keys):
        reasons.append("same_phone")
        confidence = max(confidence, 0.90)

    if any(key.startswith("name_municipality:") for key in common_keys):
        reasons.extend(["same_name", "same_municipality"])
        confidence = max(confidence, 0.85)
    elif _names_match(left, right):
        reasons.append("same_name")
        confidence = max(confidence, 0.70)

    return MatchDecision(confidence=confidence, reasons=_unique_reasons(reasons))


def _unique_reasons(reasons: list[str]) -> list[str]:
    return list(dict.fromkeys(reasons))
