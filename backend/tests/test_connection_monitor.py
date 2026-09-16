from app.models.node import Node, NodeType, NodeStatus
from app.network.connection_monitor import ConnectionMonitor
from app.network.topology import NetworkTopology


def test_node_is_marked_lost_after_connection_loss():
    topology = NetworkTopology()

    topology.add_node(
        Node("R01", NodeType.RESCUE_TEAM, x=0, y=0)
    )
    topology.add_node(
        Node("R02", NodeType.RESCUE_TEAM, x=5, y=0)
    )

    topology.connect_nodes("R01", "R02")

    monitor = ConnectionMonitor(
        topology,
        communication_range=10,
    )

    assert monitor.check_node("R02") is True

    topology.get_node("R02").x = 20
    topology.refresh_connections(10)

    assert monitor.check_node("R02") is False

    assert monitor.detect_lost_node("R02") is True
    assert topology.get_node("R02").status == NodeStatus.LOST