"""The Scenario aggregate: a complete, self-contained workshop snapshot.

A Scenario bundles every entity the solver and KPI layers need. It is the unit
of persistence and the boundary an ERP/MES adapter would populate instead of the
synthetic simulator.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from pydantic import BaseModel, Field, computed_field

from app.models.domain import (
    Breakdown,
    Machine,
    MaintenanceWindow,
    Material,
    Operation,
    Operator,
    Product,
    Routing,
    Shift,
    WorkOrder,
)
from app.models.enums import ScenarioSize


class Scenario(BaseModel):
    """Everything required to build and solve a scheduling problem."""

    id: str = Field(default_factory=lambda: f"scn_{uuid4().hex[:12]}")
    name: str = "unnamed-scenario"
    seed: int
    size: ScenarioSize
    created_at: datetime = Field(default_factory=datetime.utcnow)

    horizon_start: datetime
    horizon_minutes: int = Field(gt=0)

    materials: list[Material] = Field(default_factory=list)
    machines: list[Machine] = Field(default_factory=list)
    routings: list[Routing] = Field(default_factory=list)
    products: list[Product] = Field(default_factory=list)
    work_orders: list[WorkOrder] = Field(default_factory=list)
    operations: list[Operation] = Field(default_factory=list)
    operators: list[Operator] = Field(default_factory=list)
    shifts: list[Shift] = Field(default_factory=list)
    maintenance_windows: list[MaintenanceWindow] = Field(default_factory=list)
    breakdowns: list[Breakdown] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def horizon_end(self) -> datetime:
        return self.horizon_start + timedelta(minutes=self.horizon_minutes)

    # -- convenience lookups (used by solver / KPI / API) -----------------

    def machine_by_id(self, machine_id: str) -> Machine | None:
        return next((m for m in self.machines if m.id == machine_id), None)

    def product_by_id(self, product_id: str) -> Product | None:
        return next((p for p in self.products if p.id == product_id), None)

    def work_order_by_id(self, wo_id: str) -> WorkOrder | None:
        return next((w for w in self.work_orders if w.id == wo_id), None)

    def operations_for(self, wo_id: str) -> list[Operation]:
        ops = [o for o in self.operations if o.work_order_id == wo_id]
        return sorted(ops, key=lambda o: o.position)

    def minutes_to_datetime(self, minute: int) -> datetime:
        return self.horizon_start + timedelta(minutes=minute)

    def datetime_to_minutes(self, when: datetime) -> int:
        return int((when - self.horizon_start).total_seconds() // 60)

    def summary(self) -> "ScenarioSummary":
        return ScenarioSummary(
            id=self.id,
            name=self.name,
            seed=self.seed,
            size=self.size,
            created_at=self.created_at,
            horizon_start=self.horizon_start,
            horizon_minutes=self.horizon_minutes,
            num_machines=len(self.machines),
            num_work_orders=len(self.work_orders),
            num_operations=len(self.operations),
            num_products=len(self.products),
        )


class ScenarioSummary(BaseModel):
    """Lightweight scenario header for list/creation responses."""

    id: str
    name: str
    seed: int
    size: ScenarioSize
    created_at: datetime
    horizon_start: datetime
    horizon_minutes: int
    num_machines: int
    num_work_orders: int
    num_operations: int
    num_products: int
