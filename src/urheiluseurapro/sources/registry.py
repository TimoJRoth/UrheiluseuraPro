"""SourceConfig-rekisteri ja lataus keskitetystä asetustiedostosta."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from urheiluseurapro.config import Settings, get_settings, project_root
from urheiluseurapro.models.source_config import SourceConfig

DEFAULT_SOURCES_PATH = project_root() / "config" / "sources.json"


def _http_defaults(settings: Settings) -> dict[str, float | int | str]:
    return {
        "request_timeout": settings.request_timeout,
        "request_delay": settings.request_delay,
        "request_retries": settings.request_retries,
        "retry_backoff_seconds": settings.request_retry_backoff_seconds,
        "user_agent": settings.user_agent,
    }


def _resolve_entry(raw: dict[str, Any], settings: Settings) -> SourceConfig:
    """Yhdistä lähteen määrittely globaalien oletusten kanssa."""
    defaults = _http_defaults(settings)
    merged: dict[str, Any] = {**defaults, **raw}
    return SourceConfig.model_validate(merged)


class SourceConfigRegistry:
    """Kaikkien tietolähteiden keskitetty asetusrekisteri."""

    def __init__(self, configs: dict[str, SourceConfig]) -> None:
        self._configs = dict(configs)

    def get(self, source_id: str) -> SourceConfig | None:
        return self._configs.get(source_id)

    def require(self, source_id: str) -> SourceConfig:
        config = self.get(source_id)
        if config is None:
            available = ", ".join(sorted(self._configs)) or "(ei määriteltyjä)"
            raise KeyError(f"Tuntematon lähde '{source_id}'. Määritelty: {available}")
        return config

    def list_all(self) -> list[SourceConfig]:
        return sorted(self._configs.values(), key=lambda c: c.source_id)

    def list_enabled(self) -> list[SourceConfig]:
        return [c for c in self.list_all() if c.enabled]

    def source_ids(self) -> list[str]:
        return sorted(self._configs)


def load_source_registry(
    settings: Settings | None = None,
    *,
    path: Path | None = None,
) -> SourceConfigRegistry:
    """Lataa lähteet config/sources.json-tiedostosta."""
    resolved_settings = settings or get_settings()
    config_path = path or DEFAULT_SOURCES_PATH

    if not config_path.is_file():
        raise FileNotFoundError(f"Lähdeasetustiedostoa ei löydy: {config_path}")

    payload = json.loads(config_path.read_text(encoding="utf-8"))
    sources_raw = payload.get("sources")
    if not isinstance(sources_raw, list):
        raise ValueError(f"{config_path}: 'sources' pitää olla lista")

    configs: dict[str, SourceConfig] = {}
    for entry in sources_raw:
        if not isinstance(entry, dict):
            raise ValueError(f"{config_path}: jokainen lähde on objekti")
        config = _resolve_entry(entry, resolved_settings)
        if config.source_id in configs:
            raise ValueError(f"{config_path}: päällekkäinen source_id '{config.source_id}'")
        configs[config.source_id] = config

    return SourceConfigRegistry(configs)


def default_source_registry(settings: Settings | None = None) -> SourceConfigRegistry:
    """Palauttaa oletusrekisterin (config/sources.json)."""
    return load_source_registry(settings)
