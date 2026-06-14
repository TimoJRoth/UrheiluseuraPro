"""JSON-syöte-collectorin testit (HTTP MockTransport)."""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx

from urheiluseurapro.collectors.examples.json_feed import JsonFeedCollector
from urheiluseurapro.collectors.http.client import HttpClient
from urheiluseurapro.collectors.registry import CollectorRegistry, default_registry
from urheiluseurapro.collectors.runner import run_collector
from urheiluseurapro.config import Settings
from urheiluseurapro.pipeline.ingest import ingest_observations
from urheiluseurapro.sources.registry import default_source_registry

FIXTURE_PATH = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "example_clubs.json"
FIXTURE_JSON = FIXTURE_PATH.read_text(encoding="utf-8")
FEED_URL = "https://example.invalid/api/clubs"


def _fast_settings() -> Settings:
    return Settings(
        request_delay=0.0,
        request_retries=3,
        request_retry_backoff_seconds=0.0,
    )


def _json_feed_source_config():
    return default_source_registry(_fast_settings()).require("example-json-feed").model_copy(
        update={
            "enabled": True,
            "request_delay": 0.0,
            "request_retries": 3,
            "retry_backoff_seconds": 0.0,
        }
    )


def _collector_with_mock_transport() -> JsonFeedCollector:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, text=FIXTURE_JSON, request=request)
    )
    source_config = _json_feed_source_config()

    async def setup() -> JsonFeedCollector:
        client = HttpClient(source_config, transport=transport)
        await client.__aenter__()
        return JsonFeedCollector(
            source_config=source_config,
            settings=_fast_settings(),
            http_client=client,
        )

    return asyncio.run(setup())


def test_json_feed_collector_returns_three_clubs() -> None:
    results = asyncio.run(_collector_with_mock_transport().collect())

    assert len(results) == 3
    names = {result.observation.name_raw for result in results}
    assert "Esimerkki Urheiluseura Delta" in names


def test_json_feed_collector_stores_provenance() -> None:
    result = asyncio.run(_collector_with_mock_transport().collect())[0]

    assert result.source == "example-json-feed"
    assert result.source_url is not None
    assert result.fetched_at is not None
    assert result.observation.source_url is not None
    assert result.observation.raw is not None
    assert result.observation.raw["http"]["url"] == FEED_URL


def test_json_feed_collector_merge_compatible() -> None:
    summary = asyncio.run(run_collector(_collector_with_mock_transport()))

    clubs, processed = ingest_observations(summary.observations, [], sources={})

    assert len(clubs) == 3
    assert len(processed) == 3


def test_json_feed_not_in_default_registry() -> None:
    registry = default_registry()
    sources = dict(registry.list_sources())

    assert "example-json-feed" not in sources
    assert "mock" in sources


def test_json_feed_can_be_registered_manually() -> None:
    registry = CollectorRegistry()
    registry.register(_collector_with_mock_transport())

    assert registry.get("example-json-feed").source_id == "example-json-feed"


def test_json_feed_supports_url() -> None:
    collector = JsonFeedCollector(source_config=_json_feed_source_config())

    assert collector.supports_url(FEED_URL)
    assert not collector.supports_url("https://other.example/api/clubs")


def test_json_feed_uses_source_config_not_hardcoded_values() -> None:
    collector = JsonFeedCollector(source_config=_json_feed_source_config())

    assert collector.source_id == "example-json-feed"
    assert collector.display_name == "Esimerkki JSON-syöte (HTTP)"
    assert collector.default_confidence == 0.82
    assert collector.feed_url == FEED_URL


def test_json_feed_collector_normalizes_messy_data() -> None:
    messy_json = (FIXTURE_PATH.parent / "example_clubs_messy.json").read_text(encoding="utf-8")
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, text=messy_json, request=request)
    )
    source_config = _json_feed_source_config()

    async def run() -> object:
        client = HttpClient(source_config, transport=transport)
        await client.__aenter__()
        collector = JsonFeedCollector(
            source_config=source_config,
            settings=_fast_settings(),
            http_client=client,
        )
        return await run_collector(collector)

    summary = asyncio.run(run())
    obs = summary.observations[0]

    assert obs.name_raw == "Esimerkki Urheiluseura Messy JSON"
    assert obs.municipality_raw == "Tampere"
    assert obs.sports_raw == ["jalkapallo", "futsal"]
    assert obs.email_raw == "info@messy-json.example"
    assert obs.website_raw == "https://example.invalid/messy-json"
    assert obs.phone_raw == "+358408000001"
    assert obs.email_normalized == "info@messy-json.example"
    assert obs.contact_persons[0].emails == ["sihteeri@messy-json.example"]
