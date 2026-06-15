"""SQLiteRepository canonical clubeille."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from urheiluseurapro.resolution.canonical import CanonicalClub
from urheiluseurapro.storage.sqlite_repository import SQLiteRepository


@pytest.fixture
def db_path() -> Path:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        path = Path(handle.name)
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture
def repo(db_path: Path) -> SQLiteRepository:
    repository = SQLiteRepository.connect(db_path)
    yield repository
    repository.close()


def _sample_club(**overrides: object) -> CanonicalClub:
    data = {
        "canonical_name": "Ilves Urheiluseura ry",
        "municipality": "Tampere",
        "emails": ["info@ilves.example"],
        "phones": ["+358401111111"],
        "websites": ["https://ilves.example"],
        "sports": ["jalkapallo", "futsal"],
        "source_records": [
            {
                "name": "Ilves Urheiluseura ry",
                "email": "info@ilves.example",
                "source_id": "source-a",
            }
        ],
        "provenance": [
            {
                "field": "emails",
                "value": "info@ilves.example",
                "source_index": 0,
                "source_id": "source-a",
            }
        ],
        "confidence": 0.95,
    }
    data.update(overrides)
    return CanonicalClub(**data)


def test_empty_database_returns_no_clubs(repo: SQLiteRepository) -> None:
    assert repo.load_canonical_clubs() == []
    assert repo.get_by_id("missing") is None


def test_create_and_load(repo: SQLiteRepository) -> None:
    club = _sample_club()
    club_id = repo.save_canonical_club(club)

    loaded = repo.get_by_id(club_id)
    assert loaded is not None
    assert loaded.id == club_id
    assert loaded.club == club
    assert loaded.club.sports == ["jalkapallo", "futsal"]
    assert loaded.club.provenance[0]["source_id"] == "source-a"
    assert loaded.updated_at is not None


def test_load_multiple_clubs(repo: SQLiteRepository) -> None:
    first_id = repo.save_canonical_club(_sample_club(canonical_name="Ilves ry"))
    second_id = repo.save_canonical_club(
        _sample_club(
            canonical_name="HJK ry",
            municipality="Helsinki",
            emails=["info@hjk.example"],
            phones=["+358401234567"],
            websites=["https://hjk.example"],
            sports=["jalkapallo"],
            source_records=[{"name": "HJK ry", "source_id": "hjk"}],
            provenance=[{"field": "canonical_name", "value": "HJK ry"}],
            confidence=0.88,
        )
    )

    clubs = repo.load_canonical_clubs()

    assert len(clubs) == 2
    assert {stored.id for stored in clubs} == {first_id, second_id}
    assert {stored.club.canonical_name for stored in clubs} == {"Ilves ry", "HJK ry"}


def test_update(repo: SQLiteRepository) -> None:
    club_id = repo.save_canonical_club(_sample_club())
    updated_club = _sample_club(
        municipality="Tammerfors",
        emails=["info@ilves.example", "hallitus@ilves.example"],
        sports=["jalkapallo"],
        confidence=0.99,
    )

    assert repo.update(club_id, updated_club) is True

    loaded = repo.get_by_id(club_id)
    assert loaded is not None
    assert loaded.club.municipality == "Tammerfors"
    assert loaded.club.emails == ["info@ilves.example", "hallitus@ilves.example"]
    assert loaded.club.sports == ["jalkapallo"]
    assert loaded.club.confidence == 0.99


def test_update_missing_returns_false(repo: SQLiteRepository) -> None:
    assert repo.update("missing-id", _sample_club()) is False


def test_delete(repo: SQLiteRepository) -> None:
    club_id = repo.save_canonical_club(_sample_club())

    assert repo.delete(club_id) is True
    assert repo.get_by_id(club_id) is None
    assert repo.load_canonical_clubs() == []


def test_delete_missing_returns_false(repo: SQLiteRepository) -> None:
    assert repo.delete("missing-id") is False


def test_json_fields_are_preserved_round_trip(repo: SQLiteRepository) -> None:
    club = _sample_club(
        sports=["jalkapallo", "futsal", "salibandy"],
        provenance=[
            {"field": "sports", "value": "jalkapallo", "source_id": "a"},
            {"field": "sports", "value": "futsal", "source_id": "b"},
        ],
        source_records=[
            {"name": "Ilves", "source_id": "a", "address": "Kisatie 1"},
            {"name": "Ilves Urheiluseura", "source_id": "b", "raw": {"http": {"url": "x"}}},
        ],
    )

    club_id = repo.save_canonical_club(club)
    loaded = repo.get_by_id(club_id)

    assert loaded is not None
    assert loaded.club.sports == ["jalkapallo", "futsal", "salibandy"]
    assert loaded.club.provenance == club.provenance
    assert loaded.club.source_records == club.source_records


def test_schema_is_created_automatically(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    before = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='canonical_clubs'"
    ).fetchone()
    conn.close()
    assert before is None

    repository = SQLiteRepository.connect(db_path)
    try:
        after = repository._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='canonical_clubs'"
        ).fetchone()
        assert after is not None
    finally:
        repository.close()


def test_primary_contact_columns_store_first_values(repo: SQLiteRepository) -> None:
    club = _sample_club(
        emails=["primary@ilves.example", "secondary@ilves.example"],
        phones=["+358401111111", "+358402222222"],
        websites=["https://primary.ilves.example", "https://secondary.ilves.example"],
    )
    club_id = repo.save_canonical_club(club)

    row = repo._conn.execute(
        "SELECT email, phone, website FROM canonical_clubs WHERE id = ?",
        (club_id,),
    ).fetchone()

    assert row is not None
    assert row["email"] == "primary@ilves.example"
    assert row["phone"] == "+358401111111"
    assert row["website"] == "https://primary.ilves.example"

    loaded = repo.get_by_id(club_id)
    assert loaded is not None
    assert loaded.club.emails == ["primary@ilves.example", "secondary@ilves.example"]
