from app.models.node import Node, NodeType, NodeStatus
from app.network.location_tracker import LocationTracker
from app.network.lost_node_recovery import LostNodeRecovery
from app.network.topology import NetworkTopology
from app.simulation.simulator import NetworkSimulator


def create_recovery_network():
    topology = NetworkTopology()

    topology.add_node(
        Node("R01", NodeType.RESCUE_TEAM, x=0, y=0)
    )
    topology.add_node(
        Node(
            "R02",
            NodeType.RESCUE_TEAM,
            x=29,
            y=60,
            speed=5,
            direction=90,
        )
    )
    topology.add_node(
        Node("R03", NodeType.RESCUE_TEAM, x=40, y=60)
    )
    topology.add_node(
        Node(
            "R04",
            NodeType.RESCUE_TEAM,
            x=25,
            y=60,
            battery=95,
            signal_strength=95,
        )
    )
    topology.add_node(
        Node("C01", NodeType.COMMAND_CENTER, x=50, y=60)
    )

    topology.connect_nodes("R01", "R04")
    topology.connect_nodes("R04", "R03")
    topology.connect_nodes("R03", "C01")

    return topology


def test_complete_lost_node_recovery():
    topology = create_recovery_network()

    tracker = LocationTracker()

    tracker.update(
        "R02",
        x=25,
        y=40,
        speed=5,
        direction=90,
    )

    recovery = LostNodeRecovery(
        topology,
        tracker,
        communication_range=10,
    )

    recovery.mark_lost("R02")

    result = recovery.recover(
        "R02",
        elapsed_time=4,
    )

    assert result["status"] == "FOUND"

    assert result["prediction"]["predicted_x"] == 25.0
    assert result["prediction"]["predicted_y"] == 60.0
    assert result["prediction"]["search_radius"] == 5.0

    assert result["helper"]["node_id"] == "R04"

    assert result["search"]["route"] == ["R04"]
    assert result["search"]["travel_required"] is False

    assert result["discovery"]["discovered"] is True
    assert result["discovery"]["distance"] == 4.0

    assert topology.get_node("R02").status == NodeStatus.ONLINE
    assert topology.get_neighbors("R02") == {"R04": 1.0}

    assert result["reconnected_to"] == ["R04"]


def test_movement_to_lost_node_to_full_recovery():
    topology = create_recovery_network()

    tracker = LocationTracker()

    recovery = LostNodeRecovery(
        topology,
        tracker,
        communication_range=10,
    )

    simulator = NetworkSimulator(
        topology,
        communication_range=10,
        recovery_manager=recovery,
        location_tracker=tracker,
    )

    # Initially R02 is within communication range of R04.
    topology.connect_nodes("R02", "R04")

    assert topology.get_neighbors("R02") == {"R04": 1.0}
    assert topology.get_node("R02").status == NodeStatus.ONLINE

    # R02 moves out of communication range.
    lost_detected = simulator.move_node(
        "R02",
        29,
        80,
    )

    assert lost_detected is True
    assert topology.get_neighbors("R02") == {}
    assert topology.get_node("R02").status == NodeStatus.LOST

    # The simulator automatically registered R02 for recovery.
    assert "R02" in recovery.lost_nodes
    assert recovery.lost_nodes["R02"]["status"] == "LOST"

    # Recovery uses the automatically tracked movement state.
    result = recovery.recover(
        "R02",
        elapsed_time=0,
    )

    assert result["status"] == "FOUND"
    assert result["discovery"]["discovered"] is True
    assert topology.get_node("R02").status == NodeStatus.ONLINE