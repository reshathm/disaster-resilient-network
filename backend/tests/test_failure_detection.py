import pytest

from app.models.node import Node, NodeType
from app.network.failure_detection import FailureDetector
from app.network.topology import NetworkTopology
from app.simulation.simulator import NetworkSimulator


def create_network() -> NetworkTopology:
    network = NetworkTopology()

    network.add_node(Node("R01", NodeType.RESCUE_TEAM))
    network.add_node(Node("R02", NodeType.DRONE))
    network.add_node(Node("R03", NodeType.COMMAND_CENTER))

    return network


def test_detect_failed_node():
    network = create_network()
    simulator = NetworkSimulator(network)
    detector = FailureDetector(network)

    simulator.fail_node("R02")

    assert detector.detect_failures() == ["R02"]


def test_detect_multiple_failed_nodes():
    network = create_network()
    simulator = NetworkSimulator(network)
    detector = FailureDetector(network)

    simulator.fail_node("R01")
    simulator.fail_node("R03")

    assert detector.detect_failures() == ["R01", "R03"]


def test_recovered_node_is_not_reported():
    network = create_network()
    simulator = NetworkSimulator(network)
    detector = FailureDetector(network)

    simulator.fail_node("R01")
    assert detector.detect_failures() == ["R01"]

    simulator.recover_node("R01")

    assert detector.detect_failures() == []


def test_fail_unknown_node():
    network = create_network()
    simulator = NetworkSimulator(network)

    with pytest.raises(ValueError, match="does not exist"):
        simulator.fail_node("UNKNOWN")