"""FileImportCollector – paikallisten CSV/JSON-tiedostojen tuonti."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from urheiluseurapro.collectors.base import BaseCollector
from urheiluseurapro.collectors.file_import.mapping import DEFAULT_FIELD_MAPPING
from urheiluseurapro.collectors.file_import.parsers import load_records
from urheiluseurapro.config import Settings
from urheiluseurapro.models.collector import CollectorResult
from urheiluseurapro.models.contact_person import ObservationContactPerson
from urheiluseurapro.models.source_config import SourceConfig
from urheiluseurapro.sources.registry import SourceConfigRegistry


class FileImportCollector(BaseCollector):
    """
    Lukee paikallisia CSV- ja JSON-tiedostoja ja tuottaa CollectorResult-olioita.

    Ei verkkohakuja. Excel-tuki lisätään myöhemmin.
    source_url on muodossa file:///abs/polku/tiedostoon.
    """

    SOURCE_CONFIG_KEY = "file-import"

    def __init__(
        self,
        file_path: Path | str,
        *,
        source_config: SourceConfig | None = None,
        source_registry: SourceConfigRegistry | None = None,
        settings: Settings | None = None,
        field_mapping: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            source_config=source_config,
            source_registry=source_registry,
            settings=settings,
        )
        self._file_path = Path(file_path)
        self._field_mapping = field_mapping or DEFAULT_FIELD_MAPPING

    @property
    def file_path(self) -> Path:
        return self._file_path

    async def collect(self) -> list[CollectorResult]:
        fetched_at = datetime.now(timezone.utc)
        records = load_records(self._file_path, field_mapping=self._field_mapping)
        source_url = self._file_path.resolve().as_uri()
        return [
            self._record_to_result(record, source_url=source_url, fetched_at=fetched_at, row_index=index)
            for index, record in enumerate(records, start=1)
        ]

    def _record_to_result(
        self,
        record: dict[str, Any],
        *,
        source_url: str,
        fetched_at: datetime,
        row_index: int,
    ) -> CollectorResult:
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
            source_record_key=f"{self._file_path.name}:{row_index}",
            source_url=source_url,
            website_raw=record.get("website"),
            email_raw=record.get("email"),
            phone_raw=record.get("phone"),
            address_raw=record.get("address"),
            contact_persons=contact_persons,
            confidence=self.default_confidence,
            fetched_at=fetched_at,
            raw={
                "collector": self.source_id,
                "file": {
                    "path": str(self._file_path.resolve()),
                    "source_url": source_url,
                    "row_index": row_index,
                },
                "record": record,
            },
        )

    def supports_url(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme != "file":
            return False
        if not parsed.path:
            return False
        path = Path(unquote(parsed.path))
        suffix = path.suffix.lower()
        return suffix in {".csv", ".json"}
