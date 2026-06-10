"""KPI computation tests over a hand-built schedule."""

from __future__ import annotations

from datetime import datetime, timedelta

from app.kpi.calculator import build_alerts, compute_kpis
from app.models.domain import Machine, Operation, Product, WorkOrder
from app.models.enums import (
    AlertType,
    MachineType,
    Priority,
    SolverStatus,
)
from app.models.scenario import Scenario
from app.models.scheduling import Schedule, ScheduledOperation


def _build_scenario() -> Scenario:
    start = datetime(2026, 6, 8, 8, 0, 0)
    machine = Machine(id="mch_0001", name="Laser #1", type=MachineType.LASER_CUTTING)
    product = Product(
        id="prd_0001",
        name="Bracket",
        material_id="mat_0001",
        routing_id="rtg_0001",
        unit_weight_kg=2.0,
    )
    # WO1 finishes on time; WO2 is late.
    wo1 = WorkOrder(
        id="wo_0001", code="WO-1", product_id="prd_0001", quantity=10,
        release_date=start, due_date=start + timedelta(minutes=600),
        priority=Priority.MEDIUM,
    )
    wo2 = WorkOrder(
        id="wo_0002", code="WO-2", product_id="prd_0001", quantity=10,
        release_date=start, due_date=start + timedelta(minutes=100),
        priority=Priority.CRITICAL,
    )
    op1 = Operation(
        id="op_0001", work_order_id="wo_0001", template_id="opt_1", name="Laser",
        op_type=MachineType.LASER_CUTTING, position=0, duration_min=60,
        setup_min=10, material_kg=20.0, eligible_machine_ids=["mch_0001"],
    )
    op2 = Operation(
        id="op_0002", work_order_id="wo_0002", template_id="opt_1", name="Laser",
        op_type=MachineType.LASER_CUTTING, position=0, duration_min=60,
        setup_min=10, material_kg=20.0, eligible_machine_ids=["mch_0001"],
    )
    return Scenario(
        seed=0, size="small", horizon_start=start, horizon_minutes=2880,
        machines=[machine], products=[product], work_orders=[wo1, wo2],
        operations=[op1, op2],
    )


def _build_schedule(scenario: Scenario) -> Schedule:
    start = scenario.horizon_start
    sop1 = ScheduledOperation(
        operation_id="op_0001", work_order_id="wo_0001", work_order_code="WO-1",
        machine_id="mch_0001", op_type="laser_cutting", position=0,
        start_min=0, end_min=60, setup_min=10,
        start=start, end=start + timedelta(minutes=60),
    )
    sop2 = ScheduledOperation(
        operation_id="op_0002", work_order_id="wo_0002", work_order_code="WO-2",
        machine_id="mch_0001", op_type="laser_cutting", position=0,
        start_min=60, end_min=120, setup_min=10,
        start=start + timedelta(minutes=60), end=start + timedelta(minutes=120),
    )
    return Schedule(
        scenario_id=scenario.id, solver_status=SolverStatus.OPTIMAL,
        makespan_min=120, objective_value=42.0,
        scheduled_operations=[sop1, sop2],
    )


def test_kpis_match_expected():
    scenario = _build_scenario()
    schedule = _build_schedule(scenario)
    kpi = compute_kpis(scenario, schedule)

    assert kpi.scheduled_orders == 2
    assert kpi.total_orders == 2
    assert kpi.makespan_min == 120
    # WO2 completes at 120 but due at 100 -> 1 of 2 on time.
    assert kpi.on_time_rate == 0.5
    assert kpi.avg_lateness_min == 10.0  # (0 + 20) / 2
    # Machine busy 120 of 120 -> 100% utilisation, and the bottleneck.
    assert kpi.overall_utilisation_pct == 100.0
    assert kpi.bottleneck_machine_id == "mch_0001"
    assert kpi.backlog_size == 0
    # Both ops start on day 1 -> 40kg material.
    assert kpi.tonnage_scheduled_today_kg == 40.0


def test_alerts_flag_late_critical_order():
    scenario = _build_scenario()
    schedule = _build_schedule(scenario)
    alerts = build_alerts(scenario, schedule)
    types = {a.type for a in alerts}
    assert AlertType.LATE_ORDER in types
    late = [a for a in alerts if a.type == AlertType.LATE_ORDER]
    assert any("WO-2" in a.message for a in late)


def test_alerts_on_infeasible_status():
    scenario = _build_scenario()
    schedule = Schedule(
        scenario_id=scenario.id, solver_status=SolverStatus.INFEASIBLE
    )
    alerts = build_alerts(scenario, schedule)
    assert any(a.type == AlertType.INFEASIBLE for a in alerts)
