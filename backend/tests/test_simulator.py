from app.models.node import Node, NodeType, NodeStatus
from app.network.location_tracker import LocationTracker
from app.network.lost_node_recovery import LostNodeRecovery
from app.network.topology import NetworkTopology
from app.simulation.simulator import NetworkSimulator


def test_move_node_refreshes_connections_and_detects_loss():
    topology = NetworkTopology()

    topology.add_node(
        Node("R01", NodeType.RESCUE_TEAM, x=0, y=0)
    )
    topology.add_node(
        Node("R02", NodeType.RESCUE_TEAM, x=5, y=0)
    )

    topology.connect_nodes("R01", "R02")

    simulator = NetworkSimulator(
        topology,
        communication_range=10,
    )

    assert topology.get_neighbors("R01") == {"R02": 1.0}
    assert topology.get_node("R02").status == NodeStatus.ONLINE

    lost_detected = simulator.move_node(
        "R02",
        20,
        0,
    )

    assert lost_detected is True
    assert topology.get_neighbors("R01") == {}
    assert topology.get_node("R02").x == 20
    assert topology.get_node("R02").y == 0
    assert topology.get_node("R02").status == NodeStatus.LOST


def test_move_node_registers_lost_node_with_recovery_manager():
    topology = NetworkTopology()

    topology.add_node(
        Node("R01", NodeType.RESCUE_TEAM, x=0, y=0)
    )
    topology.add_node(
        Node("R02", NodeType.RESCUE_TEAM, x=5, y=0)
    )

    topology.connect_nodes("R01", "R02")

    location_tracker = LocationTracker()

    location_tracker.update(
        "R02",
        5,
        0,
        5,
        0,
    )

    recovery_manager = LostNodeRecovery(
        topology,
        location_tracker,
        communication_range=10,
    )

    simulator = NetworkSimulator(
        topology,
        communication_range=10,
        recovery_manager=recovery_manager,
    )

    lost_detected = simulator.move_node(
        "R02",
        20,
        0,
    )

    assert lost_detected is True
    assert topology.get_node("R02").status == NodeStatus.LOST

    assert "R02" in recovery_manager.lost_nodes
    assert recovery_manager.lost_nodes["R02"]["status"] == "LOST"


def test_move_node_tracks_movement_for_lost_node_prediction():
    topology = NetworkTopology()

    topology.add_node(
        Node("R01", NodeType.RESCUE_TEAM, x=0, y=0)
    )
    topology.add_node(
        Node(
            "R02",
            NodeType.RESCUE_TEAM,
            x=5,
            y=0,
            speed=5,
            direction=90,
        )
    )

    topology.connect_nodes("R01", "R02")

    simulator = NetworkSimulator(
        topology,
        communication_range=10,
    )

    lost_detected = simulator.move_node(
        "R02",
        20,
        0,
    )

    assert lost_detected is True

    tracked = simulator.location_tracker.last_known["R02"]

    assert tracked["x"] == 20
    assert tracked["y"] == 0
    assert tracked["speed"] == 5
    assert tracked["direction"] == 90

    predicted = simulator.location_tracker.predict_position(
        "R02",
        4,
    )

    assert predicted == (20.0, 20.0)

    radius = simulator.location_tracker.get_search_radius(
        "R02",
        4,
    )

    assert radius == 5.0
    assert topology.get_node("R02").status == NodeStatus.LOST