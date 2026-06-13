"""SQLite-repository – dummy-datatestit."""

from __future__ import annotations

import pytest

from urheiluseurapro.db.repository import SQLiteRepository


@pytest.fixture
def repo() -> SQLiteRepository:
    db = SQLiteRepository.connect(":memory:")
    db.init_schema()
    db.ensure_region("11", "Pirkanmaa")
    db.ensure_municipality("837", "Tampere", "11")
    db.ensure_region("18", "Uusimaa")
    db.ensure_municipality("091", "Helsinki", "18")
    yield db
    db.close()


def test_init_schema_creates_tables(repo: SQLiteRepository) -> None:
    row = repo.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='organizations'"
    ).fetchone()
    assert row is not None


def test_add_organization_and_sport(repo: SQLiteRepository) -> None:
    org_id = repo.add_organization("Tampereen Jääkiekkoseura")
    sport_id = repo.add_sport("jaakiekko", "Jääkiekko")
    repo.link_organization_sport(org_id, sport_id, is_primary=True)

    profile = repo.execute(
        "SELECT sport_count, is_multi_sport FROM organization_profile WHERE organization_id = ?",
        (org_id,),
    ).fetchone()
    assert profile is not None
    assert profile["sport_count"] == 1
    assert profile["is_multi_sport"] == 0


def test_add_email_and_website(repo: SQLiteRepository) -> None:
    org_id = repo.add_organization("Testiseura")
    repo.add_email(org_id, "info@testiseura.fi", is_primary=True)
    repo.add_website(org_id, "https://testiseura.fi", is_primary=True)

    profile = repo.execute(
        """
        SELECT has_email, has_website, email_count, website_count
        FROM organization_profile WHERE organization_id = ?
        """,
        (org_id,),
    ).fetchone()
    assert profile is not None
    assert profile["has_email"] == 1
    assert profile["has_website"] == 1
    assert profile["email_count"] == 1
    assert profile["website_count"] == 1


def test_find_by_sport(repo: SQLiteRepository) -> None:
    jaakiekko_id = repo.add_sport("jaakiekko", "Jääkiekko")
    salibandy_id = repo.add_sport("salibandy", "Salibandy")

    tpv = repo.add_organization("Tampereen Pallo-Veikot")
    repo.link_organization_sport(tpv, repo.add_sport("jalkapallo", "Jalkapallo"), is_primary=True)
    repo.add_location(tpv, municipality_code="837", is_primary=True)

    ilves = repo.add_organization("Ilves ry")
    repo.link_organization_sport(ilves, jaakiekko_id, is_primary=True)
    repo.add_location(ilves, municipality_code="837", is_primary=True)

    viiri = repo.add_organization("Viiri Salibandy")
    repo.link_organization_sport(viiri, salibandy_id, is_primary=True)
    repo.add_location(viiri, municipality_code="091", is_primary=True)

    hockey_clubs = repo.find_organizations_by_sport("jaakiekko")
    assert len(hockey_clubs) == 1
    assert hockey_clubs[0].name == "Ilves ry"
    assert hockey_clubs[0].primary_sport_slug == "jaakiekko"


def test_find_by_municipality(repo: SQLiteRepository) -> None:
    sport_id = repo.add_sport("jaakiekko", "Jääkiekko")

    ilves = repo.add_organization("Ilves ry")
    repo.link_organization_sport(ilves, sport_id, is_primary=True)
    repo.add_location(ilves, municipality_code="837", is_primary=True)
    repo.add_email(ilves, "ilves@example.fi", is_primary=True)

    hifk = repo.add_organization("HIFK")
    repo.link_organization_sport(hifk, sport_id, is_primary=True)
    repo.add_location(hifk, municipality_code="091", is_primary=True)

    tampere_clubs = repo.find_organizations_by_municipality("837")
    assert len(tampere_clubs) == 1
    assert tampere_clubs[0].name == "Ilves ry"
    assert tampere_clubs[0].municipality_code == "837"
    assert tampere_clubs[0].email == "ilves@example.fi"


def test_multi_sport_updates_profile(repo: SQLiteRepository) -> None:
    org_id = repo.add_organization("Monitoimiseura")
    s1 = repo.add_sport("jalkapallo", "Jalkapallo")
    s2 = repo.add_sport("jaakiekko", "Jääkiekko")
    repo.link_organization_sport(org_id, s1, is_primary=True)
    repo.link_organization_sport(org_id, s2)

    profile = repo.execute(
        "SELECT sport_count, is_multi_sport FROM organization_profile WHERE organization_id = ?",
        (org_id,),
    ).fetchone()
    assert profile is not None
    assert profile["sport_count"] == 2
    assert profile["is_multi_sport"] == 1


def test_context_manager() -> None:
    with SQLiteRepository.connect(":memory:") as db:
        db.init_schema()
        org_id = db.add_organization("Ctx Seura")
        assert org_id
