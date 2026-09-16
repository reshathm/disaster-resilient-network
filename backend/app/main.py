from fastapi import FastAPI
from pydantic import BaseModel

from app.models.message import Message, MessagePriority
from app.models.node import Node, NodeType
from app.network.event_log import EventLog
from app.network.location_tracker import LocationTracker
from app.network.lost_node_recovery import LostNodeRecovery
from app.network.messaging import MessageService
from app.network.monitor import NetworkMonitor
from app.network.self_healing import SelfHealingManager
from app.network.topology import NetworkTopology
from app.simulation.simulator import NetworkSimulator


app = FastAPI(
    title="Disaster-Resilient Emergency Communication Network",
    version="1.0.0",
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


network = NetworkTopology()

r01 = Node(
    "R01",
    NodeType.RESCUE_TEAM,
)

r02 = Node(
    "R02",
    NodeType.RESCUE_TEAM,
    x=0,
    y=0,
    speed=5,
    direction=90,
)

r03 = Node(
    "R03",
    NodeType.DRONE,
)

r04 = Node(
    "R04",
    NodeType.FIRE_RESCUE,
)

c01 = Node(
    "C01",
    NodeType.COMMAND_CENTER,
)

network.add_node(r01)
network.add_node(r02)
network.add_node(r03)
network.add_node(r04)
network.add_node(c01)

network.connect_nodes("R01", "R02")
network.connect_nodes("R02", "R03")
network.connect_nodes("R03", "C01")
network.connect_nodes("R01", "R04")
network.connect_nodes("R04", "R03")


monitor = NetworkMonitor(network)
self_healing = SelfHealingManager(network)

event_log = EventLog()
message_service = MessageService(network, event_log)

location_tracker = LocationTracker()

recovery_manager = LostNodeRecovery(
    network,
    location_tracker,
    communication_range=10.0,
)

simulator = NetworkSimulator(
    network,
    communication_range=10.0,
    recovery_manager=recovery_manager,
    location_tracker=location_tracker,
)


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
    return monitor.get_network_summary()


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
        for node in network.get_all_nodes()
    ]


@app.get("/network/topology")
def network_topology() -> dict:
    """Return the current network nodes and connections."""
    connections = []

    for node in network.get_all_nodes():
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
            for node in network.get_all_nodes()
        ],
        "connections": connections,
    }


@app.post("/network/nodes/{node_id}/fail")
def fail_node(node_id: str) -> dict:
    """Simulate a network node failure."""
    try:
        simulator.fail_node(node_id)
    except ValueError as error:
        return {
            "error": str(error),
        }

    return {
        "node_id": node_id,
        "status": "offline",
    }


@app.post("/network/nodes/{node_id}/recover")
def recover_node(node_id: str) -> dict:
    """Simulate a network node recovering."""
    try:
        simulator.recover_node(node_id)
    except ValueError as error:
        return {
            "error": str(error),
        }

    return {
        "node_id": node_id,
        "status": "online",
    }


@app.post("/network/nodes/{node_id}/move")
def move_node(node_id: str, request: MoveRequest) -> dict:
    """Move a node and detect communication loss."""
    try:
        lost_detected = simulator.move_node(
            node_id,
            request.x,
            request.y,
        )
    except ValueError as error:
        return {
            "error": str(error),
        }

    node = network.get_node(node_id)

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
        result = recovery_manager.recover(
            node_id,
            request.elapsed_time,
        )
    except ValueError as error:
        return {
            "error": str(error),
        }

    return result


@app.get("/network/nodes/{node_id}/recovery")
def recovery_status(node_id: str) -> dict:
    """Return the current recovery information for a node."""
    try:
        return recovery_manager.get_status(node_id)
    except ValueError as error:
        return {
            "error": str(error),
        }


@app.get("/network/route/{source_id}/{destination_id}")
def network_route(source_id: str, destination_id: str) -> dict:
    """Find the current route between two network nodes."""
    route = self_healing.recover_route(
        source_id,
        destination_id,
    )

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

    route = message_service.send_message(message)

    return {
        "message_id": message.message_id,
        "source": message.source_id,
        "destination": message.destination_id,
        "content": message.content,
        "priority": message.priority.value,
        "status": "delivered",
        "route": route,
    }