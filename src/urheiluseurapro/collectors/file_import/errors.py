"""Tiedostotuonnin poikkeukset."""

from __future__ import annotations

from pathlib import Path


class FileImportError(Exception):
    """Tiedostotuonnin yleinen virhe."""

    def __init__(self, message: str, *, path: Path | None = None) -> None:
        super().__init__(message)
        self.path = path


class FileImportNotFoundError(FileImportError):
    """Tuontitiedostoa ei löydy."""


class FileImportParseError(FileImportError):
    """Tiedoston sisältöä ei voitu jäsentää."""


class FileImportUnsupportedFormatError(FileImportError):
    """Tiedostomuotoa ei tueta (Excel tulossa myöhemmin)."""
