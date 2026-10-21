from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_state
from app.locked_route import LockedRoute
from app.initial_network import COMMUNICATION_RANGE
from app.recovery_requests import MoveRequest, RecoveryRequest
from app.state import ApplicationState


router = APIRouter(route_class=LockedRoute, prefix="/network/nodes", tags=["Recovery"])


@router.post("/{node_id}/move")
def move_node(
    node_id: str,
    request: MoveRequest,
    state: Annotated[ApplicationState, Depends(get_state)],
) -> dict:
    """Move a node and detect communication loss."""

    try:
        lost_detected = state.simulator.move_node(
            node_id,
            request.x,
            request.y,
        )

    except ValueError as error:
        return {
            "error": str(error),
        }

    node = state.network.get_node(node_id)

    state.event_log.record(
        "NODE_MOVED",
        f"{node_id} moved to ({node.x}, {node.y}).",
    )

    if lost_detected:
        state.event_log.record(
            "NODE_LOST",
            f"{node_id} lost communication "
            f"(no reachable neighbor within "
            f"{COMMUNICATION_RANGE} units) and is marked LOST.",
        )

    return {
        "node_id": node_id,
        "x": node.x,
        "y": node.y,
        "speed": node.speed,
        "direction": node.direction,
        "status": node.status.value,
        "lost_detected": lost_detected,
        "neighbors": node.neighbors,
    }


@router.post("/{node_id}/recover-lost")
def recover_lost_node(
    node_id: str,
    request: RecoveryRequest,
    state: Annotated[ApplicationState, Depends(get_state)],
) -> dict:
    """Recover a lost node using prediction and collaborative search."""

    try:
        result = state.recovery_manager.recover(
            node_id,
            request.elapsed_time,
        )

    except ValueError as error:
        return {
            "error": str(error),
        }

    prediction = result["prediction"]

    state.event_log.record(
        "PREDICTION",
        f"Predicted search area for {node_id}: "
        f"({prediction['predicted_x']:.1f}, "
        f"{prediction['predicted_y']:.1f}), "
        f"radius {prediction['search_radius']:.1f}.",
    )

    state.event_log.record(
        "HELPER_SELECTED",
        f"{result['helper']['node_id']} selected as "
        f"recovery helper for {node_id} "
        f"(score {result['helper']['score']:.2f}).",
    )

    state.event_log.record(
        "ASTAR_SEARCH",
        f"A* search route for "
        f"{result['helper']['node_id']}: "
        f"{' -> '.join(result['search']['route'])}.",
    )

    if result["status"] == "FOUND":

        state.event_log.record(
            "NODE_FOUND",
            f"{node_id} rediscovered.",
        )

        state.event_log.record(
            "TOPOLOGY_REBUILT",
            f"{node_id} reconnected to: "
            f"{', '.join(result.get('reconnected_to', [])) or 'none'}.",
        )

    return result


@router.get("/{node_id}/recovery")
def recovery_status(
    node_id: str,
    state: Annotated[ApplicationState, Depends(get_state)],
) -> dict:
    """Return the current recovery information for a node."""

    try:
        return state.recovery_manager.get_status(node_id)

    except ValueError as error:
        return {
            "error": str(error),
        }


@router.get("/{node_id}/helper-candidates")
def helper_candidates(
    node_id: str,
    predicted_x: float,
    predicted_y: float,
    state: Annotated[ApplicationState, Depends(get_state)],
) -> list[dict]:
    """Return every online node ranked as a candidate recovery helper."""

    return state.recovery_manager.helper_selector.rank_helpers(
        node_id,
        predicted_x,
        predicted_y,
    )
