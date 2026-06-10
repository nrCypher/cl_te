"""CP-SAT scheduling model for the sheet-metal workshop.

Model overview (all times are integer minutes from ``scenario.horizon_start``):

* Each operation gets one *optional interval per eligible machine*. A boolean
  presence literal selects exactly one machine (alternative-resource pattern).
* Operation start/end vars are linked to the chosen alternative; the chosen
  duration is the nominal time rescaled by the machine ``speed_factor``.
* Precedence is a simple ``start(op) >= end(predecessor)`` chain per work order.
* Each machine enforces ``AddNoOverlap`` over its operation intervals plus fixed
  blocked intervals for maintenance and breakdowns (toggled via SolverConfig).
* Objective = weighted sum of makespan, total tardiness, priority-weighted
  tardiness, and peak machine load (utilisation balance).

The solver never raises on an unsolvable model: it maps the OR-Tools status to a
:class:`SolverStatus` and returns an empty (but well-formed) schedule when no
assignment is found.
"""

from __future__ import annotations

import math

from ortools.sat.python import cp_model

from app.models.enums import SolverStatus
from app.models.scenario import Scenario
from app.models.scheduling import (
    Schedule,
    ScheduledOperation,
    SolverConfig,
    SolverResult,
)

_STATUS_MAP = {
    cp_model.OPTIMAL: SolverStatus.OPTIMAL,
    cp_model.FEASIBLE: SolverStatus.FEASIBLE,
    cp_model.INFEASIBLE: SolverStatus.INFEASIBLE,
    cp_model.MODEL_INVALID: SolverStatus.MODEL_INVALID,
    cp_model.UNKNOWN: SolverStatus.UNKNOWN,
}


def _effective_duration(nominal_min: int, speed_factor: float) -> int:
    """Rescale nominal time by machine speed (>1 == faster)."""
    return max(1, math.ceil(nominal_min / max(0.01, speed_factor)))


def solve_scenario(scenario: Scenario, config: SolverConfig) -> SolverResult:
    """Build and solve the CP-SAT model, returning a :class:`SolverResult`."""

    operations = scenario.operations
    if not operations:
        empty = Schedule(scenario_id=scenario.id, solver_status=SolverStatus.EMPTY)
        return SolverResult(
            schedule=empty,
            status=SolverStatus.EMPTY,
            feasible=True,
            objective_value=0.0,
            wall_time_s=0.0,
            message="Scenario has no operations to schedule.",
        )

    model = cp_model.CpModel()
    machines = {m.id: m for m in scenario.machines}

    # --- horizon upper bound that always admits a serial schedule --------
    total_nominal = sum(op.duration_min for op in operations)
    max_release = max(
        scenario.datetime_to_minutes(wo.release_date)
        for wo in scenario.work_orders
    )
    blocked_total = 0
    if config.enable_maintenance:
        blocked_total += sum(
            mw.end_min - mw.start_min for mw in scenario.maintenance_windows
        )
    if config.enable_breakdowns:
        blocked_total += sum(
            bd.end_min - bd.start_min for bd in scenario.breakdowns
        )
    horizon = max(scenario.horizon_minutes, 0) + total_nominal + max(0, max_release)
    horizon += blocked_total + 1

    # --- per-operation start/end vars and per-machine alternatives -------
    op_start: dict[str, cp_model.IntVar] = {}
    op_end: dict[str, cp_model.IntVar] = {}
    op_chosen_machine: dict[str, dict[str, cp_model.IntVar]] = {}
    machine_intervals: dict[str, list] = {mid: [] for mid in machines}
    machine_load_terms: dict[str, list] = {mid: [] for mid in machines}

    for op in operations:
        s = model.NewIntVar(0, horizon, f"start_{op.id}")
        e = model.NewIntVar(0, horizon, f"end_{op.id}")
        op_start[op.id] = s
        op_end[op.id] = e

        presence_lits = []
        op_chosen_machine[op.id] = {}
        for machine_id in op.eligible_machine_ids:
            machine = machines.get(machine_id)
            if machine is None:
                continue
            dur = _effective_duration(op.duration_min, machine.speed_factor)
            lit = model.NewBoolVar(f"on_{op.id}_{machine_id}")
            a_start = model.NewIntVar(0, horizon, f"as_{op.id}_{machine_id}")
            a_end = model.NewIntVar(0, horizon, f"ae_{op.id}_{machine_id}")
            interval = model.NewOptionalIntervalVar(
                a_start, dur, a_end, lit, f"iv_{op.id}_{machine_id}"
            )
            # Link alternative to the operation's shared start/end when chosen.
            model.Add(a_start == s).OnlyEnforceIf(lit)
            model.Add(a_end == e).OnlyEnforceIf(lit)

            machine_intervals[machine_id].append(interval)
            machine_load_terms[machine_id].append((dur, lit))
            op_chosen_machine[op.id][machine_id] = lit
            presence_lits.append(lit)

        if not presence_lits:
            # Defensive: an operation with no eligible machine is infeasible.
            return _infeasible_result(scenario, "Operation without eligible machine")
        model.AddExactlyOne(presence_lits)

    # --- precedence + release constraints --------------------------------
    op_by_id = {op.id: op for op in operations}
    for op in operations:
        if op.predecessor_id and op.predecessor_id in op_end:
            model.Add(op_start[op.id] >= op_end[op.predecessor_id])
        else:
            wo = scenario.work_order_by_id(op.work_order_id)
            if wo is not None:
                release_min = max(0, scenario.datetime_to_minutes(wo.release_date))
                model.Add(op_start[op.id] >= release_min)

    # --- machine capacity + blocked intervals ----------------------------
    for machine_id, intervals in machine_intervals.items():
        blocked = _blocked_intervals(model, scenario, machine_id, config)
        if intervals or blocked:
            model.AddNoOverlap(intervals + blocked)

    # --- objective terms -------------------------------------------------
    makespan = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(makespan, list(op_end.values()))

    tardiness_terms: list[cp_model.IntVar] = []
    priority_terms: list = []
    for wo in scenario.work_orders:
        wo_ops = scenario.operations_for(wo.id)
        if not wo_ops:
            continue
        completion = model.NewIntVar(0, horizon, f"compl_{wo.id}")
        model.AddMaxEquality(completion, [op_end[o.id] for o in wo_ops])
        due_min = max(0, scenario.datetime_to_minutes(wo.due_date))
        tard = model.NewIntVar(0, horizon, f"tard_{wo.id}")
        # tard = max(0, completion - due)
        model.Add(tard >= completion - due_min)
        tardiness_terms.append(tard)
        priority_terms.append(wo.priority.weight * tard)

    # Peak machine load (utilisation balance): minimise the busiest machine.
    peak_load = model.NewIntVar(0, horizon, "peak_load")
    load_vars: list[cp_model.IntVar] = []
    for machine_id, terms in machine_load_terms.items():
        if not terms:
            continue
        load = model.NewIntVar(0, horizon, f"load_{machine_id}")
        model.Add(load == sum(dur * lit for dur, lit in terms))
        load_vars.append(load)
    if load_vars:
        model.AddMaxEquality(peak_load, load_vars)

    objective = (
        config.weight_makespan * makespan
        + config.weight_tardiness * sum(tardiness_terms)
        + config.weight_priority * sum(priority_terms)
        + config.weight_balance * peak_load
    )
    model.Minimize(objective)

    # --- solve -----------------------------------------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = config.time_limit_s
    solver.parameters.num_search_workers = config.num_workers
    status = solver.Solve(model)
    mapped = _STATUS_MAP.get(status, SolverStatus.UNKNOWN)

    has_solution = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    if not has_solution:
        schedule = Schedule(
            scenario_id=scenario.id,
            solver_status=mapped,
            makespan_min=0,
            objective_value=0.0,
        )
        return SolverResult(
            schedule=schedule,
            status=mapped,
            feasible=False,
            objective_value=0.0,
            wall_time_s=solver.WallTime(),
            message=f"No feasible schedule found (status={mapped.value}).",
        )

    # --- extract solution ------------------------------------------------
    scheduled: list[ScheduledOperation] = []
    for op in operations:
        chosen_machine = None
        for machine_id, lit in op_chosen_machine[op.id].items():
            if solver.BooleanValue(lit):
                chosen_machine = machine_id
                break
        if chosen_machine is None:
            continue
        start_min = solver.Value(op_start[op.id])
        end_min = solver.Value(op_end[op.id])
        wo = op_by_id and scenario.work_order_by_id(op.work_order_id)
        scheduled.append(
            ScheduledOperation(
                operation_id=op.id,
                work_order_id=op.work_order_id,
                work_order_code=wo.code if wo else op.work_order_id,
                machine_id=chosen_machine,
                op_type=op.op_type.value,
                position=op.position,
                start_min=start_min,
                end_min=end_min,
                setup_min=op.setup_min,
                start=scenario.minutes_to_datetime(start_min),
                end=scenario.minutes_to_datetime(end_min),
            )
        )

    schedule = Schedule(
        scenario_id=scenario.id,
        solver_status=mapped,
        makespan_min=solver.Value(makespan),
        objective_value=solver.ObjectiveValue(),
        scheduled_operations=scheduled,
    )
    return SolverResult(
        schedule=schedule,
        status=mapped,
        feasible=True,
        objective_value=solver.ObjectiveValue(),
        wall_time_s=solver.WallTime(),
        message=f"Scheduled {len(scheduled)} operations.",
    )


def _blocked_intervals(
    model: cp_model.CpModel,
    scenario: Scenario,
    machine_id: str,
    config: SolverConfig,
) -> list:
    """Fixed unavailability intervals for a machine (maintenance/breakdown)."""
    blocked = []
    if config.enable_maintenance:
        for mw in scenario.maintenance_windows:
            if mw.machine_id == machine_id and mw.end_min > mw.start_min:
                blocked.append(
                    model.NewIntervalVar(
                        mw.start_min,
                        mw.end_min - mw.start_min,
                        mw.end_min,
                        f"mnt_{mw.id}",
                    )
                )
    if config.enable_breakdowns:
        for bd in scenario.breakdowns:
            if bd.machine_id == machine_id and bd.end_min > bd.start_min:
                blocked.append(
                    model.NewIntervalVar(
                        bd.start_min,
                        bd.end_min - bd.start_min,
                        bd.end_min,
                        f"brk_{bd.id}",
                    )
                )
    return blocked


def _infeasible_result(scenario: Scenario, message: str) -> SolverResult:
    schedule = Schedule(
        scenario_id=scenario.id, solver_status=SolverStatus.INFEASIBLE
    )
    return SolverResult(
        schedule=schedule,
        status=SolverStatus.INFEASIBLE,
        feasible=False,
        objective_value=0.0,
        wall_time_s=0.0,
        message=message,
    )
