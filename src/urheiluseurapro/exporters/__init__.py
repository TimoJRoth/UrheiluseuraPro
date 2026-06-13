"""Tulosten vienti eri formaatteihin."""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from urheiluseurapro.models.club import Club


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def export_csv(clubs: list[Club], output_dir: Path, prefix: str = "clubs") -> Path:
    """Vie seurat CSV-tiedostoon."""
    if not clubs:
        raise ValueError("Ei vietäviä tietueita")

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{prefix}_{_timestamp()}.csv"

    rows = [club.to_export_row() for club in clubs]
    fieldnames = list(rows[0].keys())

    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return path


def export_json(clubs: list[Club], output_dir: Path, prefix: str = "clubs") -> Path:
    """Vie seurat JSON-tiedostoon."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{prefix}_{_timestamp()}.json"

    payload = [club.to_export_row() for club in clubs]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return path
