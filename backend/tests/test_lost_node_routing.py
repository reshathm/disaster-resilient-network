import pytest

from app.models.node import Node, NodeStatus, NodeType
from app.network.routing import NetworkRouter
from app.network.topology import NetworkTopology


@pytest.mark.parametrize("algorithm", [
    "find_route",
    "find_route_a_star",
])
def test_lost_intermediate_node_cannot_route(algorithm):
    topology = NetworkTopology()

    for node_id in ("A", "B", "C"):
        topology.add_node(Node(node_id, NodeType.RESCUE_TEAM))

    topology.connect_nodes("A", "B")
    topology.connect_nodes("B", "C")

    topology.get_node("B").status = NodeStatus.LOST

    router = NetworkRouter(topology)

    with pytest.raises(ValueError, match="No route exists"):
        getattr(router, algorithm)("A", "C")


@pytest.mark.parametrize("algorithm", [
    "find_route",
    "find_route_a_star",
])
@pytest.mark.parametrize("lost_node", ["A", "C"])
def test_lost_endpoint_cannot_route(algorithm, lost_node):
    topology = NetworkTopology()

    topology.add_node(Node("A", NodeType.RESCUE_TEAM))
    topology.add_node(Node("C", NodeType.COMMAND_CENTER))
    topology.connect_nodes("A", "C")

    topology.get_node(lost_node).status = NodeStatus.LOST

    router = NetworkRouter(topology)

    with pytest.raises(ValueError):
        getattr(router, algorithm)("A", "C")
