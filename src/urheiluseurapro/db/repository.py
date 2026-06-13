"""SQLite-repository – master-tietokanta."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from urheiluseurapro.config import project_root
from urheiluseurapro.db.schema_loader import load_sql, schema_sql_path, seed_sql_path
from urheiluseurapro.normalization.fields import normalize_club_name


@dataclass(frozen=True)
class OrganizationRecord:
    """Yksinkertainen organisaatiotietue hakutuloksille."""

    id: str
    name: str
    primary_sport_slug: str | None = None
    municipality_code: str | None = None
    email: str | None = None
    website: str | None = None


class SQLiteRepository:
    """UrheiluseuraPro SQLite-tietokantakerros."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    @classmethod
    def connect(cls, database: str | Path = ":memory:") -> SQLiteRepository:
        conn = sqlite3.connect(str(database))
        return cls(conn)

    @classmethod
    def open_file(cls, path: Path | None = None) -> SQLiteRepository:
        db_path = path or (project_root() / "data" / "urheiluseurapro.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return cls.connect(db_path)

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> SQLiteRepository:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def init_schema(self, *, with_seed: bool = False) -> None:
        """Luo taulut db/schema.sql-tiedostosta."""
        self._conn.executescript(load_sql(schema_sql_path()))
        if with_seed:
            self._conn.executescript(load_sql(seed_sql_path()))
        self._conn.commit()

    def execute(self, sql: str, params: tuple[Any, ...] | dict[str, Any] = ()) -> sqlite3.Cursor:
        return self._conn.execute(sql, params)

    def commit(self) -> None:
        self._conn.commit()

    # ------------------------------------------------------------------
    # Referenssit (testit / minimaalinen seed)
    # ------------------------------------------------------------------

    def ensure_region(self, code: str, name: str) -> None:
        self.execute(
            "INSERT OR IGNORE INTO regions (code, name) VALUES (?, ?)",
            (code, name),
        )
        self.commit()

    def ensure_municipality(self, code: str, name: str, region_code: str) -> None:
        self.ensure_region(region_code, region_code)
        self.execute(
            "INSERT OR IGNORE INTO municipalities (code, name, region_code) VALUES (?, ?, ?)",
            (code, name, region_code),
        )
        self.commit()

    # ------------------------------------------------------------------
    # Kirjoitus
    # ------------------------------------------------------------------

    def add_organization(
        self,
        name: str,
        *,
        organization_id: str | None = None,
        name_type: str = "display",
        is_primary_name: bool = True,
    ) -> str:
        """Lisää organisaation ja pää-nimen."""
        org_id = organization_id or str(uuid4())
        name_id = str(uuid4())
        normalized = normalize_club_name(name)

        self.execute(
            """
            INSERT INTO organizations (id)
            VALUES (?)
            """,
            (org_id,),
        )
        self.execute(
            """
            INSERT INTO organization_profile (organization_id)
            VALUES (?)
            """,
            (org_id,),
        )
        self.execute(
            """
            INSERT INTO organization_names (
                id, organization_id, name, name_type, normalized_name, is_primary
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name_id, org_id, name, name_type, normalized, int(is_primary_name)),
        )
        self.commit()
        return org_id

    def add_sport(
        self,
        slug: str,
        name_fi: str,
        *,
        name_en: str | None = None,
        sport_id: int | None = None,
    ) -> int:
        """Lisää lajin. Palauttaa sport_id:n."""
        if sport_id is not None:
            self.execute(
                """
                INSERT INTO sports (id, slug, name_fi, name_en)
                VALUES (?, ?, ?, ?)
                """,
                (sport_id, slug, name_fi, name_en),
            )
        else:
            cursor = self.execute(
                """
                INSERT INTO sports (slug, name_fi, name_en)
                VALUES (?, ?, ?)
                """,
                (slug, name_fi, name_en),
            )
            sport_id = int(cursor.lastrowid)
        self.commit()
        return int(sport_id)

    def link_organization_sport(
        self,
        organization_id: str,
        sport_id: int,
        *,
        is_primary: bool = False,
    ) -> None:
        """Liittää organisaation lajiin."""
        if is_primary:
            self.execute(
                """
                UPDATE organization_sports SET is_primary = 0
                WHERE organization_id = ?
                """,
                (organization_id,),
            )
        self.execute(
            """
            INSERT OR IGNORE INTO organization_sports (organization_id, sport_id, is_primary)
            VALUES (?, ?, ?)
            """,
            (organization_id, sport_id, int(is_primary)),
        )
        self._refresh_sport_profile(organization_id)
        self.commit()

    def add_email(
        self,
        organization_id: str,
        email: str,
        *,
        email_type: str = "general",
        is_primary: bool = False,
    ) -> str:
        """Lisää sähköpostin organisaatiolle."""
        email_id = str(uuid4())
        if is_primary:
            self.execute(
                "UPDATE organization_emails SET is_primary = 0 WHERE organization_id = ?",
                (organization_id,),
            )
        self.execute(
            """
            INSERT INTO organization_emails (
                id, organization_id, email, email_type, is_primary
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (email_id, organization_id, email, email_type, int(is_primary)),
        )
        self._refresh_contact_profile(organization_id)
        self.commit()
        return email_id

    def add_website(
        self,
        organization_id: str,
        url: str,
        *,
        website_type: str = "main",
        is_primary: bool = False,
    ) -> str:
        """Lisää verkkosivun organisaatiolle."""
        website_id = str(uuid4())
        if is_primary:
            self.execute(
                "UPDATE organization_websites SET is_primary = 0 WHERE organization_id = ?",
                (organization_id,),
            )
        self.execute(
            """
            INSERT INTO organization_websites (
                id, organization_id, url, website_type, is_primary
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (website_id, organization_id, url, website_type, int(is_primary)),
        )
        self._refresh_contact_profile(organization_id)
        self.commit()
        return website_id

    def add_location(
        self,
        organization_id: str,
        *,
        municipality_code: str | None = None,
        region_code: str | None = None,
        location_type: str = "primary",
        name: str | None = None,
        is_primary: bool = False,
    ) -> str:
        """Lisää toimipaikan (esim. kunta-hakuja varten)."""
        location_id = str(uuid4())
        if is_primary:
            self.execute(
                "UPDATE organization_locations SET is_primary = 0 WHERE organization_id = ?",
                (organization_id,),
            )
        self.execute(
            """
            INSERT INTO organization_locations (
                id, organization_id, location_type, name,
                municipality_code, region_code, is_primary
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                location_id,
                organization_id,
                location_type,
                name,
                municipality_code,
                region_code,
                int(is_primary),
            ),
        )
        self._refresh_location_profile(organization_id)
        self.commit()
        return location_id

    # ------------------------------------------------------------------
    # Haku
    # ------------------------------------------------------------------

    def find_organizations_by_sport(self, sport_slug: str) -> list[OrganizationRecord]:
        """Hae kaikki organisaatiot, joilla on annettu laji."""
        rows = self.execute(
            """
            SELECT DISTINCT
                o.id,
                pn.name,
                s.slug AS primary_sport_slug,
                COALESCE(p.primary_municipality_code, ol.municipality_code) AS municipality_code,
                oe.email,
                ow.url AS website
            FROM organizations o
            JOIN organization_sports os ON os.organization_id = o.id
            JOIN sports s ON s.id = os.sport_id
            LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id
            LEFT JOIN organization_profile p ON p.organization_id = o.id
            LEFT JOIN organization_locations ol ON ol.organization_id = o.id AND ol.is_primary = 1
            LEFT JOIN organization_emails oe ON oe.organization_id = o.id AND oe.is_primary = 1
            LEFT JOIN organization_websites ow ON ow.organization_id = o.id AND ow.is_primary = 1
            WHERE s.slug = ?
            ORDER BY pn.name
            """,
            (sport_slug,),
        ).fetchall()
        return [self._row_to_record(row) for row in rows]

    def find_organizations_by_municipality(
        self, municipality_code: str
    ) -> list[OrganizationRecord]:
        """Hae organisaatiot, joilla on toimipaikka annetussa kunnassa."""
        rows = self.execute(
            """
            SELECT DISTINCT
                o.id,
                pn.name,
                ps.slug AS primary_sport_slug,
                ol.municipality_code,
                oe.email,
                ow.url AS website
            FROM organizations o
            JOIN organization_locations ol ON ol.organization_id = o.id
            LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id
            LEFT JOIN organization_sports os ON os.organization_id = o.id AND os.is_primary = 1
            LEFT JOIN sports ps ON ps.id = os.sport_id
            LEFT JOIN organization_emails oe ON oe.organization_id = o.id AND oe.is_primary = 1
            LEFT JOIN organization_websites ow ON ow.organization_id = o.id AND ow.is_primary = 1
            WHERE ol.municipality_code = ?
            ORDER BY pn.name
            """,
            (municipality_code,),
        ).fetchall()
        return [self._row_to_record(row) for row in rows]

    # ------------------------------------------------------------------
    # Profiilin päivitys
    # ------------------------------------------------------------------

    def _refresh_sport_profile(self, organization_id: str) -> None:
        row = self.execute(
            "SELECT COUNT(*) AS cnt FROM organization_sports WHERE organization_id = ?",
            (organization_id,),
        ).fetchone()
        count = int(row["cnt"]) if row else 0
        self.execute(
            """
            UPDATE organization_profile
            SET sport_count = ?, is_multi_sport = ?, profile_updated_at = datetime('now')
            WHERE organization_id = ?
            """,
            (count, int(count > 1), organization_id),
        )

    def _refresh_contact_profile(self, organization_id: str) -> None:
        email_row = self.execute(
            "SELECT COUNT(*) AS cnt FROM organization_emails WHERE organization_id = ?",
            (organization_id,),
        ).fetchone()
        website_row = self.execute(
            "SELECT COUNT(*) AS cnt FROM organization_websites WHERE organization_id = ?",
            (organization_id,),
        ).fetchone()
        email_count = int(email_row["cnt"]) if email_row else 0
        website_count = int(website_row["cnt"]) if website_row else 0
        self.execute(
            """
            UPDATE organization_profile
            SET email_count = ?, has_email = ?,
                website_count = ?, has_website = ?,
                profile_updated_at = datetime('now')
            WHERE organization_id = ?
            """,
            (
                email_count,
                int(email_count > 0),
                website_count,
                int(website_count > 0),
                organization_id,
            ),
        )

    def _refresh_location_profile(self, organization_id: str) -> None:
        count_row = self.execute(
            "SELECT COUNT(*) AS cnt FROM organization_locations WHERE organization_id = ?",
            (organization_id,),
        ).fetchone()
        primary = self.execute(
            """
            SELECT municipality_code, region_code
            FROM organization_locations
            WHERE organization_id = ? AND is_primary = 1
            LIMIT 1
            """,
            (organization_id,),
        ).fetchone()
        count = int(count_row["cnt"]) if count_row else 0
        muni = primary["municipality_code"] if primary else None
        region = primary["region_code"] if primary else None
        self.execute(
            """
            UPDATE organization_profile
            SET location_count = ?,
                primary_municipality_code = ?,
                primary_region_code = ?,
                profile_updated_at = datetime('now')
            WHERE organization_id = ?
            """,
            (count, muni, region, organization_id),
        )

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> OrganizationRecord:
        return OrganizationRecord(
            id=row["id"],
            name=row["name"] or "",
            primary_sport_slug=row["primary_sport_slug"],
            municipality_code=row["municipality_code"],
            email=row["email"],
            website=row["website"],
        )
