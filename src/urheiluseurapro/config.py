"""Sovelluksen asetukset."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def project_root() -> Path:
    """Palauttaa projektin juurikansion (pyproject.toml)."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


class Settings(BaseSettings):
    """Ympäristömuuttujista ja .env-tiedostosta luettavat asetukset."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="URHEILUSEURAPRO_",
        extra="ignore",
    )

    request_delay: float = Field(default=1.0, ge=0.0)
    request_timeout: float = Field(default=30.0, gt=0.0)
    user_agent: str = "UrheiluseuraPro/0.1"
    log_level: str = "INFO"
    output_dir: Path = Field(default_factory=lambda: project_root() / "output")
    data_dir: Path = Field(default_factory=lambda: project_root() / "data")

    def resolve_output_dir(self) -> Path:
        path = self.output_dir if self.output_dir.is_absolute() else project_root() / self.output_dir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def resolve_data_dir(self) -> Path:
        path = self.data_dir if self.data_dir.is_absolute() else project_root() / self.data_dir
        path.mkdir(parents=True, exist_ok=True)
        return path


def get_settings() -> Settings:
    return Settings()
