"""Seuratietueen normalisointi (dict-muoto ennen CollectorResultia)."""

from __future__ import annotations

from typing import Any

from urheiluseurapro.normalizers.contact_person import normalize_contact_person_dict
from urheiluseurapro.normalizers.email import normalize_email
from urheiluseurapro.normalizers.municipality import normalize_municipality
from urheiluseurapro.normalizers.phone import clean_phone_raw
from urheiluseurapro.normalizers.sports import normalize_sports
from urheiluseurapro.normalizers.text import clean_text, clean_text_required
from urheiluseurapro.normalizers.website import normalize_website


def normalize_club_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalisoi kerääjän raakatietue yhtenäiseen muotoon."""
    name = clean_text_required(str(record.get("name", "")))
    sports = normalize_sports(record.get("sports"))

    contact_persons = [
        normalize_contact_person_dict(person)
        for person in record.get("contact_persons", [])
        if isinstance(person, dict)
    ]

    email = normalize_email(record.get("email"))
    phone = clean_phone_raw(record.get("phone"))
    website = normalize_website(record.get("website"))
    municipality = normalize_municipality(record.get("municipality"))

    return {
        "name": name,
        "municipality": municipality,
        "sports": sports,
        "website": website,
        "email": email,
        "phone": phone,
        "address": clean_text(record.get("address")),
        "contact_persons": contact_persons,
    }
