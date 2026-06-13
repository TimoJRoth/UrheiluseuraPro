"""Kerääjien abstrakti perusluokka."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, ClassVar
from uuid import uuid4

from urheiluseurapro.config import Settings, get_settings
from urheiluseurapro.models.collector import CollectorResult
from urheiluseurapro.models.contact_person import ObservationContactPerson
from urheiluseurapro.models.observation import ClubObservation
from urheiluseurapro.models.source_config import SourceConfig
from urheiluseurapro.sources.registry import SourceConfigRegistry, default_source_registry


class BaseCollector(ABC):
    """
    Kaikkien tietolähteiden kerääjien yhteinen rajapinta.

    Kerääjä tuottaa CollectorResult-olioita, jotka sisältävät ClubObservation-havainnon
    merge-engineä varten sekä provenience-metadatan (source, confidence, fetched_at, …).

    Lähdekohtaiset asetukset (source_id, display_name, confidence, …) tulevat
    SourceConfig-järjestelmästä – ei kovakoodattu luokkaan.
    """

    SOURCE_CONFIG_KEY: ClassVar[str]

    def __init__(
        self,
        *,
        source_config: SourceConfig | None = None,
        source_registry: SourceConfigRegistry | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        registry = source_registry or default_source_registry(self._settings)
        if source_config is not None:
            self._source_config = source_config
        else:
            self._source_config = registry.require(self.SOURCE_CONFIG_KEY)

    @property
    def source_config(self) -> SourceConfig:
        return self._source_config

    @property
    def source_id(self) -> str:
        return self._source_config.source_id

    @property
    def display_name(self) -> str:
        return self._source_config.display_name

    @property
    def base_url(self) -> str | None:
        return self._source_config.base_url

    @property
    def default_confidence(self) -> float:
        return self._source_config.confidence_default

    @property
    def source(self) -> str:
        """Lähteen tunniste (alias source_id)."""
        return self.source_id

    @abstractmethod
    async def collect(self) -> list[CollectorResult]:
        """Kerää seuratiedot lähteestä yhtenäisessä tulosmuodossa."""

    @abstractmethod
    def supports_url(self, url: str) -> bool:
        """Tunnistaa, voidaanko annettu URL käsitellä tällä kerääjällä."""

    async def collect_observations(self) -> list[ClubObservation]:
        """Kerää ja palauttaa pelkät ClubObservation-havainnot."""
        results = await self.collect()
        return [result.observation for result in results]

    def build_result(
        self,
        *,
        name_raw: str,
        municipality_raw: str | None = None,
        sports_raw: list[str] | None = None,
        source_record_key: str | None = None,
        source_url: str | None = None,
        website_raw: str | None = None,
        email_raw: str | None = None,
        phone_raw: str | None = None,
        address_raw: str | None = None,
        contact_persons: list[ObservationContactPerson] | None = None,
        confidence: float | None = None,
        fetched_at: datetime | None = None,
        ingestion_run_id: str | None = None,
        raw: dict[str, Any] | None = None,
    ) -> CollectorResult:
        """Rakenna yhtenäinen keruutulos provenience-metadatoineen."""
        now = fetched_at or datetime.now(timezone.utc)
        conf = self.default_confidence if confidence is None else confidence
        resolved_url = source_url or self.base_url

        persons: list[ObservationContactPerson] = []
        for person in contact_persons or []:
            if person.observation_confidence is None:
                persons.append(person.model_copy(update={"observation_confidence": conf}))
            else:
                persons.append(person)

        observation = ClubObservation(
            observation_id=str(uuid4()),
            source_id=self.source_id,
            source_record_key=source_record_key,
            source_url=resolved_url,
            ingestion_run_id=ingestion_run_id,
            name_raw=name_raw,
            municipality_raw=municipality_raw,
            sports_raw=sports_raw or [],
            website_raw=website_raw,
            email_raw=email_raw,
            phone_raw=phone_raw,
            address_raw=address_raw,
            contact_persons=persons,
            collected_at=now,
            first_seen_at=now,
            last_seen_at=now,
            observation_confidence=conf,
            raw=raw,
        )

        return CollectorResult(
            source=self.source_id,
            source_url=str(resolved_url) if resolved_url else None,
            confidence=conf,
            fetched_at=now,
            first_seen_at=now,
            last_seen_at=now,
            observation=observation,
        )
