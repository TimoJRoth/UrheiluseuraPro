"""Deduplikointi."""

from urheiluseurapro.deduplication.matcher import MatchResult, build_canonical_key, match_observation_to_club

__all__ = ["MatchResult", "build_canonical_key", "match_observation_to_club"]
