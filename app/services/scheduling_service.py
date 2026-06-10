"""Solve scenarios and persist the resulting schedules."""

from __future__ import annotations

from app.models.scenario import Scenario
from app.models.scheduling import Schedule, SolverConfig, SolverResult
from app.repository.base import ScheduleRepository
from app.solver.cp_sat_solver import solve_scenario


class SchedulingService:
    def __init__(self, repository: ScheduleRepository) -> None:
        self._repo = repository

    def solve(
        self, scenario: Scenario, config: SolverConfig | None = None
    ) -> SolverResult:
        """Run the CP-SAT solver and persist the schedule."""
        result = solve_scenario(scenario, config or SolverConfig())
        self._repo.save(result.schedule)
        return result

    def get_schedule(self, schedule_id: str) -> Schedule | None:
        return self._repo.get(schedule_id)

    def get_latest_for_scenario(self, scenario_id: str) -> Schedule | None:
        return self._repo.get_latest_for_scenario(scenario_id)
