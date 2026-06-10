"""Solver execution endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_scenario_service, get_scheduling_service
from app.api.schemas import SolveRequest
from app.models.scheduling import SolverResult
from app.services.scenario_service import ScenarioService
from app.services.scheduling_service import SchedulingService

router = APIRouter(tags=["solver"])


@router.post("/solve", response_model=SolverResult)
def solve(
    req: SolveRequest,
    scenarios: ScenarioService = Depends(get_scenario_service),
    scheduler: SchedulingService = Depends(get_scheduling_service),
) -> SolverResult:
    scenario = scenarios.get_scenario(req.scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scheduler.solve(scenario, req.config)
