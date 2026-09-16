import pytest

from app.models.node import Node, NodeType
from app.network.self_healing import SelfHealingManager
from app.network.topology import NetworkTopology
from app.simulation.simulator import NetworkSimulator


def create_network() -> NetworkTopology:
    network = NetworkTopology()

    nodes = [
        ("R01", NodeType.RESCUE_TEAM),
        ("R02", NodeType.RESCUE_TEAM),
        ("R03", NodeType.RESCUE_TEAM),
        ("R04", NodeType.DRONE),
        ("C01", NodeType.COMMAND_CENTER),
    ]

    for node_id, node_type in nodes:
        network.add_node(Node(node_id, node_type))

    network.connect_nodes("R01", "R02")
    network.connect_nodes("R02", "R03")
    network.connect_nodes("R03", "C01")
    network.connect_nodes("R01", "R04")
    network.connect_nodes("R04", "R03")

    return network


def test_normal_route():
    network = create_network()
    manager = SelfHealingManager(network)

    assert manager.recover_route("R01", "C01") == [
        "R01",
        "R02",
        "R03",
        "C01",
    ]


def test_route_recovers_after_node_failure():
    network = create_network()
    simulator = NetworkSimulator(network)
    manager = SelfHealingManager(network)

    simulator.fail_node("R02")

    assert manager.recover_route("R01", "C01") == [
        "R01",
        "R04",
        "R03",
        "C01",
    ]


def test_no_route_after_multiple_failures():
    network = create_network()
    simulator = NetworkSimulator(network)
    manager = SelfHealingManager(network)

    simulator.fail_node("R02")
    simulator.fail_node("R04")

    with pytest.raises(ValueError, match="No route exists"):
        manager.recover_route("R01", "C01")