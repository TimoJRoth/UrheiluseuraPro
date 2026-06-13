"""Mock-collector – kehitys- ja testidata muistista (ei verkkohakuja)."""

from __future__ import annotations

from typing import Any

from urheiluseurapro.collectors.base import BaseCollector
from urheiluseurapro.models.collector import CollectorResult
from urheiluseurapro.models.contact_person import ObservationContactPerson

_MOCK_CLUBS: list[dict[str, Any]] = [
    {
        "source_record_key": "mock-club-001",
        "source_url": "mock://clubs/alpha",
        "name": "Esimerkki Urheiluseura Alpha",
        "municipality": "Tampere",
        "sports": ["esimerkkilaji"],
        "website": "https://example.invalid/alpha",
        "email": "info@alpha.example",
        "phone": "+358 40 100 0001",
        "address": "Esimerkkikatu 1, 33100 Tampere",
        "confidence": 0.75,
        "contact_persons": [
            {
                "full_name": "Ada Alpha",
                "role": "sihteeri",
                "emails": ["sihteeri@alpha.example"],
                "phones": ["+358 40 100 0002"],
            },
        ],
    },
    {
        "source_record_key": "mock-club-002",
        "source_url": "mock://clubs/beta",
        "name": "Esimerkki Urheiluseura Beta",
        "municipality": "Helsinki",
        "sports": ["esimerkkilaji"],
        "website": "https://example.invalid/beta",
        "email": "info@beta.example",
        "phone": "+358 40 200 0001",
        "address": "Testikatu 2, 00100 Helsinki",
        "confidence": 0.80,
        "contact_persons": [
            {
                "full_name": "Ben Beta",
                "role": "puheenjohtaja",
                "emails": ["pj@beta.example"],
                "phones": ["+358 40 200 0002"],
            },
        ],
    },
    {
        "source_record_key": "mock-club-003",
        "source_url": "mock://clubs/gamma",
        "name": "Esimerkki Urheiluseura Gamma",
        "municipality": "Turku",
        "sports": ["esimerkkilaji"],
        "website": "https://example.invalid/gamma",
        "email": "info@gamma.example",
        "phone": "+358 40 300 0001",
        "address": "Demokatu 3, 20100 Turku",
        "confidence": 0.70,
        "contact_persons": [
            {
                "full_name": "Cara Gamma",
                "role": "yhteyshenkilö",
                "emails": ["yhteys@gamma.example", "info@gamma.example"],
                "phones": [],
            },
        ],
    },
]


class MockCollector(BaseCollector):
    """
    Geneerinen mock-collector arkkitehtuurin testaukseen.

    Palauttaa kolme kovakoodattua seuraa muistista. Ei tee verkkopyyntöjä.
    Lähdeasetukset tulevat SourceConfigista (source_id: mock).
    """

    SOURCE_CONFIG_KEY = "mock"

    async def collect(self) -> list[CollectorResult]:
        return [self._record_to_result(record) for record in _MOCK_CLUBS]

    def _record_to_result(self, record: dict[str, Any]) -> CollectorResult:
        contact_persons = [
            ObservationContactPerson(
                full_name=person["full_name"],
                role=person.get("role"),
                emails=person.get("emails", []),
                phones=person.get("phones", []),
            )
            for person in record.get("contact_persons", [])
        ]

        return self.build_result(
            name_raw=record["name"],
            municipality_raw=record.get("municipality"),
            sports_raw=record.get("sports", []),
            source_record_key=record.get("source_record_key"),
            source_url=record.get("source_url"),
            website_raw=record.get("website"),
            email_raw=record.get("email"),
            phone_raw=record.get("phone"),
            address_raw=record.get("address"),
            contact_persons=contact_persons,
            confidence=record.get("confidence", self.default_confidence),
            raw={"collector": "mock", "record": record},
        )

    def supports_url(self, url: str) -> bool:
        lowered = url.lower()
        base = (self.base_url or "").lower()
        return lowered.startswith(base) or "example.invalid" in lowered
