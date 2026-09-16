from fastapi import FastAPI

from app.models.node import Node, NodeType
from app.network.monitor import NetworkMonitor
from app.network.topology import NetworkTopology
from app.simulation.simulator import NetworkSimulator
from app.network.self_healing import SelfHealingManager


app = FastAPI(
    title="Disaster-Resilient Emergency Communication Network",
    version="1.0.0",
)


network = NetworkTopology()

network.add_node(Node("R01", NodeType.RESCUE_TEAM))
network.add_node(Node("R02", NodeType.RESCUE_TEAM))
network.add_node(Node("R03", NodeType.DRONE))
network.add_node(Node("R04", NodeType.FIRE_RESCUE))
network.add_node(Node("C01", NodeType.COMMAND_CENTER))

network.connect_nodes("R01", "R02")
network.connect_nodes("R02", "R03")
network.connect_nodes("R03", "C01")
network.connect_nodes("R01", "R04")
network.connect_nodes("R04", "R03")

monitor = NetworkMonitor(network)
simulator = NetworkSimulator(network)
self_healing = SelfHealingManager(network)

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

@app.get("/network/route/{source_id}/{destination_id}")
def network_route(source_id: str, destination_id: str) -> dict:
    """Find the current route between two network nodes."""
    route = self_healing.recover_route(source_id, destination_id)

    return {
        "source": source_id,
        "destination": destination_id,
        "route": route,
    }