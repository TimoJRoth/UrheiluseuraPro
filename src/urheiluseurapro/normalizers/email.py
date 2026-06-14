"""Sähköpostin normalisointi."""

from __future__ import annotations

from urheiluseurapro.normalizers.text import clean_text


def normalize_email(email: str | None) -> str | None:
    text = clean_text(email)
    if not text:
        return None
    return text.lower()
