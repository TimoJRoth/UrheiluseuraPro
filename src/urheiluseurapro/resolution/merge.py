"""Entity resolution -tietueiden yhdistäminen canonical club -rakenteiksi."""

from __future__ import annotations

from typing import Any

from urheiluseurapro.resolution.canonical import CanonicalClub, CanonicalClubBuilder
from urheiluseurapro.resolution.decision import MatchDecisionEngine

_MERGE_THRESHOLD = 0.90


class MergeEngine:
    """
    Yhdistää selvästi samaa seuraa kuvaavat tietueet canonical club -rakenteiksi.

    Käyttää MatchDecisionEngineä päätökseen ja CanonicalClubBuilderia rakentamiseen.
    """

    def __init__(
        self,
        *,
        merge_threshold: float = _MERGE_THRESHOLD,
        decision_engine: MatchDecisionEngine | None = None,
        canonical_builder: CanonicalClubBuilder | None = None,
    ) -> None:
        self._merge_threshold = merge_threshold
        self._decision_engine = decision_engine or MatchDecisionEngine()
        self._canonical_builder = canonical_builder or CanonicalClubBuilder()

    def merge(self, records: list[dict[str, Any]]) -> list[CanonicalClub]:
        """Yhdistä tietueet canonical club -rakenteiksi."""
        return merge_club_records(
            records,
            merge_threshold=self._merge_threshold,
            decision_engine=self._decision_engine,
            canonical_builder=self._canonical_builder,
        )


def merge_club_records(
    records: list[dict[str, Any]],
    *,
    merge_threshold: float = _MERGE_THRESHOLD,
    decision_engine: MatchDecisionEngine | None = None,
    canonical_builder: CanonicalClubBuilder | None = None,
) -> list[CanonicalClub]:
    """
    Yhdistä tietueet canonical club -rakenteiksi selvien matchien perusteella.

    Kaksi tietuetta yhdistetään, jos MatchDecisionEngine antaa confidence >= 0.90.
    """
    if not records:
        return []

    engine = decision_engine or MatchDecisionEngine()
    builder = canonical_builder or CanonicalClubBuilder()
    clusters = _cluster_records(records, engine, merge_threshold)
    return [builder.build_many(cluster) for cluster in clusters]


def _cluster_records(
    records: list[dict[str, Any]],
    engine: MatchDecisionEngine,
    threshold: float,
) -> list[list[dict[str, Any]]]:
    parent = list(range(len(records)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        root_left = find(left)
        root_right = find(right)
        if root_left != root_right:
            parent[root_right] = root_left

    for left in range(len(records)):
        for right in range(left + 1, len(records)):
            decision = engine.decide(records[left], records[right])
            if decision.confidence >= threshold:
                union(left, right)

    groups: dict[int, list[dict[str, Any]]] = {}
    for index, record in enumerate(records):
        root = find(index)
        groups.setdefault(root, []).append(record)

    return list(groups.values())
