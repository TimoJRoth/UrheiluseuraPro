"""Merge-engine – tuotantotason provenance- ja master-valintatestit."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from urheiluseurapro.merge.engine import (
    get_field_observations,
    merge_observation_into_club,
    observation_to_club,
)
from urheiluseurapro.merge.priorities import resolve_source_priority
from urheiluseurapro.models.enums import SourceCategory
from urheiluseurapro.models.observation import ClubObservation
from urheiluseurapro.models.source import Source


def _obs(
    *,
    source_id: str,
    email_raw: str | None = None,
    phone_raw: str | None = None,
    website_raw: str | None = None,
    municipality_raw: str | None = "Tampere",
    collected_at: datetime | None = None,
    name_raw: str = "Ilves ry",
) -> ClubObservation:
    return ClubObservation(
        observation_id=str(uuid4()),
        source_id=source_id,
        source_record_key=f"{source_id}-rec-1",
        source_url=f"https://{source_id}.example.fi/club/1",
        name_raw=name_raw,
        municipality_raw=municipality_raw,
        email_raw=email_raw,
        phone_raw=phone_raw,
        website_raw=website_raw,
        sports_raw=["jääkiekko"],
        collected_at=collected_at or datetime(2024, 6, 1, tzinfo=timezone.utc),
    )


def _source(source_id: str, category: SourceCategory) -> Source:
    return Source(
        source_id=source_id,
        name=source_id,
        category=category,
        geographic_coverage="Test",
    )


SOURCES = {
    "club-website": _source("club-website", SourceCategory.OTHER),
    "suomisport": _source("suomisport", SourceCategory.NATIONAL),
    "kunta-tampere": _source("kunta-tampere", SourceCategory.MUNICIPALITY),
    "kunta-helsinki": _source("kunta-helsinki", SourceCategory.MUNICIPALITY),
    "palloliitto": _source("palloliitto", SourceCategory.FEDERATION),
    "prh": _source("prh", SourceCategory.REGISTRY),
}


def test_source_priority_order() -> None:
    assert resolve_source_priority(SOURCES["club-website"], "club-website") == 100
    assert resolve_source_priority(SOURCES["suomisport"], "suomisport") == 90
    assert resolve_source_priority(SOURCES["palloliitto"], "palloliitto") == 80
    assert resolve_source_priority(SOURCES["kunta-tampere"], "kunta-tampere") == 70
    assert resolve_source_priority(SOURCES["prh"], "prh") == 65


def test_same_club_from_two_sources() -> None:
    obs1 = _obs(source_id="suomisport", email_raw="info@ilves.fi")
    club = observation_to_club(obs1, sources=SOURCES)

    obs2 = _obs(
        source_id="kunta-tampere",
        email_raw="yhteystiedot@tampere.fi",
        collected_at=datetime(2024, 7, 1, tzinfo=timezone.utc),
    )
    merged = merge_observation_into_club(club, obs2, SOURCES["kunta-tampere"], sources=SOURCES)

    assert merged.quality.source_count == 2
    assert len(merged.source_links) == 2
    email_observations = get_field_observations(merged, "email")
    assert len(email_observations) == 2
    assert {o.source_id for o in email_observations} == {"suomisport", "kunta-tampere"}


def test_conflicting_emails_higher_priority_wins() -> None:
    club = observation_to_club(
        _obs(source_id="kunta-tampere", email_raw="kunta@ilves.fi"),
        sources=SOURCES,
    )
    merged = merge_observation_into_club(
        club,
        _obs(source_id="suomisport", email_raw="info@ilves.fi"),
        SOURCES["suomisport"],
        sources=SOURCES,
    )

    assert merged.contact.email == "info@ilves.fi"
    master = merged.master_values["email"]
    assert master.primary_source_id == "suomisport"
    assert "suomisport" in master.supporting_sources
    assert master.has_conflict is True
    assert "kunta@ilves.fi" in master.conflicting_values
    assert merged.quality.needs_review is True


def test_newer_observation_wins_when_equal_priority() -> None:
    older = datetime(2023, 1, 15, tzinfo=timezone.utc)
    newer = datetime(2025, 3, 20, tzinfo=timezone.utc)

    club = observation_to_club(
        _obs(
            source_id="kunta-tampere",
            email_raw="vanha@ilves.fi",
            collected_at=older,
        ),
        sources=SOURCES,
    )
    merged = merge_observation_into_club(
        club,
        _obs(
            source_id="kunta-helsinki",
            email_raw="uusi@ilves.fi",
            collected_at=newer,
        ),
        SOURCES["kunta-helsinki"],
        sources=SOURCES,
    )

    assert merged.contact.email == "uusi@ilves.fi"
    assert merged.master_values["email"].primary_source_id == "kunta-helsinki"


def test_official_source_beats_weaker_source() -> None:
    club = observation_to_club(
        _obs(source_id="kunta-tampere", website_raw="https://tampere.fi/ilves"),
        sources=SOURCES,
    )
    merged = merge_observation_into_club(
        club,
        _obs(source_id="club-website", website_raw="https://ilves.fi"),
        SOURCES["club-website"],
        sources=SOURCES,
    )

    assert merged.contact.website == "https://ilves.fi"
    assert merged.master_values["website"].primary_source_id == "club-website"
    assert resolve_source_priority(SOURCES["club-website"], "club-website") > resolve_source_priority(
        SOURCES["kunta-tampere"], "kunta-tampere"
    )


def test_all_observations_preserved_after_multiple_merges() -> None:
    club = observation_to_club(_obs(source_id="suomisport", email_raw="a@ilves.fi"), sources=SOURCES)
    count_after_first = len(club.field_observations)

    club = merge_observation_into_club(
        club,
        _obs(source_id="kunta-tampere", email_raw="b@ilves.fi", phone_raw="+358 40 111 1111"),
        SOURCES["kunta-tampere"],
        sources=SOURCES,
    )
    club = merge_observation_into_club(
        club,
        _obs(source_id="palloliitto", email_raw="c@ilves.fi", phone_raw="+358 40 222 2222"),
        SOURCES["palloliitto"],
        sources=SOURCES,
    )

    assert len(club.field_observations) > count_after_first
    assert len(get_field_observations(club, "email")) == 3
    assert len(get_field_observations(club, "phone")) == 2
    assert len({o.observation_id for o in club.field_observations}) == 3


def test_master_updates_without_losing_history() -> None:
    club = observation_to_club(
        _obs(source_id="prh", email_raw="registry@ilves.fi"),
        sources=SOURCES,
    )
    first_email_obs_id = get_field_observations(club, "email")[0].id

    merged = merge_observation_into_club(
        club,
        _obs(source_id="suomisport", email_raw="master@ilves.fi"),
        SOURCES["suomisport"],
        sources=SOURCES,
    )

    assert merged.contact.email == "master@ilves.fi"
    email_obs_ids = {o.id for o in get_field_observations(merged, "email")}
    assert first_email_obs_id in email_obs_ids
    assert merged.quality.merge_version == 2


def test_field_observation_contains_provenance_metadata() -> None:
    obs = _obs(source_id="suomisport", email_raw="info@ilves.fi")
    club = observation_to_club(obs, sources=SOURCES)
    record = get_field_observations(club, "email")[0]

    assert record.source_id == "suomisport"
    assert record.observation_id == obs.observation_id
    assert record.field_name == "email"
    assert record.value == "info@ilves.fi"
    assert record.source_record_key == "suomisport-rec-1"
    assert record.source_url == "https://suomisport.example.fi/club/1"
    assert record.observed_at == obs.collected_at


def test_duplicate_observation_not_appended_twice() -> None:
    obs = _obs(source_id="suomisport", email_raw="info@ilves.fi")
    club = observation_to_club(obs, sources=SOURCES)
    before = len(club.field_observations)

    merged = merge_observation_into_club(club, obs, SOURCES["suomisport"], sources=SOURCES)
    assert len(merged.field_observations) == before


def test_supporting_sources_when_sources_agree() -> None:
    same_email = "info@ilves.fi"
    club = observation_to_club(
        _obs(source_id="suomisport", email_raw=same_email),
        sources=SOURCES,
    )
    merged = merge_observation_into_club(
        club,
        _obs(
            source_id="club-website",
            email_raw=same_email,
            collected_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        ),
        SOURCES["club-website"],
        sources=SOURCES,
    )

    master = merged.master_values["email"]
    assert set(master.supporting_sources) == {"suomisport", "club-website"}
    assert master.has_conflict is False
    assert master.confidence_score > 0.5
