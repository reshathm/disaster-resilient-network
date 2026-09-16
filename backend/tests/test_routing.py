import pytest

from app.models.node import Node, NodeType
from app.network.routing import NetworkRouter
from app.network.topology import NetworkTopology


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

    return network


def test_find_route():
    network = create_network()

    network.connect_nodes("R01", "R02")
    network.connect_nodes("R02", "R03")
    network.connect_nodes("R03", "C01")

    router = NetworkRouter(network)

    assert router.find_route("R01", "C01") == [
        "R01",
        "R02",
        "R03",
        "C01",
    ]


def test_find_alternate_route():
    network = create_network()

    network.connect_nodes("R01", "R02")
    network.connect_nodes("R02", "R03")
    network.connect_nodes("R03", "C01")

    network.connect_nodes("R01", "R04")
    network.connect_nodes("R04", "R03")

    router = NetworkRouter(network)

    network.disconnect_nodes("R01", "R02")

    assert router.find_route("R01", "C01") == [
        "R01",
        "R04",
        "R03",
        "C01",
    ]


def test_no_route_exists():
    network = create_network()

    network.connect_nodes("R01", "R02")

    router = NetworkRouter(network)

    with pytest.raises(ValueError, match="No route exists"):
        router.find_route("R01", "C01")


def test_invalid_source_node():
    network = create_network()

    router = NetworkRouter(network)

    with pytest.raises(ValueError, match="does not exist"):
        router.find_route("UNKNOWN", "C01")