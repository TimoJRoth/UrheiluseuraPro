"""CSV- ja JSON-tiedostojen lukeminen."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from urheiluseurapro.collectors.file_import.errors import (
    FileImportNotFoundError,
    FileImportParseError,
    FileImportUnsupportedFormatError,
)
from urheiluseurapro.collectors.file_import.mapping import (
    DEFAULT_FIELD_MAPPING,
    map_row,
    record_to_club_dict,
)

_SUPPORTED_SUFFIXES = {".csv", ".json"}
_EXCEL_SUFFIXES = {".xlsx", ".xls", ".xlsm"}


def load_records(
    path: Path,
    *,
    field_mapping: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Lue CSV- tai JSON-tiedosto ja palauta normalisoidut seuratietueet."""
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileImportNotFoundError(f"Tiedostoa ei löydy: {resolved}", path=resolved)

    suffix = resolved.suffix.lower()
    if suffix in _EXCEL_SUFFIXES:
        raise FileImportUnsupportedFormatError(
            f"Excel-tuonti ({suffix}) tulossa myöhemmin: {resolved}",
            path=resolved,
        )
    if suffix not in _SUPPORTED_SUFFIXES:
        raise FileImportUnsupportedFormatError(
            f"Tuettuja muotoja ovat CSV ja JSON, saatiin {suffix}: {resolved}",
            path=resolved,
        )

    mapping = field_mapping or DEFAULT_FIELD_MAPPING
    raw_rows = _read_csv(resolved) if suffix == ".csv" else _read_json(resolved)

    records: list[dict[str, Any]] = []
    for index, raw_row in enumerate(raw_rows, start=1):
        try:
            canonical = map_row(raw_row, mapping)
            records.append(record_to_club_dict(canonical))
        except ValueError as exc:
            raise FileImportParseError(
                f"Rivi {index} tiedostossa {resolved.name}: {exc}",
                path=resolved,
            ) from exc

    if not records:
        raise FileImportParseError(f"Tiedostosta ei löytynyt seuratietueita: {resolved}", path=resolved)

    return records


def _read_csv(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise FileImportParseError(f"CSV-tiedosto on tyhjä: {path}", path=path)
            return [dict(row) for row in reader]
    except FileImportParseError:
        raise
    except OSError as exc:
        raise FileImportParseError(f"CSV-tiedostoa ei voitu lukea: {path}", path=path) from exc


def _read_json(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FileImportParseError(f"JSON-parsinta epäonnistui: {path}", path=path) from exc
    except OSError as exc:
        raise FileImportParseError(f"JSON-tiedostoa ei voitu lukea: {path}", path=path) from exc

    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        clubs = payload.get("clubs")
        if isinstance(clubs, list):
            rows = clubs
        else:
            raise FileImportParseError(
                f"Odottamaton JSON-rakenne (clubs-listaa ei löytynyt): {path}",
                path=path,
            )
    else:
        raise FileImportParseError(f"Odottamaton JSON-rakenne: {path}", path=path)

    if not all(isinstance(row, dict) for row in rows):
        raise FileImportParseError(f"JSON-rivien pitää olla objekteja: {path}", path=path)

    return rows
