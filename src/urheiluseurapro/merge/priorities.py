"""Lähteen luotettavuusprioriteetit merge-vaiheessa."""

from __future__ import annotations

from urheiluseurapro.models.enums import SourceCategory
from urheiluseurapro.models.source import Source

# Korkeampi = luotettavampi (0–100).
# Järjestys: seuran sivu > Suomisport > OK > lajiliitto > kunta > PRH/YTJ > muu
SOURCE_TRUST_TIER: dict[str, int] = {
    "club-website": 100,
    "seuran-verkkosivu": 100,
    "suomisport": 90,
    "olympiakomitea": 85,
    "olympic-committee": 85,
    "laji-fi": 75,
    "prh": 65,
    "ytj": 65,
}

_CATEGORY_TIER: dict[SourceCategory, int] = {
    SourceCategory.FEDERATION: 80,
    SourceCategory.REGIONAL: 75,
    SourceCategory.MUNICIPALITY: 70,
    SourceCategory.NATIONAL: 85,
    SourceCategory.REGISTRY: 65,
    SourceCategory.GRANT: 55,
    SourceCategory.FACILITY: 50,
    SourceCategory.BOOKING: 45,
    SourceCategory.OTHER: 40,
}

_FEDERATION_SOURCE_IDS: frozenset[str] = frozenset(
    {
        "palloliitto",
        "finhockey",
        "finland-basketball",
        "suomen-käsipalloliitto",
        "salibandy",
        "suomen-ampumaurheiluliitto",
    }
)

_MUNICIPALITY_SOURCE_PREFIXES: tuple[str, ...] = ("kunta-", "kaupunki-")


def resolve_source_priority(source: Source | None, source_id: str) -> int:
    """
    Palauttaa lähteen merge-prioriteetin (0–100).

    Eksplisiittinen Source.merge_priority voittaa oletustason vain jos se on
    korkeampi kuin tunnistettu luottamustaso (manuaalinen ylikirjoitus).
    """
    tier = _tier_from_source_id_and_category(source_id, source)
    if source is not None and source.merge_priority > tier:
        return source.merge_priority
    return tier


def _tier_from_source_id_and_category(source_id: str, source: Source | None) -> int:
    key = source_id.lower().strip()
    if key in SOURCE_TRUST_TIER:
        return SOURCE_TRUST_TIER[key]

    if source is not None:
        if source.category == SourceCategory.FEDERATION:
            return _CATEGORY_TIER[SourceCategory.FEDERATION]
        if source.category == SourceCategory.MUNICIPALITY:
            return _CATEGORY_TIER[SourceCategory.MUNICIPALITY]
        if source.category == SourceCategory.REGISTRY:
            return _CATEGORY_TIER[SourceCategory.REGISTRY]
        if source.category == SourceCategory.NATIONAL:
            return _CATEGORY_TIER[SourceCategory.NATIONAL]
        return _CATEGORY_TIER.get(source.category, 40)

    if key in _FEDERATION_SOURCE_IDS:
        return _CATEGORY_TIER[SourceCategory.FEDERATION]
    if any(key.startswith(prefix) for prefix in _MUNICIPALITY_SOURCE_PREFIXES):
        return _CATEGORY_TIER[SourceCategory.MUNICIPALITY]
    if key in ("prh", "ytj", "kaupparekisteri"):
        return _CATEGORY_TIER[SourceCategory.REGISTRY]

    return 40
