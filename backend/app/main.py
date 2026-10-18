from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.models.message import Message, MessagePriority
from app.models.node import Node, NodeType
from app.network.topology import NetworkTopology
from app.state import ApplicationState


app = FastAPI(
    title="Disaster-Resilient Emergency Communication Network",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MoveRequest(BaseModel):
    x: float
    y: float


class RecoveryRequest(BaseModel):
    elapsed_time: float = 0.0


class MessageRequest(BaseModel):
    message_id: str
    source_id: str
    destination_id: str
    content: str
    priority: MessagePriority


COMMUNICATION_RANGE = 16.0


def build_initial_network() -> NetworkTopology:
    """Build the default 5-node fully connected demo topology."""

    topology = NetworkTopology()

    topology.add_node(
        Node("R01", NodeType.RESCUE_TEAM, x=0, y=0)
    )

    topology.add_node(
        Node(
            "R02",
            NodeType.RESCUE_TEAM,
            x=5,
            y=0,
            speed=5,
            direction=180,
        )
    )

    topology.add_node(
        Node("R03", NodeType.DRONE, x=10, y=0)
    )

    topology.add_node(
        Node("R04", NodeType.FIRE_RESCUE, x=5, y=5)
    )

    topology.add_node(
        Node("C01", NodeType.COMMAND_CENTER, x=15, y=0)
    )

    # Fully connected mesh
    topology.connect_nodes("R01", "R02")
    topology.connect_nodes("R01", "R03")
    topology.connect_nodes("R01", "R04")
    topology.connect_nodes("R01", "C01")

    topology.connect_nodes("R02", "R03")
    topology.connect_nodes("R02", "R04")
    topology.connect_nodes("R02", "C01")

    topology.connect_nodes("R03", "R04")
    topology.connect_nodes("R03", "C01")

    topology.connect_nodes("R04", "C01")

    return topology


state = ApplicationState(build_initial_network(), COMMUNICATION_RANGE)

@app.get("/")
def health_check() -> dict:
    """Return a basic API health response."""

    return {
        "status": "online",
        "service": "disaster-resilient-network",
    }


@app.get("/network/status")
def network_status() -> dict:
    """Return the current network health summary."""

    return state.monitor.get_network_summary()


@app.get("/network/nodes")
def network_nodes() -> list[dict]:
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


@app.get("/network/topology")
def network_topology() -> dict:
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


@app.get("/network/events")
def network_events() -> list[dict]:
    """Return recorded network events in chronological order."""

    return [
        {
            "event_type": event.event_type,
            "message": event.message,
            "timestamp": event.timestamp.isoformat(),
        }
        for event in state.event_log.get_events()
    ]


@app.post("/network/reset")
def reset_network() -> dict:
    """Reset the simulation back to its initial topology and state."""

    state.reset(build_initial_network())

    return {
        "status": "reset",
        "nodes": len(state.network.get_all_nodes()),
    }


@app.post("/network/nodes/{node_id}/fail")
def fail_node(node_id: str) -> dict:
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


@app.post("/network/nodes/{node_id}/recover")
def recover_node(node_id: str) -> dict:
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


@app.post("/network/nodes/{node_id}/move")
def move_node(
    node_id: str,
    request: MoveRequest,
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


@app.post("/network/nodes/{node_id}/recover-lost")
def recover_lost_node(
    node_id: str,
    request: RecoveryRequest,
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


@app.get("/network/nodes/{node_id}/recovery")
def recovery_status(node_id: str) -> dict:
    """Return the current recovery information for a node."""

    try:
        return state.recovery_manager.get_status(node_id)

    except ValueError as error:
        return {
            "error": str(error),
        }


@app.get("/network/nodes/{node_id}/helper-candidates")
def helper_candidates(
    node_id: str,
    predicted_x: float,
    predicted_y: float,
) -> list[dict]:
    """Return every online node ranked as a candidate recovery helper."""

    return state.recovery_manager.helper_selector.rank_helpers(
        node_id,
        predicted_x,
        predicted_y,
    )


@app.get("/network/route/{source_id}/{destination_id}")
def network_route(
    source_id: str,
    destination_id: str,
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


@app.post("/network/messages/send")
def send_message(request: MessageRequest) -> dict:
    """Send an emergency message through the mesh network."""

    message = Message(
        message_id=request.message_id,
        source_id=request.source_id,
        destination_id=request.destination_id,
        content=request.content,
        priority=request.priority,
    )

    try:
        route = state.message_service.send_message(message)

    except ValueError as error:
        return {
            "message_id": message.message_id,
            "source": message.source_id,
            "destination": message.destination_id,
            "status": "failed",
            "error": str(error),
        }

    return {
        "message_id": message.message_id,
        "source": message.source_id,
        "destination": message.destination_id,
        "content": message.content,
        "priority": message.priority.value,
        "status": "delivered",
        "route": route,
    }