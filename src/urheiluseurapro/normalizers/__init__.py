"""Yhteinen normalisointikerros – raakadata yhtenäiseen muotoon."""

from urheiluseurapro.normalizers.business_id import normalize_business_id
from urheiluseurapro.normalizers.contact_person import (
    normalize_contact_person,
    normalize_contact_person_dict,
)
from urheiluseurapro.normalizers.email import normalize_email
from urheiluseurapro.normalizers.municipality import normalize_municipality
from urheiluseurapro.normalizers.name import normalize_club_name
from urheiluseurapro.normalizers.observation import normalize_observation, normalize_observation_fields
from urheiluseurapro.normalizers.phone import clean_phone_raw, normalize_phone
from urheiluseurapro.normalizers.record import normalize_club_record
from urheiluseurapro.normalizers.sports import normalize_sport, normalize_sports
from urheiluseurapro.normalizers.text import clean_text, clean_text_required
from urheiluseurapro.normalizers.website import normalize_website

__all__ = [
    "clean_phone_raw",
    "clean_text",
    "clean_text_required",
    "normalize_business_id",
    "normalize_club_name",
    "normalize_club_record",
    "normalize_contact_person",
    "normalize_contact_person_dict",
    "normalize_email",
    "normalize_municipality",
    "normalize_observation",
    "normalize_observation_fields",
    "normalize_phone",
    "normalize_sport",
    "normalize_sports",
    "normalize_website",
]
