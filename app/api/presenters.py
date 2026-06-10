"""Pure presentation helpers that shape domain models into API DTOs.

Grouping a flat schedule into machine lanes is view logic, kept out of both the
services (which stay storage/solver oriented) and the route handlers (which stay
thin). One place to change if the Gantt contract changes.
"""

from __future__ import annotations

from app.api.schemas import GanttRow, ScheduleResponse
from app.models.scenario import Scenario
from app.models.scheduling import Schedule


def to_schedule_response(
    scenario: Scenario, schedule: Schedule
) -> ScheduleResponse:
    rows: list[GanttRow] = []
    for machine in scenario.machines:
        rows.append(
            GanttRow(
                machine_id=machine.id,
                machine_name=machine.name,
                machine_type=machine.type.value,
                operations=schedule.operations_for_machine(machine.id),
            )
        )
    return ScheduleResponse(
        schedule_id=schedule.id,
        scenario_id=schedule.scenario_id,
        solver_status=schedule.solver_status,
        makespan_min=schedule.makespan_min,
        objective_value=schedule.objective_value,
        horizon_start=scenario.horizon_start,
        horizon_minutes=scenario.horizon_minutes,
        rows=rows,
    )
