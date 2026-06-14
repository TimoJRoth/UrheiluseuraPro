"""Verkkosivun normalisointi."""

from __future__ import annotations

from urheiluseurapro.normalizers.text import clean_text


def normalize_website(url: str | None) -> str | None:
    text = clean_text(url)
    if not text:
        return None
    if not text.startswith(("http://", "https://")):
        text = f"https://{text}"
    return text.rstrip("/")
