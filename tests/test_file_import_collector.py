"""FileImportCollector-testit."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from urheiluseurapro.collectors.file_import import (
    FileImportCollector,
    FileImportNotFoundError,
    FileImportParseError,
    FileImportUnsupportedFormatError,
)
from urheiluseurapro.collectors.runner import run_collector
from urheiluseurapro.models.source_config import SourceConfig
from urheiluseurapro.pipeline.ingest import ingest_observations

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "data" / "fixtures"


def _source_config(**overrides: float | int | str | bool) -> SourceConfig:
    defaults: dict[str, float | int | str | bool] = {
        "source_id": "file-import",
        "display_name": "Tiedostotuonti",
        "enabled": True,
        "request_timeout": 30.0,
        "request_delay": 0.0,
        "request_retries": 3,
        "retry_backoff_seconds": 0.0,
        "user_agent": "UrheiluseuraPro-Test/0.1",
        "confidence_default": 0.88,
    }
    return SourceConfig.from_merged(defaults, overrides)


def _collector(path: Path, **kwargs: object) -> FileImportCollector:
    return FileImportCollector(path, source_config=_source_config(), **kwargs)


def test_csv_import_returns_collector_results() -> None:
    results = asyncio.run(_collector(FIXTURE_DIR / "file_import_clubs.csv").collect())

    assert len(results) == 3
    alpha = next(r for r in results if r.observation.name_raw.endswith("Alpha"))
    assert alpha.source == "file-import"
    assert alpha.observation.sports_raw == ["jalkapallo"]
    assert alpha.observation.municipality_raw == "Tampere"
    assert alpha.observation.email_raw == "info@alpha.example"
    assert len(alpha.observation.contact_persons) == 1
    assert alpha.observation.contact_persons[0].role == "sihteeri"


def test_json_import_returns_collector_results() -> None:
    results = asyncio.run(_collector(FIXTURE_DIR / "file_import_clubs.json").collect())

    assert len(results) == 2
    delta = next(r for r in results if r.observation.name_raw.endswith("Delta"))
    assert delta.observation.sports_raw == ["jalkapallo"]
    assert delta.observation.phone_raw == "+358 40 400 0001"


def test_missing_optional_fields_are_allowed() -> None:
    result = asyncio.run(_collector(FIXTURE_DIR / "file_import_minimal.csv").collect())[0]
    obs = result.observation

    assert obs.name_raw == "Esimerkki Urheiluseura File Minimal"
    assert obs.municipality_raw == "Oulu"
    assert obs.sports_raw == ["jalkapallo"]
    assert obs.website_raw is None
    assert obs.email_raw is None
    assert obs.phone_raw is None
    assert obs.address_raw is None
    assert obs.contact_persons == []


def test_field_mapping_renames_columns() -> None:
    mapping = {
        "club_name": "name",
        "city": "municipality",
        "sport": "sports",
        "web": "website",
        "contact_name": "contact_person_name",
        "contact_role": "contact_person_role",
    }
    result = asyncio.run(
        _collector(FIXTURE_DIR / "file_import_mapped.csv", field_mapping=mapping).collect()
    )[0]

    assert result.observation.name_raw == "Esimerkki Urheiluseura File Mapped"
    assert result.observation.municipality_raw == "Jyväskylä"
    assert result.observation.website_raw == "https://example.invalid/mapped"
    assert result.observation.contact_persons[0].full_name == "Cara Mapped"


def test_provenance_uses_file_url_and_fetched_at() -> None:
    path = FIXTURE_DIR / "file_import_clubs.csv"
    result = asyncio.run(_collector(path).collect())[0]

    assert result.source_url == path.resolve().as_uri()
    assert result.fetched_at is not None
    assert result.confidence == 0.88
    assert result.observation.source_id == "file-import"
    assert result.observation.raw is not None
    assert result.observation.raw["file"]["source_url"].startswith("file://")


def test_invalid_json_raises_parse_error() -> None:
    with pytest.raises(FileImportParseError):
        asyncio.run(_collector(FIXTURE_DIR / "file_import_invalid.json").collect())


def test_missing_file_raises_not_found() -> None:
    with pytest.raises(FileImportNotFoundError):
        asyncio.run(_collector(FIXTURE_DIR / "does_not_exist.csv").collect())


def test_unsupported_excel_raises() -> None:
    excel_path = FIXTURE_DIR / "file_import_clubs.xlsx"
    excel_path.write_bytes(b"fake")
    try:
        with pytest.raises(FileImportUnsupportedFormatError):
            asyncio.run(_collector(excel_path).collect())
    finally:
        excel_path.unlink(missing_ok=True)


def test_ingest_merge_compatible() -> None:
    summary = asyncio.run(run_collector(_collector(FIXTURE_DIR / "file_import_clubs.csv")))

    clubs, processed = ingest_observations(summary.observations, [], sources={})

    assert len(clubs) == 3
    assert len(processed) == 3


def test_supports_url() -> None:
    collector = _collector(FIXTURE_DIR / "file_import_clubs.csv")
    file_uri = (FIXTURE_DIR / "file_import_clubs.csv").resolve().as_uri()

    assert collector.supports_url(file_uri)
    assert not collector.supports_url("https://example.invalid/clubs.csv")
