"""Work-order listing endpoint (with expanded operations)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.api.deps import get_scenario_service
from app.models.domain import Operation, WorkOrder
from app.services.scenario_service import ScenarioService

router = APIRouter(tags=["resources"])


class WorkOrderWithOperations(BaseModel):
    work_order: WorkOrder
    operations: list[Operation]


@router.get("/work-orders", response_model=list[WorkOrderWithOperations])
def get_work_orders(
    scenario_id: str = Query(...),
    service: ScenarioService = Depends(get_scenario_service),
) -> list[WorkOrderWithOperations]:
    scenario = service.get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return [
        WorkOrderWithOperations(
            work_order=wo, operations=scenario.operations_for(wo.id)
        )
        for wo in scenario.work_orders
    ]
