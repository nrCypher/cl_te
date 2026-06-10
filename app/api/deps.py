"""Dependency-injection providers.

A single shared SQLite connection is created at import time and reused across
requests (SQLite handles its own locking; the repos add a thread lock). Swapping
the persistence backend means changing only the factory functions here.
"""

from __future__ import annotations

import sqlite3
from functools import lru_cache

from app.config import get_settings
from app.repository.sqlite import (
    SqliteScenarioRepository,
    SqliteScheduleRepository,
    _connect,
    init_db,
)
from app.services.analytics_service import AnalyticsService
from app.services.scenario_service import ScenarioService
from app.services.scheduling_service import SchedulingService


@lru_cache(maxsize=1)
def get_connection() -> sqlite3.Connection:
    settings = get_settings()
    conn = _connect(settings.db_path)
    init_db(conn)
    return conn


@lru_cache(maxsize=1)
def get_scenario_service() -> ScenarioService:
    return ScenarioService(SqliteScenarioRepository(get_connection()))


@lru_cache(maxsize=1)
def get_scheduling_service() -> SchedulingService:
    return SchedulingService(SqliteScheduleRepository(get_connection()))


@lru_cache(maxsize=1)
def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()


def reset_dependencies() -> None:
    """Test helper: clear cached singletons so a fresh DB can be injected."""
    get_connection.cache_clear()
    get_scenario_service.cache_clear()
    get_scheduling_service.cache_clear()
    get_analytics_service.cache_clear()
