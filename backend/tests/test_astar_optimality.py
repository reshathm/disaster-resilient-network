from app.models.node import Node, NodeType
from app.network.routing import NetworkRouter
from app.network.topology import NetworkTopology


def test_a_star_finds_lowest_cost_route():
    topology = NetworkTopology()

    positions = {
        "S": (0, 0),
        "A": (1, 0),
        "B": (90, 0),
        "C": (99, 0),
        "T": (100, 0),
    }

    for node_id, (x, y) in positions.items():
        topology.add_node(
            Node(node_id, NodeType.RESCUE_TEAM, x=x, y=y)
        )

    topology.connect_nodes("S", "A")
    topology.connect_nodes("A", "B")
    topology.connect_nodes("B", "C")
    topology.connect_nodes("C", "T")
    topology.connect_nodes("S", "T", weight=5)

    router = NetworkRouter(topology)

    assert router.find_route_a_star("S", "T") == [
        "S", "A", "B", "C", "T"
    ]
    assert router.get_a_star_route_cost("S", "T") == 4.0
