"""Collector- ja ingestor-testit (geneerinen arkkitehtuuri)."""

from __future__ import annotations

import asyncio

from urheiluseurapro.collectors.mock import MockCollector
from urheiluseurapro.collectors.registry import default_registry
from urheiluseurapro.collectors.runner import run_collector
from urheiluseurapro.merge.contact_persons import get_contact_person_observations
from urheiluseurapro.models.enums import SourceCategory
from urheiluseurapro.models.source import Source
from urheiluseurapro.pipeline.ingest import ingest_observations


def test_mock_collector_returns_three_clubs() -> None:
    results = asyncio.run(MockCollector().collect())

    assert len(results) == 3
    names = {result.observation.name_raw for result in results}
    assert "Esimerkki Urheiluseura Alpha" in names
    assert "Esimerkki Urheiluseura Beta" in names
    assert "Esimerkki Urheiluseura Gamma" in names


def test_collector_result_has_provenance_metadata() -> None:
    result = asyncio.run(MockCollector().collect())[0]

    assert result.source == "mock"
    assert result.source_url is not None
    assert 0.0 < result.confidence <= 1.0
    assert result.fetched_at is not None
    assert result.first_seen_at is not None
    assert result.last_seen_at is not None
    assert result.observation.source_id == "mock"
    assert result.observation.observation_confidence == result.confidence


def test_collector_result_includes_club_fields() -> None:
    results = asyncio.run(MockCollector().collect())
    alpha = next(r for r in results if r.observation.name_raw == "Esimerkki Urheiluseura Alpha")
    obs = alpha.observation

    assert obs.municipality_raw == "Tampere"
    assert obs.sports_raw == ["esimerkkilaji"]
    assert obs.website_raw == "https://example.invalid/alpha"
    assert obs.email_raw == "info@alpha.example"
    assert obs.phone_raw is not None
    assert obs.address_raw is not None


def test_collector_result_includes_contact_persons() -> None:
    results = asyncio.run(MockCollector().collect())
    alpha = next(r for r in results if r.observation.name_raw == "Esimerkki Urheiluseura Alpha")

    assert len(alpha.observation.contact_persons) == 1
    person = alpha.observation.contact_persons[0]
    assert person.role == "sihteeri"
    assert person.emails == ["sihteeri@alpha.example"]
    assert person.observation_confidence is not None


def test_run_collector_sets_ingestion_run_id() -> None:
    summary = asyncio.run(run_collector(MockCollector()))

    assert summary.run.status == "success"
    assert summary.run.records_fetched == 3
    assert all(obs.ingestion_run_id == summary.run.run_id for obs in summary.observations)


def test_collector_observations_merge_compatible() -> None:
    summary = asyncio.run(run_collector(MockCollector()))
    sources = {
        "mock": Source(
            source_id="mock",
            name="Mock-lähde (kehitys)",
            category=SourceCategory.OTHER,
            geographic_coverage="Kehitys",
            merge_priority=50,
        )
    }

    clubs, processed = ingest_observations(summary.observations, [], sources=sources)

    assert len(clubs) == 3
    assert len(processed) == 3

    alpha = next(c for c in clubs if c.contact.email == "info@alpha.example")
    assert alpha.identity.name  # master-nimi laskettu havainnosta
    assert len(get_contact_person_observations(alpha, role="sihteeri")) == 1


def test_default_registry_includes_mock_collector() -> None:
    registry = default_registry()
    sources = dict(registry.list_sources())

    assert "mock" in sources
    assert registry.get("mock").source_id == "mock"


def test_mock_collector_supports_url() -> None:
    collector = MockCollector()

    assert collector.supports_url("mock://clubs/alpha")
    assert collector.supports_url("https://example.invalid/alpha")
    assert not collector.supports_url("https://www.example.fi/seura")
