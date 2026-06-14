"""Puhelinnumeron normalisointi."""

from __future__ import annotations

import re

from urheiluseurapro.normalizers.text import clean_text


def clean_phone_raw(phone: str | None) -> str | None:
    """Siivoa raakapuhelin välilyönneistä ja yleisistä erikoismerkeistä."""
    text = clean_text(phone)
    if not text:
        return None
    cleaned = re.sub(r"[\s\-()./]", "", text)
    return cleaned or None


def normalize_phone(phone: str | None) -> str | None:
    """Normalisoi puhelin E.164-tyyliseen +358-muotoon."""
    text = clean_phone_raw(phone)
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
