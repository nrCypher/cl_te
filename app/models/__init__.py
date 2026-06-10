"""Domain models for the production-scheduling prototype.

These are pure Pydantic v2 types with no dependency on the simulator, solver,
KPI, or persistence layers. Every other layer depends on these models, which is
what lets us swap the synthetic simulator for real ERP/MES adapters later
without touching the solver or API code.
"""

from app.models.enums import (
    AlertSeverity,
    AlertType,
    MachineType,
    OperationStatus,
    Priority,
    ScenarioSize,
    SolverStatus,
    WorkOrderStatus,
)
from app.models.domain import (
    Breakdown,
    Machine,
    MaintenanceWindow,
    Material,
    Operation,
    OperationTemplate,
    Operator,
    Product,
    Routing,
    Shift,
    WorkOrder,
)
from app.models.scenario import Scenario, ScenarioSummary
from app.models.scheduling import (
    Schedule,
    ScheduledOperation,
    SolverConfig,
    SolverResult,
)
from app.models.kpi import Alert, KPI, MachineUtilisation

__all__ = [
    # enums
    "AlertSeverity",
    "AlertType",
    "MachineType",
    "OperationStatus",
    "Priority",
    "ScenarioSize",
    "SolverStatus",
    "WorkOrderStatus",
    # domain
    "Breakdown",
    "Machine",
    "MaintenanceWindow",
    "Material",
    "Operation",
    "OperationTemplate",
    "Operator",
    "Product",
    "Routing",
    "Shift",
    "WorkOrder",
    # scenario
    "Scenario",
    "ScenarioSummary",
    # scheduling
    "Schedule",
    "ScheduledOperation",
    "SolverConfig",
    "SolverResult",
    # kpi
    "Alert",
    "KPI",
    "MachineUtilisation",
]
