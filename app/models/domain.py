"""Core domain entities for the workshop.

Two layers of operation modelling are intentional:

* ``OperationTemplate`` lives inside a ``Routing`` and describes *how* a product
  is made (independent of any particular order or quantity).
* ``Operation`` is the concrete, schedulable instance the solver consumes. It is
  produced by expanding a work order against its product's routing, baking in
  the quantity (so ``duration_min`` is already total setup + processing time)
  and the resolved list of eligible machine ids.

This separation mirrors how a real MES distinguishes routing master data from
the operations of a specific production order, which makes the eventual ERP
swap cleaner.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.enums import (
    MachineType,
    OperationStatus,
    Priority,
    WorkOrderStatus,
)


class Material(BaseModel):
    """A raw sheet-metal stock item consumed by operations."""

    id: str
    name: str
    grade: str
    thickness_mm: float = Field(gt=0)
    available_kg: float = Field(ge=0)
    unit: str = "kg"


class Machine(BaseModel):
    """A workshop resource. ``speed_factor`` < 1 means slower than nominal."""

    id: str
    name: str
    type: MachineType
    capacity: int = Field(default=1, ge=1, description="Parallel jobs supported")
    cost_per_hour: float = Field(default=0.0, ge=0)
    speed_factor: float = Field(default=1.0, gt=0)

    @property
    def eligible_op_type(self) -> MachineType:
        """An operation is eligible here iff its op_type equals this."""
        return self.type


class OperationTemplate(BaseModel):
    """One step of a routing (master data, quantity-independent)."""

    id: str
    name: str
    op_type: MachineType
    position: int = Field(ge=0, description="Order within the routing")
    base_processing_min_per_unit: float = Field(gt=0)
    setup_min: float = Field(ge=0)
    material_kg_per_unit: float = Field(ge=0, default=0.0)
    eligible_machine_types: list[MachineType] = Field(default_factory=list)


class Routing(BaseModel):
    """An ordered list of operation templates to manufacture a product."""

    id: str
    product_id: str
    operations: list[OperationTemplate]

    @field_validator("operations")
    @classmethod
    def _non_empty_and_ordered(
        cls, v: list[OperationTemplate]
    ) -> list[OperationTemplate]:
        if not v:
            raise ValueError("A routing must contain at least one operation")
        return sorted(v, key=lambda op: op.position)


class Product(BaseModel):
    id: str
    name: str
    material_id: str
    routing_id: str
    unit_weight_kg: float = Field(gt=0)


class WorkOrder(BaseModel):
    """A demand for a quantity of a product by a due date."""

    id: str
    code: str
    product_id: str
    quantity: int = Field(gt=0)
    release_date: datetime
    due_date: datetime
    priority: Priority = Priority.MEDIUM
    status: WorkOrderStatus = WorkOrderStatus.RELEASED

    @field_validator("due_date")
    @classmethod
    def _due_after_release(cls, v: datetime, info) -> datetime:
        release = info.data.get("release_date")
        if release is not None and v < release:
            raise ValueError("due_date must be on or after release_date")
        return v


class Operation(BaseModel):
    """A concrete schedulable operation (work order × routing step).

    ``duration_min`` is the *nominal* total time (setup + processing × qty) at
    ``speed_factor == 1``. The solver rescales by the chosen machine's speed.
    """

    id: str
    work_order_id: str
    template_id: str
    name: str
    op_type: MachineType
    position: int = Field(ge=0)
    duration_min: int = Field(gt=0)
    setup_min: int = Field(ge=0)
    material_kg: float = Field(ge=0, default=0.0)
    eligible_machine_ids: list[str] = Field(min_length=1)
    predecessor_id: str | None = None
    status: OperationStatus = OperationStatus.PENDING


class Shift(BaseModel):
    """A working-time window (minutes from the scenario horizon start)."""

    id: str
    name: str
    machine_id: str | None = None  # None => applies to all machines
    start_min: int = Field(ge=0)
    end_min: int = Field(gt=0)


class MaintenanceWindow(BaseModel):
    id: str
    machine_id: str
    start_min: int = Field(ge=0)
    end_min: int = Field(gt=0)
    reason: str = "preventive_maintenance"


class Breakdown(BaseModel):
    id: str
    machine_id: str
    start_min: int = Field(ge=0)
    end_min: int = Field(gt=0)
    cause: str = "unplanned"


class Operator(BaseModel):
    """Carried through the model for future scheduling; informational in v1."""

    id: str
    name: str
    skills: list[MachineType] = Field(default_factory=list)
    shift_ids: list[str] = Field(default_factory=list)
