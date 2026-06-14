"""Tekstin siivous."""

from __future__ import annotations

import re
import unicodedata


def clean_text(value: str | None) -> str | None:
    """Trim, ylimääräiset välilyönnit pois, tyhjä → None."""
    if value is None:
        return None
    text = unicodedata.normalize("NFKC", str(value).strip())
    text = re.sub(r"\s+", " ", text)
    return text or None


def clean_text_required(value: str) -> str:
    """Pakollinen tekstikenttä – ei saa palauttaa tyhjää."""
    cleaned = clean_text(value)
    if cleaned is None:
        raise ValueError("Tekstikenttä ei voi olla tyhjä")
    return cleaned
