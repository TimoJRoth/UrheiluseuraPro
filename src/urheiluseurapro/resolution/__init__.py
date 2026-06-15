"""Entity resolution -moduuli."""

from urheiluseurapro.resolution.canonical import (
    CanonicalClub,
    CanonicalClubBuilder,
    build_canonical_club,
)
from urheiluseurapro.resolution.decision import (
    MatchDecision,
    MatchDecisionEngine,
    decide_match,
)
from urheiluseurapro.resolution.keys import club_match_keys, normalize_org_name_for_matching
from urheiluseurapro.resolution.merge import MergeEngine, merge_club_records

__all__ = [
    "CanonicalClub",
    "CanonicalClubBuilder",
    "MatchDecision",
    "MatchDecisionEngine",
    "MergeEngine",
    "build_canonical_club",
    "club_match_keys",
    "decide_match",
    "merge_club_records",
    "normalize_org_name_for_matching",
]
