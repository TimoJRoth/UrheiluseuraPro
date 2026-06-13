"""Normalisointifunktiot: raakadata → yhtenäiset kentät."""

from __future__ import annotations

import re
import unicodedata

_NAME_PREFIXES = (
    "seura",
    "urheiluseura",
    "liikuntaseura",
    "ry",
    "rf",
    "sr",
)
_NAME_SUFFIXES = (
    " ry",
    " rf",
    " sr",
    " r.y.",
    " r.f.",
    " r.s.",
    " seura",
    " urheiluseura",
    " liikuntaseura",
)

_MUNICIPALITY_ALIASES: dict[str, str] = {
    "helsinki": "Helsinki",
    "tampere": "Tampere",
    "espoo": "Espoo",
    "vantaa": "Vantaa",
    "turku": "Turku",
    "oulu": "Oulu",
}


def normalize_text(value: str | None) -> str | None:
    if not value:
        return None
    text = unicodedata.normalize("NFKC", value.strip())
    text = re.sub(r"\s+", " ", text)
    return text or None


def normalize_club_name(name: str | None) -> str | None:
    text = normalize_text(name)
    if not text:
        return None

    lowered = text.lower()

    for suffix in _NAME_SUFFIXES:
        if lowered.endswith(suffix):
            lowered = lowered[: -len(suffix)].strip()

    for prefix in _NAME_PREFIXES:
        if lowered.startswith(prefix + " "):
            lowered = lowered[len(prefix) + 1 :]

    lowered = re.sub(r"[^\w\s]", "", lowered, flags=re.UNICODE)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered or None


def normalize_municipality(municipality: str | None) -> str | None:
    text = normalize_text(municipality)
    if not text:
        return None
    key = text.lower()
    return _MUNICIPALITY_ALIASES.get(key, text.title())


def normalize_business_id(business_id: str | None) -> str | None:
    text = normalize_text(business_id)
    if not text:
        return None
    digits = re.sub(r"\D", "", text)
    if len(digits) != 9:
        return None
    return f"{digits[:7]}-{digits[7:]}"


def normalize_email(email: str | None) -> str | None:
    text = normalize_text(email)
    if not text:
        return None
    return text.lower()


def normalize_phone(phone: str | None) -> str | None:
    text = normalize_text(phone)
    if not text:
        return None
    digits = re.sub(r"\D", "", text)
    if digits.startswith("358"):
        digits = digits[3:]
    if digits.startswith("0"):
        digits = digits[1:]
    if len(digits) < 6:
        return None
    return f"+358{digits}"


def normalize_website(url: str | None) -> str | None:
    text = normalize_text(url)
    if not text:
        return None
    if not text.startswith(("http://", "https://")):
        text = f"https://{text}"
    return text.rstrip("/").lower()


def normalize_sport(sport: str | None) -> str | None:
    text = normalize_text(sport)
    if not text:
        return None
    return text.lower()


def normalize_observation_fields(
    *,
    name_raw: str | None = None,
    municipality_raw: str | None = None,
    business_id_raw: str | None = None,
    email_raw: str | None = None,
    phone_raw: str | None = None,
    website_raw: str | None = None,
    sports_raw: list[str] | None = None,
    region_raw: str | None = None,
    address_raw: str | None = None,
) -> dict[str, str | list[str] | None]:
    sports = sports_raw or []
    return {
        "name_normalized": normalize_club_name(name_raw),
        "municipality_normalized": normalize_municipality(municipality_raw),
        "region_normalized": normalize_text(region_raw),
        "address_normalized": normalize_text(address_raw),
        "business_id_normalized": normalize_business_id(business_id_raw),
        "email_normalized": normalize_email(email_raw),
        "phone_normalized": normalize_phone(phone_raw),
        "website_normalized": normalize_website(website_raw),
        "sports_normalized": [s for s in (normalize_sport(x) for x in sports) if s],
    }
