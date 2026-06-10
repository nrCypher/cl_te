"""Persistence layer behind an abstract interface.

The ABCs in :mod:`app.repository.base` decouple services from storage. The
default :class:`SqliteScenarioRepository` / :class:`SqliteScheduleRepository`
store pydantic JSON blobs, but any backend (Postgres, an ERP gateway, an
in-memory cache) can be dropped in without touching the service or API layers.
"""

from app.repository.base import ScenarioRepository, ScheduleRepository
from app.repository.sqlite import (
    SqliteScenarioRepository,
    SqliteScheduleRepository,
    init_db,
)

__all__ = [
    "ScenarioRepository",
    "ScheduleRepository",
    "SqliteScenarioRepository",
    "SqliteScheduleRepository",
    "init_db",
]
