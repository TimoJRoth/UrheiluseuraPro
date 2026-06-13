"""Kerääjärekisteri."""

from urheiluseurapro.collectors.base import BaseCollector


class CollectorRegistry:
    """Rekisteröi ja hakee käytettävissä olevat kerääjät."""

    def __init__(self) -> None:
        self._collectors: dict[str, BaseCollector] = {}

    def register(self, collector: BaseCollector) -> None:
        self._collectors[collector.source_id] = collector

    def get(self, source_id: str) -> BaseCollector:
        if source_id not in self._collectors:
            available = ", ".join(sorted(self._collectors)) or "(ei rekisteröityjä)"
            raise KeyError(f"Tuntematon lähde '{source_id}'. Saatavilla: {available}")
        return self._collectors[source_id]

    def list_sources(self) -> list[tuple[str, str]]:
        return [(c.source_id, c.display_name) for c in self._collectors.values()]

    def find_for_url(self, url: str) -> BaseCollector | None:
        for collector in self._collectors.values():
            if collector.supports_url(url):
                return collector
        return None


def default_registry() -> CollectorRegistry:
    """Palauttaa oletusrekisterin. Kerääjät lisätään tähän vaiheittain."""
    return CollectorRegistry()
