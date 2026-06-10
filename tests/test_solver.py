"""Solver feasibility and constraint-satisfaction tests."""

from __future__ import annotations

from collections import defaultdict

from app.models.enums import ScenarioSize, SolverStatus
from app.models.scheduling import SolverConfig
from app.simulator.generator import SyntheticDataGenerator
from app.solver.cp_sat_solver import solve_scenario


def _solve(seed: int, size: ScenarioSize, **cfg):
    scenario = SyntheticDataGenerator.for_size(seed=seed, size=size).generate()
    result = solve_scenario(scenario, SolverConfig(time_limit_s=15.0, **cfg))
    return scenario, result


def test_small_scenario_is_feasible():
    _, result = _solve(7, ScenarioSize.SMALL)
    assert result.feasible
    assert result.status in (SolverStatus.OPTIMAL, SolverStatus.FEASIBLE)
    assert result.schedule.scheduled_operations


def test_all_operations_scheduled_once_on_eligible_machine():
    scenario, result = _solve(7, ScenarioSize.SMALL)
    op_by_id = {o.id: o for o in scenario.operations}
    seen = set()
    for sop in result.schedule.scheduled_operations:
        assert sop.operation_id not in seen, "operation scheduled twice"
        seen.add(sop.operation_id)
        op = op_by_id[sop.operation_id]
        assert sop.machine_id in op.eligible_machine_ids
    assert seen == set(op_by_id)


def test_precedence_respected():
    scenario, result = _solve(7, ScenarioSize.SMALL)
    starts = {s.operation_id: s.start_min for s in result.schedule.scheduled_operations}
    ends = {s.operation_id: s.end_min for s in result.schedule.scheduled_operations}
    for op in scenario.operations:
        if op.predecessor_id:
            assert starts[op.id] >= ends[op.predecessor_id]


def test_no_machine_overlap():
    _, result = _solve(7, ScenarioSize.SMALL)
    by_machine = defaultdict(list)
    for s in result.schedule.scheduled_operations:
        by_machine[s.machine_id].append((s.start_min, s.end_min))
    for machine_id, intervals in by_machine.items():
        intervals.sort()
        for (s1, e1), (s2, e2) in zip(intervals, intervals[1:]):
            assert e1 <= s2, f"overlap on {machine_id}: {e1} > {s2}"


def test_empty_scenario_returns_empty_status():
    scenario = SyntheticDataGenerator.for_size(
        seed=1, size=ScenarioSize.SMALL
    ).generate()
    scenario.operations = []
    result = solve_scenario(scenario, SolverConfig(time_limit_s=2.0))
    assert result.status == SolverStatus.EMPTY
    assert result.feasible
    assert not result.schedule.scheduled_operations


def test_disabling_maintenance_still_feasible():
    _, result = _solve(
        4, ScenarioSize.SMALL, enable_maintenance=False, enable_breakdowns=False
    )
    assert result.feasible


def test_medium_scenario_solves_within_time_limit():
    _, result = _solve(2, ScenarioSize.MEDIUM)
    assert result.feasible
    assert result.wall_time_s <= 20.0
