"""Yhteyshenkilökenttien normalisointi."""

from __future__ import annotations

from typing import Any

from urheiluseurapro.models.contact_person import ObservationContactPerson
from urheiluseurapro.normalizers.email import normalize_email
from urheiluseurapro.normalizers.phone import clean_phone_raw, normalize_phone
from urheiluseurapro.normalizers.text import clean_text, clean_text_required


def normalize_contact_person_dict(person: dict[str, Any]) -> dict[str, Any]:
    """Normalisoi yhteyshenkilötietue sanakirjana."""
    full_name = clean_text_required(str(person.get("full_name", "")))

    emails: list[str] = []
    seen_emails: set[str] = set()
    for raw_email in person.get("emails", []):
        email = normalize_email(str(raw_email) if raw_email is not None else None)
        if email and email not in seen_emails:
            seen_emails.add(email)
            emails.append(email)

    phones: list[str] = []
    seen_phones: set[str] = set()
    for raw_phone in person.get("phones", []):
        phone = normalize_phone(str(raw_phone) if raw_phone is not None else None)
        if phone and phone not in seen_phones:
            seen_phones.add(phone)
            phones.append(phone)

    return {
        "full_name": full_name,
        "role": clean_text(person.get("role")),
        "emails": emails,
        "phones": phones,
    }


def normalize_contact_person(person: ObservationContactPerson) -> ObservationContactPerson:
    """Normalisoi ObservationContactPerson."""
    normalized = normalize_contact_person_dict(
        {
            "full_name": person.full_name,
            "role": person.role,
            "emails": person.emails,
            "phones": person.phones,
        }
    )
    return person.model_copy(update=normalized)
