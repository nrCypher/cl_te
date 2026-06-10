"""Application settings (env-overridable via pydantic-settings)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.models.enums import ScenarioSize


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WORKSHOP_", extra="ignore")

    app_name: str = "Sheet-Metal Workshop Scheduler"
    db_path: str = "data/workshop.db"

    default_seed: int = 42
    default_size: ScenarioSize = ScenarioSize.SMALL

    solver_time_limit_s: float = 10.0
    solver_num_workers: int = 8


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
