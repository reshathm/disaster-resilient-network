from app.models.node import Node, NodeType
from app.network.monitor import NetworkMonitor
from app.network.topology import NetworkTopology
from app.simulation.simulator import NetworkSimulator


def create_network() -> NetworkTopology:
    network = NetworkTopology()

    network.add_node(Node("R01", NodeType.RESCUE_TEAM))
    network.add_node(Node("R02", NodeType.DRONE))
    network.add_node(Node("C01", NodeType.COMMAND_CENTER))

    return network


def test_get_online_nodes():
    network = create_network()
    monitor = NetworkMonitor(network)

    assert monitor.get_online_nodes() == [
        "R01",
        "R02",
        "C01",
    ]


def test_get_offline_nodes():
    network = create_network()
    simulator = NetworkSimulator(network)
    monitor = NetworkMonitor(network)

    simulator.fail_node("R02")

    assert monitor.get_offline_nodes() == ["R02"]


def test_network_summary():
    network = create_network()
    simulator = NetworkSimulator(network)
    monitor = NetworkMonitor(network)

    simulator.fail_node("R02")

    assert monitor.get_network_summary() == {
        "total_nodes": 3,
        "online_nodes": 2,
        "offline_nodes": 1,
    }