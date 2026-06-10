"""Enumerations shared across the domain model.

Keeping these in one place means the simulator, solver, and API all agree on
the vocabulary (machine types, statuses, priorities) without circular imports.
"""

from __future__ import annotations

from enum import Enum


class MachineType(str, Enum):
    """Sheet-metal workshop machine families.

    The values double as the ``op_type`` of the operations that run on them,
    which keeps machine eligibility easy to reason about: an operation of type
    ``LASER_CUTTING`` is eligible on any machine of type ``LASER_CUTTING``.
    """

    LASER_CUTTING = "laser_cutting"
    STAMPING = "stamping"
    BENDING = "bending"
    WELDING = "welding"
    ADDITIVE = "additive"
    FINISHING = "finishing"
    TREATMENT = "treatment"
    ASSEMBLY = "assembly"


# Canonical order in which sheet-metal operations tend to flow through a shop.
# The simulator samples contiguous-ish slices of this ordering to build
# realistic routings (you cannot weld before you cut, etc.).
ROUTING_FLOW: tuple[MachineType, ...] = (
    MachineType.LASER_CUTTING,
    MachineType.STAMPING,
    MachineType.BENDING,
    MachineType.ADDITIVE,
    MachineType.WELDING,
    MachineType.TREATMENT,
    MachineType.FINISHING,
    MachineType.ASSEMBLY,
)


class Priority(str, Enum):
    """Work-order priority. ``weight`` feeds the solver's tardiness penalty."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def weight(self) -> int:
        return {
            Priority.LOW: 1,
            Priority.MEDIUM: 2,
            Priority.HIGH: 4,
            Priority.CRITICAL: 8,
        }[self]


class WorkOrderStatus(str, Enum):
    RELEASED = "released"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class OperationStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    DONE = "done"


class ScenarioSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class SolverStatus(str, Enum):
    """Normalised solver outcome, decoupled from OR-Tools' own constants."""

    OPTIMAL = "optimal"
    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"
    UNKNOWN = "unknown"
    MODEL_INVALID = "model_invalid"
    EMPTY = "empty"  # nothing to schedule


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(str, Enum):
    BOTTLENECK = "bottleneck"
    LATE_ORDER = "late_order"
    MATERIAL_SHORTAGE = "material_shortage"
    CAPACITY_OVERLOAD = "capacity_overload"
    INFEASIBLE = "infeasible"
    BREAKDOWN = "breakdown"
