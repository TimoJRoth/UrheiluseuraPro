"""ClubObservation-normalisointi."""

from __future__ import annotations

from urheiluseurapro.models.observation import ClubObservation
from urheiluseurapro.normalizers.contact_person import normalize_contact_person
from urheiluseurapro.normalizers.email import normalize_email
from urheiluseurapro.normalizers.municipality import normalize_municipality
from urheiluseurapro.normalizers.name import normalize_club_name
from urheiluseurapro.normalizers.phone import clean_phone_raw, normalize_phone
from urheiluseurapro.normalizers.sports import normalize_sports
from urheiluseurapro.normalizers.text import clean_text, clean_text_required
from urheiluseurapro.normalizers.website import normalize_website


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
    """Laske normalisoidut kentät raakarvoista."""
    from urheiluseurapro.normalizers.business_id import normalize_business_id

    sports = normalize_sports(sports_raw)
    return {
        "name_normalized": normalize_club_name(name_raw),
        "municipality_normalized": normalize_municipality(municipality_raw),
        "region_normalized": clean_text(region_raw),
        "address_normalized": clean_text(address_raw),
        "business_id_normalized": normalize_business_id(business_id_raw),
        "email_normalized": normalize_email(email_raw),
        "phone_normalized": normalize_phone(phone_raw),
        "website_normalized": normalize_website(website_raw),
        "sports_normalized": sports,
        "primary_sport": sports[0] if sports else None,
    }


def normalize_observation(observation: ClubObservation) -> ClubObservation:
    """
    Normalisoi havainnon raaka- ja normalisoidut kentät yhtenäiseen muotoon.

    Kutsutaan ennen ingest/merge-putkea kaikille collectoreille.
    """
    name_raw = clean_text_required(observation.name_raw)
    municipality_raw = normalize_municipality(observation.municipality_raw)
    sports_raw = normalize_sports(observation.sports_raw)
    email_raw = normalize_email(observation.email_raw)
    phone_raw = clean_phone_raw(observation.phone_raw)
    website_raw = normalize_website(observation.website_raw)
    address_raw = clean_text(observation.address_raw)
    region_raw = clean_text(observation.region_raw)
    business_id_raw = clean_text(observation.business_id_raw)

    contact_persons = [normalize_contact_person(person) for person in observation.contact_persons]

    normalized_fields = normalize_observation_fields(
        name_raw=name_raw,
        municipality_raw=municipality_raw,
        business_id_raw=business_id_raw,
        email_raw=email_raw,
        phone_raw=phone_raw,
        website_raw=website_raw,
        sports_raw=sports_raw,
        region_raw=region_raw,
        address_raw=address_raw,
    )

    legacy_contact_name = contact_persons[0].full_name if contact_persons else None
    legacy_contact_role = contact_persons[0].role if contact_persons else None
    legacy_contact_email = contact_persons[0].emails[0] if contact_persons and contact_persons[0].emails else None
    legacy_contact_phone = contact_persons[0].phones[0] if contact_persons and contact_persons[0].phones else None

    return observation.model_copy(
        update={
            "name_raw": name_raw,
            "municipality_raw": municipality_raw,
            "sports_raw": sports_raw,
            "email_raw": email_raw,
            "phone_raw": phone_raw,
            "website_raw": website_raw,
            "address_raw": address_raw,
            "region_raw": region_raw,
            "business_id_raw": business_id_raw,
            "contact_persons": contact_persons,
            "contact_person_name": legacy_contact_name,
            "contact_person_role": legacy_contact_role,
            "contact_person_email": legacy_contact_email,
            "contact_person_phone": legacy_contact_phone,
            **normalized_fields,
        }
    )
