"""Lähteiden asetusjärjestelmä."""

from urheiluseurapro.sources.registry import (
    SourceConfigRegistry,
    default_source_registry,
    load_source_registry,
)

__all__ = [
    "SourceConfigRegistry",
    "default_source_registry",
    "load_source_registry",
]
