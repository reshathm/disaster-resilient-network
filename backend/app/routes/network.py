from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_state
from app.initial_network import build_initial_network
from app.state import ApplicationState


router = APIRouter(prefix="/network", tags=["Network"])


@router.get("/status")
def network_status(
    state: Annotated[ApplicationState, Depends(get_state)],
) -> dict:
    """Return the current network health summary."""
    return state.monitor.get_network_summary()


@router.get("/nodes")
def network_nodes(
    state: Annotated[ApplicationState, Depends(get_state)],
) -> list[dict]:
    """Return the current state of all network nodes."""

    return [
        {
            "node_id": node.node_id,
            "type": node.node_type.value,
            "status": node.status.value,
            "battery": node.battery,
            "signal_strength": node.signal_strength,
            "x": node.x,
            "y": node.y,
            "speed": node.speed,
            "direction": node.direction,
        }
        for node in state.network.get_all_nodes()
    ]


@router.get("/topology")
def network_topology(
    state: Annotated[ApplicationState, Depends(get_state)],
) -> dict:
    """Return the current network nodes and connections."""

    connections = []

    for node in state.network.get_all_nodes():
        for neighbor_id in node.neighbors:
            if node.node_id < neighbor_id:
                connections.append(
                    {
                        "source": node.node_id,
                        "target": neighbor_id,
                    }
                )

    return {
        "nodes": [
            {
                "node_id": node.node_id,
                "status": node.status.value,
            }
            for node in state.network.get_all_nodes()
        ],
        "connections": connections,
    }


@router.get("/events")
def network_events(
    state: Annotated[ApplicationState, Depends(get_state)],
) -> list[dict]:
    """Return recorded network events in chronological order."""

    return [
        {
            "event_type": event.event_type,
            "message": event.message,
            "timestamp": event.timestamp.isoformat(),
        }
        for event in state.event_log.get_events()
    ]


@router.post("/reset")
def reset_network(
    state: Annotated[ApplicationState, Depends(get_state)],
) -> dict:
    """Reset the simulation back to its initial topology and state."""

    state.reset(build_initial_network())

    return {
        "status": "reset",
        "nodes": len(state.network.get_all_nodes()),
    }


@router.post("/nodes/{node_id}/fail")
def fail_node(
    node_id: str,
    state: Annotated[ApplicationState, Depends(get_state)],
) -> dict:
    """Simulate a network node failure."""

    try:
        state.simulator.fail_node(node_id)

    except ValueError as error:
        return {
            "error": str(error),
        }

    state.event_log.record(
        "NODE_OFFLINE",
        f"{node_id} failed and went OFFLINE.",
    )

    return {
        "node_id": node_id,
        "status": "offline",
    }


@router.post("/nodes/{node_id}/recover")
def recover_node(
    node_id: str,
    state: Annotated[ApplicationState, Depends(get_state)],
) -> dict:
    """Simulate a network node recovering."""

    try:
        state.simulator.recover_node(node_id)

    except ValueError as error:
        return {
            "error": str(error),
        }

    state.event_log.record(
        "NODE_ONLINE",
        f"{node_id} recovered and is back ONLINE.",
    )

    return {
        "node_id": node_id,
        "status": "online",
    }


@router.get("/route/{source_id}/{destination_id}")
def network_route(
    source_id: str,
    destination_id: str,
    state: Annotated[ApplicationState, Depends(get_state)],
) -> dict:
    """Find the current route between two network nodes."""

    try:
        route = state.self_healing.recover_route(
            source_id,
            destination_id,
        )

    except ValueError as error:
        return {
            "source": source_id,
            "destination": destination_id,
            "error": str(error),
        }

    return {
        "source": source_id,
        "destination": destination_id,
        "route": route,
    }
