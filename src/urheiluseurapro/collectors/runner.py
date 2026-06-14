"""Collector-keruun orkestraatio."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from urheiluseurapro.collectors.base import BaseCollector
from urheiluseurapro.models.collector import CollectorResult
from urheiluseurapro.models.ingestion import IngestionRun
from urheiluseurapro.models.observation import ClubObservation
from urheiluseurapro.normalizers import normalize_observation

logger = logging.getLogger(__name__)


class CollectorRunSummary:
    """Yhden collector-ajon yhteenveto."""

    def __init__(
        self,
        *,
        run: IngestionRun,
        results: list[CollectorResult],
    ) -> None:
        self.run = run
        self.results = results

    @property
    def observations(self) -> list[ClubObservation]:
        return [result.observation for result in self.results]


async def run_collector(collector: BaseCollector) -> CollectorRunSummary:
    """
    Suorita collector ja palauta yhtenäinen yhteenveto provenience-metadatoineen.

    Asettaa ingestion_run_id jokaiselle havainnolle.
    """
    run_id = str(uuid4())
    started = datetime.now(timezone.utc)
    run = IngestionRun(run_id=run_id, source_id=collector.source_id, started_at=started)

    try:
        raw_results = await collector.collect()
        results: list[CollectorResult] = []
        for result in raw_results:
            observation = normalize_observation(
                result.observation.model_copy(update={"ingestion_run_id": run_id})
            )
            results.append(
                CollectorResult(
                    source=result.source,
                    source_url=result.source_url,
                    confidence=result.confidence,
                    fetched_at=result.fetched_at,
                    first_seen_at=result.first_seen_at,
                    last_seen_at=result.last_seen_at,
                    observation=observation,
                )
            )

        finished = datetime.now(timezone.utc)
        run = run.model_copy(
            update={
                "finished_at": finished,
                "status": "success",
                "records_fetched": len(results),
                "records_normalized": len(results),
            }
        )
        logger.info(
            "Collector %s valmis: %d havaintoa (run_id=%s)",
            collector.source_id,
            len(results),
            run_id,
        )
        return CollectorRunSummary(run=run, results=results)
    except Exception as exc:
        finished = datetime.now(timezone.utc)
        run = run.model_copy(
            update={
                "finished_at": finished,
                "status": "failed",
                "errors": [str(exc)],
            }
        )
        logger.exception("Collector %s epäonnistui", collector.source_id)
        raise
