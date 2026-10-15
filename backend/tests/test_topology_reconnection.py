from app.models.node import Node, NodeStatus, NodeType
from app.network.topology import NetworkTopology
from app.simulation.simulator import NetworkSimulator


def test_online_node_reconnects_when_back_in_range():
    topology = NetworkTopology()

    for node_id, x in [("A", 0), ("B", 5), ("C", 15)]:
        topology.add_node(
            Node(node_id, NodeType.RESCUE_TEAM, x=x, y=0)
        )

    topology.connect_nodes("A", "B")
    topology.connect_nodes("B", "C")

    simulator = NetworkSimulator(topology, communication_range=10)

    simulator.move_node("B", 14, 0)

    assert topology.get_node("B").status == NodeStatus.ONLINE
    assert "A" not in topology.get_neighbors("B")
    assert "C" in topology.get_neighbors("B")

    simulator.move_node("B", 5, 0)

    assert topology.get_node("B").status == NodeStatus.ONLINE
    assert "A" in topology.get_neighbors("B")
    assert "C" in topology.get_neighbors("B")
