"""Y-tunnuksen normalisointi."""

from __future__ import annotations

import re

from urheiluseurapro.normalizers.text import clean_text


def normalize_business_id(business_id: str | None) -> str | None:
    text = clean_text(business_id)
    if not text:
        return None
    digits = re.sub(r"\D", "", text)
    if len(digits) != 9:
        return None
    return f"{digits[:7]}-{digits[7:]}"
