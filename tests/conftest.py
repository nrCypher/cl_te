"""Shared pytest fixtures.

The API tests run against an isolated in-memory SQLite database so they never
touch the developer's real ``data/workshop.db``. We use FastAPI's
``dependency_overrides`` to inject services bound to an in-memory connection.
"""

from __future__ import annotations

import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.api import deps
from app.models.enums import ScenarioSize
from app.repository.sqlite import (
    SqliteScenarioRepository,
    SqliteScheduleRepository,
    init_db,
)
from app.services.analytics_service import AnalyticsService
from app.services.scenario_service import ScenarioService
from app.services.scheduling_service import SchedulingService
from app.simulator.generator import SyntheticDataGenerator


@pytest.fixture()
def small_scenario():
    """A deterministic small scenario for solver/KPI tests."""
    gen = SyntheticDataGenerator.for_size(seed=7, size=ScenarioSize.SMALL)
    return gen.generate()


@pytest.fixture()
def client():
    """FastAPI TestClient backed by an isolated in-memory DB."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    init_db(conn)

    scenario_service = ScenarioService(SqliteScenarioRepository(conn))
    scheduling_service = SchedulingService(SqliteScheduleRepository(conn))
    analytics_service = AnalyticsService()

    from app.main import create_app

    app = create_app()
    app.dependency_overrides[deps.get_scenario_service] = lambda: scenario_service
    app.dependency_overrides[deps.get_scheduling_service] = (
        lambda: scheduling_service
    )
    app.dependency_overrides[deps.get_analytics_service] = lambda: analytics_service

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    conn.close()
