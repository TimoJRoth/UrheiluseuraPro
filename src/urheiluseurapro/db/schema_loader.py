"""SQLite-tietokanta: skeeman lataus."""

from __future__ import annotations

from pathlib import Path

from urheiluseurapro.config import project_root


def schema_sql_path() -> Path:
    return project_root() / "db" / "schema.sql"


def seed_sql_path() -> Path:
    return project_root() / "db" / "seed" / "reference.sql"


def load_sql(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"SQL-tiedostoa ei löydy: {path}")
    return path.read_text(encoding="utf-8")
