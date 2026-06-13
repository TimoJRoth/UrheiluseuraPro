"""Keruuputken suoritus."""

import logging
from pathlib import Path

from urheiluseurapro.collectors.registry import CollectorRegistry
from urheiluseurapro.collectors.runner import run_collector
from urheiluseurapro.config import Settings
from urheiluseurapro.exporters import export_csv, export_json
from urheiluseurapro.models.club import Club
from urheiluseurapro.models.enums import SourceCategory
from urheiluseurapro.models.source import Source
from urheiluseurapro.pipeline.ingest import ingest_observations

logger = logging.getLogger(__name__)


async def run_collection(
    registry: CollectorRegistry,
    source_id: str,
    settings: Settings,
    export_format: str = "csv",
    existing_clubs: list[Club] | None = None,
) -> tuple[list[Club], list[Path]]:
    """
    Suorittaa keruun valitusta lähteestä, yhdistää master-tietueisiin ja vie tulokset.

    Kerääjä tuottaa ClubObservation-havaintoja → ingest_observations → Club-master.
    """
    collector = registry.get(source_id)
    logger.info("Kerätään lähde: %s (%s)", collector.display_name, collector.source_id)

    summary = await run_collector(collector)
    observations = summary.observations
    sources = {
        source_id: Source(
            source_id=source_id,
            name=collector.display_name,
            category=SourceCategory.OTHER,
            geographic_coverage="Kehitys",
            merge_priority=50,
        )
    }
    clubs, _ = ingest_observations(observations, existing_clubs or [], sources=sources)
    logger.info(
        "Master-tietueita: %d (havaintoja: %d, run_id=%s)",
        len(clubs),
        len(observations),
        summary.run.run_id,
    )

    output_dir = settings.resolve_output_dir()
    prefix = f"clubs_{source_id}"

    if export_format == "csv":
        path = export_csv(clubs, output_dir, prefix=prefix)
        return clubs, [path]
    if export_format == "json":
        path = export_json(clubs, output_dir, prefix=prefix)
        return clubs, [path]
    if export_format == "both":
        csv_path = export_csv(clubs, output_dir, prefix=prefix)
        json_path = export_json(clubs, output_dir, prefix=prefix)
        return clubs, [csv_path, json_path]

    raise ValueError(f"Tuntematon vientiformaatti: {export_format}")
