"""Resolution MergeEngine-testit."""

from __future__ import annotations

from urheiluseurapro.resolution.merge import MergeEngine, merge_club_records


def test_empty_list_returns_empty() -> None:
    assert merge_club_records([]) == []


def test_same_email_records_merge() -> None:
    records = [
        {
            "name": "Ilves Urheiluseura ry",
            "municipality": "Tampere",
            "email": "info@ilves.example",
            "source_id": "source-a",
            "source_record_key": "a:1",
        },
        {
            "name": "Toinen nimi",
            "municipality": "Helsinki",
            "email": "INFO@ILVES.EXAMPLE",
            "source_id": "source-b",
            "source_record_key": "b:1",
        },
    ]

    clubs = merge_club_records(records)

    assert len(clubs) == 1
    assert clubs[0].emails == ["info@ilves.example"]
    assert len(clubs[0].source_records) == 2
    assert {record["source_id"] for record in clubs[0].source_records} == {"source-a", "source-b"}


def test_same_website_records_merge() -> None:
    records = [
        {
            "name": "Seura A",
            "website": "https://www.ilves.example",
            "source_id": "a",
        },
        {
            "name": "Seura B",
            "website": "http://ilves.example/path",
            "source_id": "b",
        },
    ]

    clubs = merge_club_records(records)

    assert len(clubs) == 1
    assert clubs[0].websites == ["https://www.ilves.example"]
    assert len(clubs[0].source_records) == 2


def test_same_phone_records_merge() -> None:
    records = [
        {
            "name": "Seura A",
            "phone": "+358 40 123 4567",
            "source_id": "a",
        },
        {
            "name": "Seura B",
            "phone": "0401234567",
            "source_id": "b",
        },
    ]

    clubs = merge_club_records(records)

    assert len(clubs) == 1
    assert clubs[0].phones == ["+358401234567"]
    assert len(clubs[0].source_records) == 2


def test_different_clubs_do_not_merge() -> None:
    records = [
        {
            "name": "Ilves Urheiluseura ry",
            "municipality": "Tampere",
            "email": "info@ilves.example",
            "source_id": "ilves",
        },
        {
            "name": "HJK ry",
            "municipality": "Helsinki",
            "email": "info@hjk.example",
            "source_id": "hjk",
        },
    ]

    clubs = merge_club_records(records)

    assert len(clubs) == 2
    assert {club.source_records[0]["source_id"] for club in clubs} == {"ilves", "hjk"}


def test_three_records_from_same_club_merge_to_one() -> None:
    records = [
        {
            "name": "Ilves Urheiluseura ry",
            "email": "info@ilves.example",
            "source_id": "a",
            "source_record_key": "a:1",
        },
        {
            "name": "Ilves",
            "email": "info@ilves.example",
            "phone": "+358 40 111 1111",
            "source_id": "b",
            "source_record_key": "b:1",
        },
        {
            "name": "Ilves Urheiluseura",
            "phone": "0401111111",
            "website": "https://ilves.example",
            "source_id": "c",
            "source_record_key": "c:1",
        },
    ]

    clubs = MergeEngine().merge(records)

    assert len(clubs) == 1
    club = clubs[0]
    assert len(club.source_records) == 3
    assert club.emails == ["info@ilves.example"]
    assert club.phones == ["+358401111111"]
    assert club.websites == ["https://ilves.example"]
    assert {record["source_id"] for record in club.source_records} == {"a", "b", "c"}


def test_provenance_is_preserved() -> None:
    records = [
        {
            "name": "Ilves ry",
            "email": "info@ilves.example",
            "source_id": "source-a",
            "source_url": "file:///a.csv",
            "source_record_key": "a:1",
            "confidence": 0.80,
        },
        {
            "name": "Ilves Urheiluseura",
            "email": "info@ilves.example",
            "source_id": "source-b",
            "source_url": "file:///b.csv",
            "source_record_key": "b:1",
            "confidence": 0.95,
            "address": "Kisatie 1",
        },
    ]

    club = merge_club_records(records)[0]

    assert len(club.provenance) > 0
    assert len(club.source_records) == 2
    assert club.source_records[1]["address"] == "Kisatie 1"

    email_provenance = [entry for entry in club.provenance if entry["field"] == "emails"]
    assert len(email_provenance) == 1
    assert email_provenance[0]["source_id"] in {"source-a", "source-b"}

    source_ids_in_provenance = {
        entry["source_id"]
        for entry in club.provenance
        if "source_id" in entry
    }
    assert source_ids_in_provenance.issubset({"source-a", "source-b"})


def test_name_and_municipality_only_do_not_merge() -> None:
    records = [
        {
            "name": "Ilves Urheiluseura ry",
            "municipality": "Tampere",
            "source_id": "a",
        },
        {
            "name": "Ilves Urheiluseura",
            "municipality": "tampere",
            "source_id": "b",
        },
    ]

    clubs = merge_club_records(records)

    assert len(clubs) == 2
