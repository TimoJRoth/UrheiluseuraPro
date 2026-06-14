"""Seuran nimen normalisointi."""

from __future__ import annotations

import re

from urheiluseurapro.normalizers.text import clean_text

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


def normalize_club_name(name: str | None) -> str | None:
    """Normalisoi seuran nimi deduplikointia varten."""
    text = clean_text(name)
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
