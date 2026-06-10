"""Derive dashboard KPIs and alerts from a scenario and its schedule.

These are deliberately pure functions: given the same ``Scenario`` and
``Schedule`` they always return the same ``KPI``/``Alert`` list, which keeps the
analytics layer trivially testable and free of side effects.
"""

from __future__ import annotations

from datetime import timedelta

from app.models.enums import AlertSeverity, AlertType, SolverStatus
from app.models.kpi import Alert, KPI, MachineUtilisation
from app.models.scenario import Scenario
from app.models.scheduling import Schedule


def compute_kpis(scenario: Scenario, schedule: Schedule) -> KPI:
    """Compute headline KPIs for a solved scenario."""
    completions = schedule.completion_min_by_work_order()
    scheduled_orders = len(completions)
    total_orders = len(scenario.work_orders)

    # On-time / lateness against due dates.
    lateness: list[int] = []
    on_time = 0
    for wo in scenario.work_orders:
        if wo.id not in completions:
            continue
        due_min = scenario.datetime_to_minutes(wo.due_date)
        late = completions[wo.id] - due_min
        lateness.append(max(0, late))
        if late <= 0:
            on_time += 1

    on_time_rate = (on_time / scheduled_orders) if scheduled_orders else 0.0
    avg_lateness = (sum(lateness) / len(lateness)) if lateness else 0.0

    # Machine utilisation over the planning horizon.
    util = _machine_utilisation(scenario, schedule)
    overall = (
        sum(u.utilisation_pct for u in util) / len(util) if util else 0.0
    )
    bottleneck = max(util, key=lambda u: u.utilisation_pct).machine_id if util else None

    backlog = total_orders - scheduled_orders
    tonnage_today = _tonnage_scheduled_today(scenario, schedule)

    alerts = build_alerts(scenario, schedule)

    return KPI(
        scenario_id=scenario.id,
        schedule_id=schedule.id,
        scheduled_orders=scheduled_orders,
        total_orders=total_orders,
        on_time_rate=round(on_time_rate, 4),
        avg_lateness_min=round(avg_lateness, 2),
        makespan_min=schedule.makespan_min,
        overall_utilisation_pct=round(overall, 2),
        machine_utilisation=util,
        bottleneck_machine_id=bottleneck,
        backlog_size=backlog,
        tonnage_scheduled_today_kg=round(tonnage_today, 2),
        num_alerts=len(alerts),
    )


def _machine_utilisation(
    scenario: Scenario, schedule: Schedule
) -> list[MachineUtilisation]:
    available = max(1, schedule.makespan_min or scenario.horizon_minutes)
    out: list[MachineUtilisation] = []
    for machine in scenario.machines:
        busy = sum(
            op.end_min - op.start_min
            for op in schedule.operations_for_machine(machine.id)
        )
        out.append(
            MachineUtilisation(
                machine_id=machine.id,
                machine_name=machine.name,
                busy_min=busy,
                available_min=available,
                utilisation_pct=round(100.0 * busy / available, 2),
            )
        )
    return out


def _tonnage_scheduled_today(scenario: Scenario, schedule: Schedule) -> float:
    """Material mass (kg) of operations starting on the horizon's first day."""
    day_end = scenario.horizon_start + timedelta(days=1)
    day_end_min = scenario.datetime_to_minutes(day_end)
    op_material = {op.id: op.material_kg for op in scenario.operations}
    total = 0.0
    for sop in schedule.scheduled_operations:
        if sop.start_min < day_end_min:
            total += op_material.get(sop.operation_id, 0.0)
    return total


def build_alerts(scenario: Scenario, schedule: Schedule) -> list[Alert]:
    """Surface late orders, bottlenecks, material shortages, and infeasibility."""
    alerts: list[Alert] = []

    if schedule.solver_status in (
        SolverStatus.INFEASIBLE,
        SolverStatus.UNKNOWN,
        SolverStatus.MODEL_INVALID,
    ):
        alerts.append(
            Alert(
                severity=AlertSeverity.CRITICAL,
                type=AlertType.INFEASIBLE,
                message=(
                    f"Solver returned status '{schedule.solver_status.value}'; "
                    "no usable schedule was produced."
                ),
                entity_refs=[scenario.id],
            )
        )
        return alerts

    # Late orders.
    completions = schedule.completion_min_by_work_order()
    for wo in scenario.work_orders:
        if wo.id not in completions:
            continue
        due_min = scenario.datetime_to_minutes(wo.due_date)
        late = completions[wo.id] - due_min
        if late > 0:
            alerts.append(
                Alert(
                    severity=AlertSeverity.WARNING
                    if wo.priority.weight < 4
                    else AlertSeverity.CRITICAL,
                    type=AlertType.LATE_ORDER,
                    message=(
                        f"Work order {wo.code} is late by {late} min "
                        f"(priority={wo.priority.value})."
                    ),
                    entity_refs=[wo.id],
                )
            )

    # Bottleneck machine (highest utilisation above a threshold).
    util = _machine_utilisation(scenario, schedule)
    if util:
        top = max(util, key=lambda u: u.utilisation_pct)
        if top.utilisation_pct >= 85.0:
            alerts.append(
                Alert(
                    severity=AlertSeverity.WARNING,
                    type=AlertType.BOTTLENECK,
                    message=(
                        f"{top.machine_name} is a bottleneck at "
                        f"{top.utilisation_pct:.0f}% utilisation."
                    ),
                    entity_refs=[top.machine_id],
                )
            )

    # Material shortage: required mass per material vs available stock.
    required: dict[str, float] = {}
    product_material = {p.id: p.material_id for p in scenario.products}
    wo_product = {w.id: w.product_id for w in scenario.work_orders}
    for op in scenario.operations:
        product_id = wo_product.get(op.work_order_id)
        material_id = product_material.get(product_id) if product_id else None
        if material_id:
            required[material_id] = required.get(material_id, 0.0) + op.material_kg
    for material in scenario.materials:
        need = required.get(material.id, 0.0)
        if need > material.available_kg:
            alerts.append(
                Alert(
                    severity=AlertSeverity.WARNING,
                    type=AlertType.MATERIAL_SHORTAGE,
                    message=(
                        f"Material {material.name} short: need "
                        f"{need:.0f}kg, have {material.available_kg:.0f}kg."
                    ),
                    entity_refs=[material.id],
                )
            )

    return alerts
