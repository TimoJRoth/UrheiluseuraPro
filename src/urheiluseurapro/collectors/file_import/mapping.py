"""Kenttämappaus tiedostotuontia varten."""

from __future__ import annotations

from typing import Any

CANONICAL_FIELDS = frozenset(
    {
        "name",
        "municipality",
        "sports",
        "website",
        "email",
        "phone",
        "address",
        "contact_person_name",
        "contact_person_role",
        "contact_person_email",
        "contact_person_phone",
    }
)

DEFAULT_FIELD_MAPPING: dict[str, str] = {field: field for field in CANONICAL_FIELDS}


def parse_sports(value: Any) -> list[str]:
    """Muunna sports-kenttä listaksi (merkkijono, pilkku-/puolipiste-eroteltu tai lista)."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    separator = ";" if ";" in text else "," if "," in text else None
    if separator:
        return [part.strip() for part in text.split(separator) if part.strip()]
    return [text]


def map_row(raw_row: dict[str, Any], field_mapping: dict[str, str]) -> dict[str, Any]:
    """
    Muunna tiedostorivi kanoniseen muotoon.

    field_mapping: lähtesarakkeen nimi → kanoninen kenttänimi.
    """
    canonical: dict[str, Any] = {}
    for source_column, value in raw_row.items():
        if source_column is None:
            continue
        key = str(source_column).strip()
        if not key:
            continue
        target = field_mapping.get(key, key)
        if target in CANONICAL_FIELDS:
            canonical[target] = value
    return canonical


def record_to_club_dict(canonical: dict[str, Any]) -> dict[str, Any]:
    """Muunna kanoninen rivi collector-record-muotoon."""
    name = canonical.get("name")
    if name is None or not str(name).strip():
        raise ValueError("Riviltä puuttuu pakollinen kenttä: name")

    contact_persons: list[dict[str, Any]] = []
    person_name = canonical.get("contact_person_name")
    if person_name and str(person_name).strip():
        emails: list[str] = []
        email = canonical.get("contact_person_email")
        if email and str(email).strip():
            emails.append(str(email).strip())
        phones: list[str] = []
        phone = canonical.get("contact_person_phone")
        if phone and str(phone).strip():
            phones.append(str(phone).strip())
        contact_persons.append(
            {
                "full_name": str(person_name).strip(),
                "role": _optional_str(canonical.get("contact_person_role")),
                "emails": emails,
                "phones": phones,
            }
        )

    return {
        "name": str(name).strip(),
        "municipality": _optional_str(canonical.get("municipality")),
        "sports": parse_sports(canonical.get("sports")),
        "website": _optional_str(canonical.get("website")),
        "email": _optional_str(canonical.get("email")),
        "phone": _optional_str(canonical.get("phone")),
        "address": _optional_str(canonical.get("address")),
        "contact_persons": contact_persons,
    }


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
