"""CanonicalClubBuilder-testit."""

from __future__ import annotations

import copy

import pytest

from urheiluseurapro.resolution.canonical import (
    CanonicalClubBuilder,
    build_canonical_club,
)


def _single_record() -> dict[str, object]:
    return {
        "name": "Ilves Urheiluseura ry",
        "municipality": "Tampere",
        "email": "info@ilves.example",
        "phone": "+358 40 111 1111",
        "website": "https://www.ilves.example",
        "sports": ["jalkapallo", "futsal"],
        "source_id": "file-import",
        "source_url": "file:///data/clubs.csv",
        "source_record_key": "clubs.csv:1",
        "confidence": 0.88,
        "address": "Kisatie 1",
        "contact_persons": [{"full_name": "Matti Meikäläinen", "role": "puheenjohtaja"}],
    }


def test_build_single_record() -> None:
    record = _single_record()
    club = CanonicalClubBuilder().build(record)

    assert club.canonical_name == "Ilves Urheiluseura ry"
    assert club.municipality == "Tampere"
    assert club.emails == ["info@ilves.example"]
    assert club.phones == ["+358401111111"]
    assert club.websites == ["https://www.ilves.example"]
    assert club.sports == ["jalkapallo", "futsal"]
    assert club.confidence == 0.88
    assert club.source_records == [record]
    assert club.source_records[0]["address"] == "Kisatie 1"
    assert club.source_records[0]["contact_persons"][0]["full_name"] == "Matti Meikäläinen"


def test_build_preserves_all_source_fields() -> None:
    record = _single_record()
    record["raw"] = {"http": {"url": "https://example.invalid/feed.json"}}
    original = copy.deepcopy(record)

    club = build_canonical_club(record)

    assert club.source_records[0] == original
    assert record == original


def test_build_single_record_provenance() -> None:
    club = CanonicalClubBuilder().build(_single_record())

    fields = {entry["field"] for entry in club.provenance}
    assert fields == {"canonical_name", "municipality", "emails", "phones", "websites", "sports"}

    email_entry = next(entry for entry in club.provenance if entry["field"] == "emails")
    assert email_entry["value"] == "info@ilves.example"
    assert email_entry["source_index"] == 0
    assert email_entry["source_id"] == "file-import"
    assert email_entry["source_url"] == "file:///data/clubs.csv"
    assert email_entry["record_field"] == "email"


def test_build_many_merges_contact_fields() -> None:
    records = [
        {
            "name": "Ilves Urheiluseura ry",
            "municipality": "Tampere",
            "email": "info@ilves.example",
            "phone": "+358 40 111 1111",
            "website": "https://ilves.example",
            "sports": ["jalkapallo"],
            "source_id": "source-a",
            "confidence": 0.80,
        },
        {
            "name_raw": "ILVES URHEILUSEURA R.Y.",
            "municipality_raw": "tampere",
            "email_raw": "hallitus@ilves.example",
            "phone_raw": "0402222222",
            "website_raw": "www.ilves.example/info",
            "sports_raw": ["futsal"],
            "source_id": "source-b",
            "confidence": 0.95,
        },
    ]

    club = CanonicalClubBuilder().build_many(records)

    assert club.canonical_name == "ILVES URHEILUSEURA R.Y."
    assert club.municipality == "Tampere"
    assert club.emails == ["hallitus@ilves.example", "info@ilves.example"]
    assert club.phones == ["+358402222222", "+358401111111"]
    assert club.websites == ["https://www.ilves.example/info"]
    assert club.sports == ["futsal", "jalkapallo"]
    assert club.confidence == 0.95
    assert len(club.source_records) == 2


def test_build_many_deduplicates_normalized_values() -> None:
    records = [
        {
            "name": "Ilves ry",
            "email": "INFO@ILVES.EXAMPLE",
            "phone": "+358 40 111 1111",
            "website": "https://www.ilves.example",
            "source_id": "a",
        },
        {
            "name": "Ilves Urheiluseura",
            "email_raw": "info@ilves.example",
            "phone_raw": "0401111111",
            "website_raw": "http://ilves.example",
            "source_id": "b",
        },
    ]

    club = build_canonical_club(records)

    assert club.emails == ["info@ilves.example"]
    assert club.phones == ["+358401111111"]
    assert club.websites == ["https://www.ilves.example"]
    assert len([entry for entry in club.provenance if entry["field"] == "emails"]) == 1


def test_build_many_provenance_covers_all_sources() -> None:
    records = [
        {
            "name": "Seura A",
            "email": "a@example.invalid",
            "source_id": "source-a",
            "source_record_key": "a:1",
        },
        {
            "name": "Seura A",
            "email": "b@example.invalid",
            "source_id": "source-b",
            "source_record_key": "b:1",
        },
    ]

    club = CanonicalClubBuilder().build_many(records)

    email_provenance = [entry for entry in club.provenance if entry["field"] == "emails"]
    assert len(email_provenance) == 2
    assert {entry["source_id"] for entry in email_provenance} == {"source-a", "source-b"}
    assert {entry["source_record_key"] for entry in email_provenance} == {"a:1", "b:1"}


def test_build_many_prefers_higher_confidence_name_and_municipality() -> None:
    records = [
        {
            "name": "Lyhyt",
            "municipality": "Helsinki",
            "confidence": 0.50,
            "source_id": "low",
        },
        {
            "name_official": "Esimerkki Urheiluseura Rekisteröity Yhdistys",
            "municipality_normalized": "Tampere",
            "confidence": 0.99,
            "source_id": "high",
        },
    ]

    club = build_canonical_club(records)

    assert club.canonical_name == "Esimerkki Urheiluseura Rekisteröity Yhdistys"
    assert club.municipality == "Tampere"
    assert club.confidence == 0.99


def test_build_many_empty_list_raises() -> None:
    with pytest.raises(ValueError, match="At least one source record"):
        CanonicalClubBuilder().build_many([])


def test_build_minimal_record_defaults() -> None:
    club = build_canonical_club({"name": "Minimi Seura"})

    assert club.canonical_name == "Minimi Seura"
    assert club.municipality is None
    assert club.emails == []
    assert club.phones == []
    assert club.websites == []
    assert club.sports == []
    assert club.confidence == 1.0
    assert len(club.provenance) == 1
    assert club.provenance[0]["field"] == "canonical_name"


def test_build_minimal_record_provenance_has_no_extra_meta() -> None:
    club = build_canonical_club({"name": "Minimi Seura"})

    entry = club.provenance[0]
    assert entry["field"] == "canonical_name"
    assert entry["value"] == "Minimi Seura"
    assert entry["source_index"] == 0
    assert entry["record_field"] == "name"
    assert "source_id" not in entry
