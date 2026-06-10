"""Machine and work-order listing endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_scenario_service
from app.models.domain import Machine
from app.services.scenario_service import ScenarioService

router = APIRouter(tags=["resources"])


def _require_scenario(service: ScenarioService, scenario_id: str):
    scenario = service.get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.get("/machines", response_model=list[Machine])
def get_machines(
    scenario_id: str = Query(..., description="Scenario to read machines from"),
    service: ScenarioService = Depends(get_scenario_service),
) -> list[Machine]:
    return _require_scenario(service, scenario_id).machines
