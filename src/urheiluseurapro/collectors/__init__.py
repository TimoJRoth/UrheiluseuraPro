"""Kerääjät – geneerinen ingest-arkkitehtuuri."""

from urheiluseurapro.collectors.base import BaseCollector
from urheiluseurapro.collectors.examples.json_feed import JsonFeedCollector
from urheiluseurapro.collectors.http import HttpClient, HttpCollector
from urheiluseurapro.collectors.mock import MockCollector
from urheiluseurapro.collectors.registry import CollectorRegistry, default_registry
from urheiluseurapro.collectors.runner import CollectorRunSummary, run_collector
from urheiluseurapro.models.collector import CollectorResult

__all__ = [
    "BaseCollector",
    "CollectorRegistry",
    "CollectorResult",
    "CollectorRunSummary",
    "HttpClient",
    "HttpCollector",
    "JsonFeedCollector",
    "MockCollector",
    "default_registry",
    "run_collector",
]
