"""Scenario simulation and retrieval endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_scenario_service
from app.api.schemas import CreateScenarioRequest, SimulateRequest
from app.models.scenario import Scenario, ScenarioSummary
from app.services.scenario_service import ScenarioService

router = APIRouter(tags=["scenarios"])


@router.post("/simulate", response_model=Scenario)
def simulate(
    req: SimulateRequest,
    service: ScenarioService = Depends(get_scenario_service),
) -> Scenario:
    """Generate and persist a synthetic scenario; return the full payload."""
    return service.create_scenario(seed=req.seed, size=req.size, name=req.name)


@router.post("/scenarios", response_model=ScenarioSummary, status_code=201)
def create_scenario(
    req: CreateScenarioRequest,
    service: ScenarioService = Depends(get_scenario_service),
) -> ScenarioSummary:
    """Create a scenario and return a lightweight summary."""
    scenario = service.create_scenario(seed=req.seed, size=req.size, name=req.name)
    return scenario.summary()


@router.get("/scenarios", response_model=list[ScenarioSummary])
def list_scenarios(
    service: ScenarioService = Depends(get_scenario_service),
) -> list[ScenarioSummary]:
    return [s.summary() for s in service.list_scenarios()]


@router.get("/scenarios/{scenario_id}", response_model=Scenario)
def get_scenario(
    scenario_id: str,
    service: ScenarioService = Depends(get_scenario_service),
) -> Scenario:
    scenario = service.get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario
