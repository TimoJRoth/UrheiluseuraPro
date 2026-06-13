"""Kerääjärekisteri."""

from __future__ import annotations

from typing import Type

from urheiluseurapro.collectors.base import BaseCollector
from urheiluseurapro.collectors.examples.json_feed import JsonFeedCollector
from urheiluseurapro.collectors.mock import MockCollector
from urheiluseurapro.config import Settings, get_settings
from urheiluseurapro.sources.registry import SourceConfigRegistry, default_source_registry

# Kartta source_id → collector-luokka. Uusi lähde = uusi rivi + SourceConfig config/sources.json:ssa.
_COLLECTOR_TYPES: dict[str, Type[BaseCollector]] = {
    "mock": MockCollector,
    "example-json-feed": JsonFeedCollector,
}


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
        return sorted(
            [(c.source_id, c.display_name) for c in self._collectors.values()],
            key=lambda item: item[0],
        )

    def find_for_url(self, url: str) -> BaseCollector | None:
        for collector in self._collectors.values():
            if collector.supports_url(url):
                return collector
        return None


def _build_collector(
    source_id: str,
    collector_cls: Type[BaseCollector],
    source_registry: SourceConfigRegistry,
    settings: Settings,
) -> BaseCollector | None:
    config = source_registry.get(source_id)
    if config is None or not config.enabled:
        return None
    return collector_cls(
        source_config=config,
        source_registry=source_registry,
        settings=settings,
    )


def default_registry(
    settings: Settings | None = None,
    source_registry: SourceConfigRegistry | None = None,
) -> CollectorRegistry:
    """Palauttaa oletusrekisterin enabled-lähteille, joille on collector-toteutus."""
    resolved_settings = settings or get_settings()
    resolved_sources = source_registry or default_source_registry(resolved_settings)
    registry = CollectorRegistry()

    for source_id, collector_cls in _COLLECTOR_TYPES.items():
        collector = _build_collector(source_id, collector_cls, resolved_sources, resolved_settings)
        if collector is not None:
            registry.register(collector)

    return registry
