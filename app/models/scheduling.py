"""Solver inputs and outputs.

``ScheduledOperation`` carries both integer-minute fields (the solver's native
unit) and ISO datetimes (frontend-friendly), so the Gantt UI can render bars
directly while tests can assert on the integers.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.enums import OperationStatus, SolverStatus


class SolverConfig(BaseModel):
    """Tunable solver parameters and objective weights."""

    time_limit_s: float = Field(default=10.0, gt=0)
    num_workers: int = Field(default=8, ge=1)

    weight_makespan: int = Field(default=1, ge=0)
    weight_tardiness: int = Field(default=3, ge=0)
    weight_priority: int = Field(default=2, ge=0)
    weight_balance: int = Field(default=1, ge=0)

    enable_maintenance: bool = True
    enable_breakdowns: bool = True


class ScheduledOperation(BaseModel):
    """A single bar on the Gantt chart."""

    operation_id: str
    work_order_id: str
    work_order_code: str
    machine_id: str
    op_type: str
    position: int

    start_min: int
    end_min: int
    setup_min: int
    start: datetime
    end: datetime
    status: OperationStatus = OperationStatus.SCHEDULED


class Schedule(BaseModel):
    """The result of a solve: scheduled operations + headline metrics."""

    id: str = Field(default_factory=lambda: f"sch_{uuid4().hex[:12]}")
    scenario_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    solver_status: SolverStatus
    makespan_min: int = 0
    objective_value: float = 0.0
    scheduled_operations: list[ScheduledOperation] = Field(default_factory=list)

    def operations_for_machine(self, machine_id: str) -> list[ScheduledOperation]:
        ops = [o for o in self.scheduled_operations if o.machine_id == machine_id]
        return sorted(ops, key=lambda o: o.start_min)

    def completion_min_by_work_order(self) -> dict[str, int]:
        """Latest operation end per work order (its completion time)."""
        out: dict[str, int] = {}
        for op in self.scheduled_operations:
            out[op.work_order_id] = max(out.get(op.work_order_id, 0), op.end_min)
        return out


class SolverResult(BaseModel):
    """Wrapper returned by ``POST /solve``."""

    schedule: Schedule
    status: SolverStatus
    feasible: bool
    objective_value: float
    wall_time_s: float
    message: str = ""
