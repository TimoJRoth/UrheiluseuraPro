"""Normalisointikerroksen testit."""

from __future__ import annotations

import asyncio
from pathlib import Path

from urheiluseurapro.collectors.file_import import FileImportCollector
from urheiluseurapro.collectors.runner import run_collector
from urheiluseurapro.models.contact_person import ObservationContactPerson
from urheiluseurapro.models.observation import ClubObservation
from urheiluseurapro.models.source_config import SourceConfig
from urheiluseurapro.normalizers import (
    clean_text,
    normalize_club_record,
    normalize_contact_person,
    normalize_email,
    normalize_municipality,
    normalize_observation,
    normalize_phone,
    normalize_sports,
    normalize_website,
)

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "data" / "fixtures"


def test_clean_text_empty_and_whitespace() -> None:
    assert clean_text(None) is None
    assert clean_text("") is None
    assert clean_text("   ") is None
    assert clean_text("  Esimerkki   Seura  ") == "Esimerkki Seura"


def test_normalize_email_lowercase() -> None:
    assert normalize_email("  INFO@Example.COM  ") == "info@example.com"
    assert normalize_email("") is None


def test_normalize_phone_strips_formatting() -> None:
    assert normalize_phone("+358 (40) 123 4567") == "+358401234567"
    assert normalize_phone("0401234567") == "+358401234567"
    assert normalize_phone("123") is None


def test_normalize_website_adds_https() -> None:
    assert normalize_website("  example.invalid/club  ") == "https://example.invalid/club"
    assert normalize_website("https://example.invalid/club/") == "https://example.invalid/club"


def test_normalize_municipality() -> None:
    assert normalize_municipality("  tampere ") == "Tampere"
    assert normalize_municipality("  ") is None


def test_normalize_sports_from_string_and_list() -> None:
    assert normalize_sports("Jalkapallo; Futsal") == ["jalkapallo", "futsal"]
    assert normalize_sports([" Jalkapallo ", "jalkapallo", ""]) == ["jalkapallo"]


def test_normalize_contact_person() -> None:
    person = normalize_contact_person(
        ObservationContactPerson(
            full_name="  Ada Alpha  ",
            role="  sihteeri  ",
            emails=[" INFO@Alpha.EXAMPLE "],
            phones=["+358 (40) 100 0002"],
        )
    )

    assert person.full_name == "Ada Alpha"
    assert person.role == "sihteeri"
    assert person.emails == ["info@alpha.example"]
    assert person.phones == ["+358401000002"]


def test_normalize_observation_sets_raw_and_normalized_fields() -> None:
    observation = normalize_observation(
        ClubObservation(
            observation_id="obs-1",
            source_id="test",
            name_raw="  Ilves Urheiluseura ry  ",
            municipality_raw=" tampere ",
            sports_raw=[" Jalkapallo "],
            email_raw=" INFO@ILVES.EXAMPLE ",
            phone_raw="+358 40 111 1111",
            website_raw="ilves.example",
            contact_persons=[
                ObservationContactPerson(
                    full_name="  Test Person  ",
                    role=" pj ",
                    emails=[" PJ@ILVES.EXAMPLE "],
                    phones=[],
                )
            ],
        )
    )

    assert observation.name_raw == "Ilves Urheiluseura ry"
    assert observation.municipality_raw == "Tampere"
    assert observation.email_raw == "info@ilves.example"
    assert observation.phone_raw == "+358401111111"
    assert observation.website_raw == "https://ilves.example"
    assert observation.sports_raw == ["jalkapallo"]
    assert observation.email_normalized == "info@ilves.example"
    assert observation.phone_normalized == "+358401111111"
    assert observation.website_normalized == "https://ilves.example"
    assert observation.municipality_normalized == "Tampere"
    assert observation.name_normalized == "ilves"


def test_normalize_club_record() -> None:
    record = normalize_club_record(
        {
            "name": "  Test Seura  ",
            "municipality": " oulu ",
            "sports": "jalkapallo, futsal",
            "website": "example.invalid",
            "email": "INFO@TEST.EXAMPLE",
            "phone": "+358 40 999 9999",
            "contact_persons": [
                {
                    "full_name": "  Contact  ",
                    "role": " sihteeri ",
                    "emails": [" A@B.EXAMPLE "],
                    "phones": ["0409999999"],
                }
            ],
        }
    )

    assert record["name"] == "Test Seura"
    assert record["municipality"] == "Oulu"
    assert record["sports"] == ["jalkapallo", "futsal"]
    assert record["website"] == "https://example.invalid"
    assert record["email"] == "info@test.example"


def _file_import_config() -> SourceConfig:
    return SourceConfig.from_merged(
        {
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
    )


def test_file_import_collector_applies_normalization() -> None:
    summary = asyncio.run(
        run_collector(
            FileImportCollector(
                FIXTURE_DIR / "file_import_messy.csv",
                source_config=_file_import_config(),
            )
        )
    )

    obs = summary.observations[0]
    assert obs.name_raw == "Esimerkki Urheiluseura File Messy"
    assert obs.municipality_raw == "Tampere"
    assert obs.sports_raw == ["jalkapallo", "futsal"]
    assert obs.email_raw == "info@messy.example"
    assert obs.website_raw == "https://example.invalid/messy"
    assert obs.phone_raw == "+358407000001"
    assert obs.email_normalized == "info@messy.example"
    assert obs.contact_persons[0].emails == ["sihteeri@messy.example"]
