"""Canonical club -tallennus SQLiteen."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from urheiluseurapro.resolution.canonical import CanonicalClub

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS canonical_clubs (
    id TEXT PRIMARY KEY,
    canonical_name TEXT,
    municipality TEXT,
    email TEXT,
    website TEXT,
    phone TEXT,
    emails TEXT NOT NULL DEFAULT '[]',
    phones TEXT NOT NULL DEFAULT '[]',
    websites TEXT NOT NULL DEFAULT '[]',
    sports TEXT NOT NULL DEFAULT '[]',
    provenance TEXT NOT NULL DEFAULT '[]',
    source_records TEXT NOT NULL DEFAULT '[]',
    confidence REAL NOT NULL DEFAULT 0.0,
    updated_at TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class StoredCanonicalClub:
    """Tietokannasta luettu canonical club tunnisteineen."""

    id: str
    club: CanonicalClub
    updated_at: datetime


class SQLiteRepository:
    """SQLite-tallennus canonical club -rakenteille."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    @classmethod
    def connect(cls, database: str | Path = ":memory:") -> SQLiteRepository:
        conn = sqlite3.connect(str(database))
        return cls(conn)

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> SQLiteRepository:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _init_schema(self) -> None:
        self._conn.executescript(_SCHEMA_SQL)
        self._conn.commit()

    def save_canonical_club(
        self,
        club: CanonicalClub,
        *,
        club_id: str | None = None,
    ) -> str:
        """Tallenna canonical club. Palauttaa tunnisteen."""
        record_id = club_id or str(uuid4())
        updated_at = _utc_now()
        row = _club_to_row(club, record_id, updated_at)
        self._conn.execute(
            """
            INSERT INTO canonical_clubs (
                id,
                canonical_name,
                municipality,
                email,
                website,
                phone,
                emails,
                phones,
                websites,
                sports,
                provenance,
                source_records,
                confidence,
                updated_at
            ) VALUES (
                :id,
                :canonical_name,
                :municipality,
                :email,
                :website,
                :phone,
                :emails,
                :phones,
                :websites,
                :sports,
                :provenance,
                :source_records,
                :confidence,
                :updated_at
            )
            """,
            row,
        )
        self._conn.commit()
        return record_id

    def load_canonical_clubs(self) -> list[StoredCanonicalClub]:
        """Lataa kaikki canonical clubit."""
        rows = self._conn.execute(
            "SELECT * FROM canonical_clubs ORDER BY updated_at ASC, id ASC"
        ).fetchall()
        return [_row_to_stored(row) for row in rows]

    def get_by_id(self, club_id: str) -> StoredCanonicalClub | None:
        """Hae canonical club tunnisteella."""
        row = self._conn.execute(
            "SELECT * FROM canonical_clubs WHERE id = ?",
            (club_id,),
        ).fetchone()
        if row is None:
            return None
        return _row_to_stored(row)

    def update(self, club_id: str, club: CanonicalClub) -> bool:
        """Päivitä olemassa oleva canonical club."""
        updated_at = _utc_now()
        row = _club_to_row(club, club_id, updated_at)
        cursor = self._conn.execute(
            """
            UPDATE canonical_clubs
            SET
                canonical_name = :canonical_name,
                municipality = :municipality,
                email = :email,
                website = :website,
                phone = :phone,
                emails = :emails,
                phones = :phones,
                websites = :websites,
                sports = :sports,
                provenance = :provenance,
                source_records = :source_records,
                confidence = :confidence,
                updated_at = :updated_at
            WHERE id = :id
            """,
            row,
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def delete(self, club_id: str) -> bool:
        """Poista canonical club tunnisteella."""
        cursor = self._conn.execute(
            "DELETE FROM canonical_clubs WHERE id = ?",
            (club_id,),
        )
        self._conn.commit()
        return cursor.rowcount > 0


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _dump_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _load_json_list(value: str | None) -> list[Any]:
    if not value:
        return []
    loaded = json.loads(value)
    if not isinstance(loaded, list):
        raise ValueError("Expected JSON list")
    return loaded


def _club_to_row(club: CanonicalClub, club_id: str, updated_at: str) -> dict[str, Any]:
    return {
        "id": club_id,
        "canonical_name": club.canonical_name,
        "municipality": club.municipality,
        "email": club.emails[0] if club.emails else None,
        "website": club.websites[0] if club.websites else None,
        "phone": club.phones[0] if club.phones else None,
        "emails": _dump_json(club.emails),
        "phones": _dump_json(club.phones),
        "websites": _dump_json(club.websites),
        "sports": _dump_json(club.sports),
        "provenance": _dump_json(club.provenance),
        "source_records": _dump_json(club.source_records),
        "confidence": club.confidence,
        "updated_at": updated_at,
    }


def _row_to_stored(row: sqlite3.Row) -> StoredCanonicalClub:
    emails = _load_json_list(row["emails"])
    if not emails and row["email"]:
        emails = [row["email"]]

    phones = _load_json_list(row["phones"])
    if not phones and row["phone"]:
        phones = [row["phone"]]

    websites = _load_json_list(row["websites"])
    if not websites and row["website"]:
        websites = [row["website"]]

    club = CanonicalClub(
        canonical_name=row["canonical_name"],
        municipality=row["municipality"],
        emails=emails,
        phones=phones,
        websites=websites,
        sports=[str(item) for item in _load_json_list(row["sports"])],
        source_records=_load_json_list(row["source_records"]),
        provenance=_load_json_list(row["provenance"]),
        confidence=float(row["confidence"]),
    )
    return StoredCanonicalClub(
        id=row["id"],
        club=club,
        updated_at=_parse_timestamp(row["updated_at"]),
    )
