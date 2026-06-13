"""SourceConfig-järjestelmän testit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from urheiluseurapro.collectors.mock import MockCollector
from urheiluseurapro.config import Settings
from urheiluseurapro.sources.registry import (
    DEFAULT_SOURCES_PATH,
    load_source_registry,
)

FUTURE_SOURCE_IDS = frozenset(
    {
        "palloliitto",
        "koripalloliitto",
        "jaakiekko",
        "lentopallo",
        "salibandy",
        "kunnat",
        "prh",
        "ytj",
    }
)


def test_sources_json_exists_and_loads() -> None:
    registry = load_source_registry()
    assert len(registry.list_all()) >= 10


def test_mock_source_enabled_by_default() -> None:
    registry = load_source_registry()
    mock = registry.require("mock")

    assert mock.enabled is True
    assert mock.source_id == "mock"
    assert mock.display_name == "Mock-lähde (kehitys)"
    assert mock.confidence_default == 0.75
    assert mock.base_url == "mock://"


def test_example_json_feed_disabled_by_default() -> None:
    registry = load_source_registry()
    config = registry.require("example-json-feed")

    assert config.enabled is False
    assert config.feed_url == "https://example.invalid/api/clubs"


def test_future_sources_defined_but_disabled() -> None:
    registry = load_source_registry()

    for source_id in FUTURE_SOURCE_IDS:
        config = registry.require(source_id)
        assert config.enabled is False, source_id
        assert config.display_name
        assert 0.0 < config.confidence_default <= 1.0


def test_http_defaults_from_settings_when_omitted_in_json() -> None:
    settings = Settings(
        request_timeout=12.0,
        request_delay=2.5,
        request_retries=5,
        request_retry_backoff_seconds=1.25,
        user_agent="Test-Agent/9.9",
    )
    registry = load_source_registry(settings)
    mock = registry.require("mock")

    assert mock.request_timeout == 12.0
    assert mock.request_delay == 2.5
    assert mock.request_retries == 5
    assert mock.retry_backoff_seconds == 1.25
    assert mock.user_agent == "Test-Agent/9.9"


def test_per_source_overrides_in_json(tmp_path: Path) -> None:
    payload = {
        "sources": [
            {
                "source_id": "mock",
                "display_name": "Test mock",
                "enabled": True,
                "confidence_default": 0.5,
                "request_timeout": 99.0,
                "request_delay": 0.1,
                "request_retries": 2,
                "retry_backoff_seconds": 0.2,
                "user_agent": "Override/1.0",
            }
        ]
    }
    config_path = tmp_path / "sources.json"
    config_path.write_text(json.dumps(payload), encoding="utf-8")

    registry = load_source_registry(path=config_path)
    mock = registry.require("mock")

    assert mock.request_timeout == 99.0
    assert mock.user_agent == "Override/1.0"
    assert mock.confidence_default == 0.5


def test_duplicate_source_id_raises(tmp_path: Path) -> None:
    payload = {
        "sources": [
            {
                "source_id": "mock",
                "display_name": "A",
                "enabled": True,
                "confidence_default": 0.5,
            },
            {
                "source_id": "mock",
                "display_name": "B",
                "enabled": False,
                "confidence_default": 0.5,
            },
        ]
    }
    config_path = tmp_path / "sources.json"
    config_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="päällekkäinen"):
        load_source_registry(path=config_path)


def test_mock_collector_reads_source_config() -> None:
    registry = load_source_registry()
    collector = MockCollector(source_config=registry.require("mock"))

    assert collector.source_id == "mock"
    assert collector.display_name == "Mock-lähde (kehitys)"
    assert collector.default_confidence == 0.75
    assert collector.base_url == "mock://"


def test_default_sources_path_points_to_project_config() -> None:
    assert DEFAULT_SOURCES_PATH.name == "sources.json"
    assert DEFAULT_SOURCES_PATH.parent.name == "config"
    assert DEFAULT_SOURCES_PATH.is_file()
