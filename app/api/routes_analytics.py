"""KPI and alert endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import (
    get_analytics_service,
    get_scenario_service,
    get_scheduling_service,
)
from app.api.schemas import AlertsResponse, KPIResponse
from app.models.scenario import Scenario
from app.models.scheduling import Schedule
from app.services.analytics_service import AnalyticsService
from app.services.scenario_service import ScenarioService
from app.services.scheduling_service import SchedulingService

router = APIRouter(tags=["analytics"])


def _resolve(
    scenario_id: str | None,
    schedule_id: str | None,
    scenarios: ScenarioService,
    scheduler: SchedulingService,
) -> tuple[Scenario, Schedule]:
    """Resolve a (scenario, schedule) pair from either id, or raise 4xx."""
    if not scenario_id and not schedule_id:
        raise HTTPException(
            status_code=400, detail="Provide scenario_id or schedule_id"
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
    return scenario, schedule


@router.get("/kpis", response_model=KPIResponse)
def get_kpis(
    scenario_id: str | None = Query(None),
    schedule_id: str | None = Query(None),
    scenarios: ScenarioService = Depends(get_scenario_service),
    scheduler: SchedulingService = Depends(get_scheduling_service),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> KPIResponse:
    scenario, schedule = _resolve(scenario_id, schedule_id, scenarios, scheduler)
    return KPIResponse(**analytics.kpis(scenario, schedule).model_dump())


@router.get("/alerts", response_model=AlertsResponse)
def get_alerts(
    scenario_id: str | None = Query(None),
    schedule_id: str | None = Query(None),
    scenarios: ScenarioService = Depends(get_scenario_service),
    scheduler: SchedulingService = Depends(get_scheduling_service),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> AlertsResponse:
    scenario, schedule = _resolve(scenario_id, schedule_id, scenarios, scheduler)
    return AlertsResponse(
        scenario_id=scenario.id,
        schedule_id=schedule.id,
        alerts=analytics.alerts(scenario, schedule),
    )
