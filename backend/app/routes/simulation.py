import math
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator

from app.dependencies import get_state
from app.locked_route import LockedRoute
from app.state import ApplicationState


router = APIRouter(
    route_class=LockedRoute,
    prefix="/simulation",
    tags=["Simulation"],
)


class StepRequest(BaseModel):
    elapsed: float

    @field_validator("elapsed")
    @classmethod
    def validate_elapsed(cls, value: float) -> float:
        if not math.isfinite(value) or value < 0:
            raise ValueError("Elapsed time must be finite and nonnegative.")
        return value


@router.get("/status")
def simulation_status(
    state: Annotated[ApplicationState, Depends(get_state)],
) -> dict:
    return {
        "simulation_time": state.engine.simulation_time,
        "paused": state.driver.paused,
        "speed": state.driver.speed,
        "fixed_dt": state.driver.fixed_dt,
        "moving_nodes": sorted(state.engine._moving_nodes),
    }


@router.post("/nodes/{node_id}/start")
def start_movement(
    node_id: str,
    state: Annotated[ApplicationState, Depends(get_state)],
) -> dict:
    try:
        state.engine.start_movement(node_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {"node_id": node_id, "moving": True}


@router.post("/nodes/{node_id}/stop")
def stop_movement(
    node_id: str,
    state: Annotated[ApplicationState, Depends(get_state)],
) -> dict:
    try:
        state.engine.stop_movement(node_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {"node_id": node_id, "moving": False}


@router.post("/step")
def advance_simulation(
    request: StepRequest,
    state: Annotated[ApplicationState, Depends(get_state)],
) -> dict:
    previous_time = state.engine.simulation_time
    steps = state.driver.update(request.elapsed)

    return {
        "steps": steps,
        "advanced_time": state.engine.simulation_time - previous_time,
        "simulation_time": state.engine.simulation_time,
    }
