"""Lajien normalisointi."""

from __future__ import annotations

from typing import Any

from urheiluseurapro.normalizers.text import clean_text


def normalize_sport(sport: str | None) -> str | None:
    text = clean_text(sport)
    if not text:
        return None
    return text.lower()


def normalize_sports(value: str | list[str] | None) -> list[str]:
    """
    Normalisoi lajit listaksi.

    Hyväksyy merkkijonon (pilkku-/puolipiste-eroteltu) tai listan.
    """
    if value is None:
        return []

    items: list[str]
    if isinstance(value, list):
        items = [str(item) for item in value]
    else:
        text = str(value).strip()
        if not text:
            return []
        separator = ";" if ";" in text else "," if "," in text else None
        items = text.split(separator) if separator else [text]

    normalized: list[str] = []
    seen: set[str] = set()
    for item in items:
        sport = normalize_sport(item)
        if sport and sport not in seen:
            seen.add(sport)
            normalized.append(sport)
    return normalized
