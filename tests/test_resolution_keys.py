"""Entity resolution -avainten testit."""

from __future__ import annotations

from urheiluseurapro.resolution.keys import club_match_keys, normalize_org_name_for_matching


def test_normalize_org_name_same_club_different_spelling() -> None:
    a = normalize_org_name_for_matching("  Ilves Urheiluseura RY  ")
    b = normalize_org_name_for_matching("ilves urheiluseura r.y.")
    c = normalize_org_name_for_matching("Ilves Urheiluseura Rekisteröity Yhdistys")

    assert a == "ilves urheiluseura"
    assert b == "ilves urheiluseura"
    assert c == "ilves urheiluseura"


def test_club_match_keys_email() -> None:
    keys = club_match_keys({"email": "  INFO@Example.COM  "})
    assert keys == ["email:info@example.com"]


def test_club_match_keys_website_domain() -> None:
    keys = club_match_keys({"website": "https://WWW.Example.Invalid/club/"})
    assert keys == ["website:example.invalid"]


def test_club_match_keys_phone() -> None:
    keys = club_match_keys({"phone": "+358 (40) 123 4567"})
    assert keys == ["phone:+358401234567"]


def test_club_match_keys_name_municipality() -> None:
    keys = club_match_keys(
        {
            "name": "Esimerkki Urheiluseura ry",
            "municipality": "  tampere ",
        }
    )
    assert "name_municipality:esimerkki urheiluseura|tampere" in keys


def test_club_match_keys_empty_values_create_no_keys() -> None:
    assert club_match_keys({}) == []
    assert club_match_keys({"email": "", "phone": "   ", "name": "Seura"}) == []


def test_club_match_keys_combined() -> None:
    record = {
        "name": "Test Seura ry",
        "municipality": "Oulu",
        "email": "info@test.example",
        "website": "example.invalid",
        "phone": "0401234567",
    }
    keys = club_match_keys(record)

    assert keys == sorted(
        {
            "email:info@test.example",
            "website:example.invalid",
            "phone:+358401234567",
            "name_municipality:test seura|oulu",
        }
    )


def test_club_match_keys_supports_observation_field_names() -> None:
    keys = club_match_keys(
        {
            "name_raw": "Ilves ry",
            "municipality_raw": "Tampere",
            "email_normalized": "info@ilves.example",
        }
    )

    assert "email:info@ilves.example" in keys
    assert "name_municipality:ilves|tampere" in keys
