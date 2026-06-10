"""Request/response DTOs for the API.

Kept separate from domain models so the wire contract can evolve independently
of the internal model. Response models reuse domain types directly where the
shape already matches what the frontend needs.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ScenarioSize
from app.models.kpi import Alert, KPI
from app.models.scheduling import ScheduledOperation, SolverConfig, SolverStatus


class SimulateRequest(BaseModel):
    seed: int = 42
    size: ScenarioSize = ScenarioSize.SMALL
    name: str | None = None


class CreateScenarioRequest(SimulateRequest):
    """POST /scenarios body (same fields; explicit creation endpoint)."""


class SolveRequest(BaseModel):
    scenario_id: str
    config: SolverConfig | None = None


class GanttRow(BaseModel):
    """One machine lane in the Gantt chart with its operations."""

    machine_id: str
    machine_name: str
    machine_type: str
    operations: list[ScheduledOperation] = Field(default_factory=list)


class ScheduleResponse(BaseModel):
    """Gantt-ready schedule: metadata plus operations grouped by machine."""

    schedule_id: str
    scenario_id: str
    solver_status: SolverStatus
    makespan_min: int
    objective_value: float
    horizon_start: datetime
    horizon_minutes: int
    rows: list[GanttRow] = Field(default_factory=list)


class KPIResponse(KPI):
    pass


class AlertsResponse(BaseModel):
    scenario_id: str
    schedule_id: str
    alerts: list[Alert] = Field(default_factory=list)
