"""KPI and Alert models surfaced to the dashboard."""

from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.enums import AlertSeverity, AlertType


class MachineUtilisation(BaseModel):
    machine_id: str
    machine_name: str
    busy_min: int
    available_min: int
    utilisation_pct: float


class KPI(BaseModel):
    """Headline metrics for a solved scenario."""

    scenario_id: str
    schedule_id: str

    scheduled_orders: int
    total_orders: int
    on_time_rate: float  # 0..1
    avg_lateness_min: float
    makespan_min: int

    overall_utilisation_pct: float
    machine_utilisation: list[MachineUtilisation] = Field(default_factory=list)
    bottleneck_machine_id: str | None = None

    backlog_size: int
    tonnage_scheduled_today_kg: float
    num_alerts: int


class Alert(BaseModel):
    """A solver/data condition worth surfacing to the operator."""

    id: str = Field(default_factory=lambda: f"alt_{uuid4().hex[:8]}")
    severity: AlertSeverity
    type: AlertType
    message: str
    entity_refs: list[str] = Field(default_factory=list)
