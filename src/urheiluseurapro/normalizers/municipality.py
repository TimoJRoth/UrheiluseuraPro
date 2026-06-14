"""Kuntanimen normalisointi."""

from __future__ import annotations

from urheiluseurapro.normalizers.text import clean_text

_MUNICIPALITY_ALIASES: dict[str, str] = {
    "helsinki": "Helsinki",
    "tampere": "Tampere",
    "espoo": "Espoo",
    "vantaa": "Vantaa",
    "turku": "Turku",
    "oulu": "Oulu",
}


def normalize_municipality(municipality: str | None) -> str | None:
    text = clean_text(municipality)
    if not text:
        return None
    key = text.lower()
    return _MUNICIPALITY_ALIASES.get(key, text.title())
