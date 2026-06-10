"""Schedule retrieval endpoint (Gantt-ready)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_scenario_service, get_scheduling_service
from app.api.presenters import to_schedule_response
from app.api.schemas import ScheduleResponse
from app.services.scenario_service import ScenarioService
from app.services.scheduling_service import SchedulingService

router = APIRouter(tags=["schedule"])


@router.get("/schedule", response_model=ScheduleResponse)
def get_schedule(
    scenario_id: str | None = Query(None),
    schedule_id: str | None = Query(None),
    scenarios: ScenarioService = Depends(get_scenario_service),
    scheduler: SchedulingService = Depends(get_scheduling_service),
) -> ScheduleResponse:
    """Return a schedule by id, or the latest schedule for a scenario."""
    if not scenario_id and not schedule_id:
        raise HTTPException(
            status_code=400,
            detail="Provide either scenario_id or schedule_id",
        )

    if schedule_id:
        schedule = scheduler.get_schedule(schedule_id)
        if schedule is None:
            raise HTTPException(status_code=404, detail="Schedule not found")
        scenario_id = schedule.scenario_id
    else:
        schedule = scheduler.get_latest_for_scenario(scenario_id)
        if schedule is None:
            raise HTTPException(
                status_code=404,
                detail="No schedule for scenario; call POST /solve first",
            )

    scenario = scenarios.get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return to_schedule_response(scenario, schedule)
