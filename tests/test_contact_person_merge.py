"""Yhteyshenkilöiden merge-testit."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from urheiluseurapro.merge.engine import merge_observation_into_club, observation_to_club
from urheiluseurapro.merge.contact_persons import get_contact_person_observations
from urheiluseurapro.models.contact_person import ObservationContactPerson
from urheiluseurapro.models.enums import ContactPersonRole, SourceCategory
from urheiluseurapro.models.observation import ClubObservation
from urheiluseurapro.models.source import Source


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
    "palloliitto": _source("palloliitto", SourceCategory.FEDERATION),
}


def _obs(
    *,
    source_id: str,
    contact_persons: list[ObservationContactPerson] | None = None,
    collected_at: datetime | None = None,
    name_raw: str = "Ilves ry",
) -> ClubObservation:
    return ClubObservation(
        observation_id=str(uuid4()),
        source_id=source_id,
        source_record_key=f"{source_id}-rec-1",
        source_url=f"https://{source_id}.example.fi/club/1",
        name_raw=name_raw,
        municipality_raw="Tampere",
        sports_raw=["jääkiekko"],
        contact_persons=contact_persons or [],
        collected_at=collected_at or datetime(2024, 6, 1, tzinfo=timezone.utc),
    )


def _person(
    name: str,
    role: str,
    *,
    emails: list[str] | None = None,
    phones: list[str] | None = None,
) -> ObservationContactPerson:
    return ObservationContactPerson(
        full_name=name,
        role=role,
        emails=emails or [],
        phones=phones or [],
    )


def test_single_contact_person() -> None:
    obs = _obs(
        source_id="suomisport",
        contact_persons=[
            _person("Maija Meikäläinen", "sihteeri", emails=["maija@ilves.fi"])
        ],
    )
    club = observation_to_club(obs, sources=SOURCES)

    assert len(club.contact_person_observations) == 1
    assert club.master_contact_persons["sihteeri"].full_name == "Maija Meikäläinen"
    assert club.contact_person.name == "Maija Meikäläinen"
    assert club.contact_person.email == "maija@ilves.fi"


def test_same_contact_person_from_two_sources() -> None:
    club = observation_to_club(
        _obs(
            source_id="kunta-tampere",
            contact_persons=[
                _person("Maija Meikäläinen", "sihteeri", emails=["maija@ilves.fi"])
            ],
        ),
        sources=SOURCES,
    )
    merged = merge_observation_into_club(
        club,
        _obs(
            source_id="suomisport",
            contact_persons=[
                _person("Maija Meikäläinen", "sihteeri", emails=["maija@ilves.fi"])
            ],
        ),
        SOURCES["suomisport"],
        sources=SOURCES,
    )

    secretary_obs = get_contact_person_observations(merged, role="sihteeri")
    assert len(secretary_obs) == 2
    master = merged.master_contact_persons["sihteeri"]
    assert master.full_name == "Maija Meikäläinen"
    assert set(master.supporting_sources) == {"kunta-tampere", "suomisport"}
    assert master.has_conflict is False


def test_same_role_different_person_different_sources() -> None:
    club = observation_to_club(
        _obs(
            source_id="kunta-tampere",
            contact_persons=[_person("Maija Meikäläinen", "sihteeri")],
        ),
        sources=SOURCES,
    )
    merged = merge_observation_into_club(
        club,
        _obs(
            source_id="suomisport",
            contact_persons=[_person("Pekka Pulkkinen", "sihteeri")],
        ),
        SOURCES["suomisport"],
        sources=SOURCES,
    )

    assert len(get_contact_person_observations(merged, role="sihteeri")) == 2
    master = merged.master_contact_persons["sihteeri"]
    assert master.full_name == "Pekka Pulkkinen"
    assert master.primary_source_id == "suomisport"
    assert master.has_conflict is True
    assert "Maija Meikäläinen" in master.conflicting_names


def test_contact_person_email_changes() -> None:
    club = observation_to_club(
        _obs(
            source_id="kunta-tampere",
            contact_persons=[
                _person("Maija Meikäläinen", "sihteeri", emails=["vanha@ilves.fi"])
            ],
            collected_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        ),
        sources=SOURCES,
    )
    merged = merge_observation_into_club(
        club,
        _obs(
            source_id="kunta-tampere",
            contact_persons=[
                _person("Maija Meikäläinen", "sihteeri", emails=["uusi@ilves.fi"])
            ],
            collected_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        ),
        SOURCES["kunta-tampere"],
        sources=SOURCES,
    )

    observations = get_contact_person_observations(merged, role="sihteeri")
    assert len(observations) == 2
    emails = {email for obs in observations for email in obs.emails}
    assert emails == {"vanha@ilves.fi", "uusi@ilves.fi"}
    assert merged.master_contact_persons["sihteeri"].emails == ["uusi@ilves.fi"]


def test_contact_person_phone_changes() -> None:
    club = observation_to_club(
        _obs(
            source_id="palloliitto",
            contact_persons=[
                _person(
                    "Maija Meikäläinen",
                    "puheenjohtaja",
                    phones=["+358 40 111 1111"],
                )
            ],
            collected_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
        ),
        sources=SOURCES,
    )
    merged = merge_observation_into_club(
        club,
        _obs(
            source_id="club-website",
            contact_persons=[
                _person(
                    "Maija Meikäläinen",
                    "puheenjohtaja",
                    phones=["+358 50 222 2222"],
                )
            ],
            collected_at=datetime(2025, 6, 1, tzinfo=timezone.utc),
        ),
        SOURCES["club-website"],
        sources=SOURCES,
    )

    observations = get_contact_person_observations(merged, role="puheenjohtaja")
    assert len(observations) == 2
    phones = {phone for obs in observations for phone in obs.phones}
    assert "+358401111111" in phones
    assert "+358502222222" in phones
    master = merged.master_contact_persons["puheenjohtaja"]
    assert master.primary_source_id == "club-website"
    assert master.phones == ["+358502222222"]


def test_all_contact_person_observations_preserved() -> None:
    club = observation_to_club(
        _obs(
            source_id="suomisport",
            contact_persons=[
                _person("Maija Meikäläinen", "sihteeri"),
                _person("Pekka Pulkkinen", "puheenjohtaja"),
            ],
        ),
        sources=SOURCES,
    )
    before = len(club.contact_person_observations)

    club = merge_observation_into_club(
        club,
        _obs(
            source_id="kunta-tampere",
            contact_persons=[
                _person("Liisa Laaksonen", "rahastonhoitaja"),
            ],
        ),
        SOURCES["kunta-tampere"],
        sources=SOURCES,
    )
    club = merge_observation_into_club(
        club,
        _obs(
            source_id="palloliitto",
            contact_persons=[
                _person("Matti Muu", "valmennuspäällikkö"),
            ],
        ),
        SOURCES["palloliitto"],
        sources=SOURCES,
    )

    assert len(club.contact_person_observations) == before + 2
    assert len(club.master_contact_persons) == 4


def test_master_contact_person_selected_by_priority() -> None:
    club = observation_to_club(
        _obs(
            source_id="kunta-tampere",
            contact_persons=[
                _person(
                    "Kunta Kontakti",
                    ContactPersonRole.CONTACT.value,
                    emails=["kunta@ilves.fi"],
                )
            ],
        ),
        sources=SOURCES,
    )
    merged = merge_observation_into_club(
        club,
        _obs(
            source_id="club-website",
            contact_persons=[
                _person(
                    "Virallinen Kontakti",
                    ContactPersonRole.CONTACT.value,
                    emails=["info@ilves.fi"],
                )
            ],
        ),
        SOURCES["club-website"],
        sources=SOURCES,
    )

    master = merged.master_contact_persons[ContactPersonRole.CONTACT.value]
    assert master.full_name == "Virallinen Kontakti"
    assert master.primary_source_id == "club-website"
    assert merged.contact_person.email == "info@ilves.fi"


def test_contact_person_provenance_metadata() -> None:
    obs = _obs(
        source_id="suomisport",
        contact_persons=[_person("Maija Meikäläinen", "sihteeri", emails=["maija@ilves.fi"])],
    )
    club = observation_to_club(obs, sources=SOURCES)
    record = club.contact_person_observations[0]

    assert record.source_id == "suomisport"
    assert record.source_url == "https://suomisport.example.fi/club/1"
    assert record.source_record_key == "suomisport-rec-1"
    assert record.first_seen_at == obs.collected_at
    assert record.last_seen_at == obs.collected_at
    assert record.observation_id == obs.observation_id


def test_multiple_emails_and_phones_on_person() -> None:
    club = observation_to_club(
        _obs(
            source_id="suomisport",
            contact_persons=[
                _person(
                    "Maija Meikäläinen",
                    "sihteeri",
                    emails=["maija@ilves.fi", "sihteeri@ilves.fi"],
                    phones=["+358 40 111 1111", "+358 50 222 2222"],
                )
            ],
        ),
        sources=SOURCES,
    )

    record = club.contact_person_observations[0]
    assert len(record.emails) == 2
    assert len(record.phones) == 2
    master = club.master_contact_persons["sihteeri"]
    assert len(master.emails) == 2
    assert len(master.phones) == 2
