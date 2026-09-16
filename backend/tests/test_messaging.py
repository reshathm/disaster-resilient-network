import pytest

from app.models.message import Message, MessagePriority
from app.models.node import Node, NodeType
from app.network.event_log import EventLog
from app.network.messaging import MessageService
from app.network.topology import NetworkTopology
from app.simulation.simulator import NetworkSimulator


def create_network() -> NetworkTopology:
    network = NetworkTopology()

    nodes = [
        ("R01", NodeType.RESCUE_TEAM),
        ("R02", NodeType.RESCUE_TEAM),
        ("R03", NodeType.COMMAND_CENTER),
        ("R04", NodeType.DRONE),
    ]

    for node_id, node_type in nodes:
        network.add_node(Node(node_id, node_type))

    network.connect_nodes("R01", "R02")
    network.connect_nodes("R02", "R03")
    network.connect_nodes("R01", "R04")
    network.connect_nodes("R04", "R03")

    return network


def test_send_message():
    network = create_network()
    event_log = EventLog()
    service = MessageService(network, event_log)

    message = Message(
        "M001",
        "R01",
        "R03",
        "Need evacuation",
        MessagePriority.CRITICAL,
    )

    assert service.send_message(message) == [
        "R01",
        "R02",
        "R03",
    ]

    events = event_log.get_events()

    assert len(events) == 1
    assert events[0].event_type == "MESSAGE_DELIVERED"
    assert events[0].message == "M001 delivered via R01 -> R02 -> R03"


def test_message_uses_alternate_route_after_failure():
    network = create_network()
    event_log = EventLog()
    service = MessageService(network, event_log)
    simulator = NetworkSimulator(network)

    simulator.fail_node("R02")

    message = Message(
        "M002",
        "R01",
        "R03",
        "Emergency request",
        MessagePriority.HIGH,
    )

    assert service.send_message(message) == [
        "R01",
        "R04",
        "R03",
    ]


def test_message_fails_when_no_route_exists():
    network = create_network()
    event_log = EventLog()
    service = MessageService(network, event_log)
    simulator = NetworkSimulator(network)

    simulator.fail_node("R02")
    simulator.fail_node("R04")

    message = Message(
        "M003",
        "R01",
        "R03",
        "Emergency request",
        MessagePriority.CRITICAL,
    )

    with pytest.raises(ValueError, match="No route exists"):
        service.send_message(message)