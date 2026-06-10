"""SQLite-backed repositories storing pydantic models as JSON blobs.

Prototype-grade persistence: one table per aggregate, ``data`` column holds the
model's JSON. This keeps the schema trivial and the swap to a normalized store
(or a real ERP gateway) confined to this file. A module-level connection guarded
by a lock keeps it safe for FastAPI's threadpool.
"""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from app.models.scenario import Scenario
from app.models.scheduling import Schedule
from app.repository.base import ScenarioRepository, ScheduleRepository

_LOCK = threading.Lock()


def _connect(db_path: str) -> sqlite3.Connection:
    if db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    with _LOCK:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS scenarios (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                data TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS schedules (
                id TEXT PRIMARY KEY,
                scenario_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                data TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_sched_scenario
                ON schedules(scenario_id, created_at);
            """
        )
        conn.commit()


class SqliteScenarioRepository(ScenarioRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, scenario: Scenario) -> Scenario:
        with _LOCK:
            self._conn.execute(
                "INSERT OR REPLACE INTO scenarios (id, created_at, data) "
                "VALUES (?, ?, ?)",
                (
                    scenario.id,
                    scenario.created_at.isoformat(),
                    scenario.model_dump_json(),
                ),
            )
            self._conn.commit()
        return scenario

    def get(self, scenario_id: str) -> Scenario | None:
        cur = self._conn.execute(
            "SELECT data FROM scenarios WHERE id = ?", (scenario_id,)
        )
        row = cur.fetchone()
        return Scenario.model_validate_json(row["data"]) if row else None

    def list(self) -> list[Scenario]:
        cur = self._conn.execute(
            "SELECT data FROM scenarios ORDER BY created_at DESC"
        )
        return [Scenario.model_validate_json(r["data"]) for r in cur.fetchall()]

    def delete(self, scenario_id: str) -> bool:
        with _LOCK:
            cur = self._conn.execute(
                "DELETE FROM scenarios WHERE id = ?", (scenario_id,)
            )
            self._conn.commit()
        return cur.rowcount > 0


class SqliteScheduleRepository(ScheduleRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, schedule: Schedule) -> Schedule:
        with _LOCK:
            self._conn.execute(
                "INSERT OR REPLACE INTO schedules "
                "(id, scenario_id, created_at, data) VALUES (?, ?, ?, ?)",
                (
                    schedule.id,
                    schedule.scenario_id,
                    schedule.created_at.isoformat(),
                    schedule.model_dump_json(),
                ),
            )
            self._conn.commit()
        return schedule

    def get(self, schedule_id: str) -> Schedule | None:
        cur = self._conn.execute(
            "SELECT data FROM schedules WHERE id = ?", (schedule_id,)
        )
        row = cur.fetchone()
        return Schedule.model_validate_json(row["data"]) if row else None

    def get_latest_for_scenario(self, scenario_id: str) -> Schedule | None:
        cur = self._conn.execute(
            "SELECT data FROM schedules WHERE scenario_id = ? "
            "ORDER BY created_at DESC LIMIT 1",
            (scenario_id,),
        )
        row = cur.fetchone()
        return Schedule.model_validate_json(row["data"]) if row else None

    def list_for_scenario(self, scenario_id: str) -> list[Schedule]:
        cur = self._conn.execute(
            "SELECT data FROM schedules WHERE scenario_id = ? "
            "ORDER BY created_at DESC",
            (scenario_id,),
        )
        return [Schedule.model_validate_json(r["data"]) for r in cur.fetchall()]
