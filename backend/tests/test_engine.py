import pytest

from app.models.node import Node, NodeType
from app.network.topology import NetworkTopology
from app.simulation.engine import SimulationEngine


def test_nodes_remain_stationary_until_commanded():
    topology = NetworkTopology()
    node = Node(
        "R01",
        NodeType.RESCUE_TEAM,
        x=0,
        y=0,
        speed=5,
        direction=0,
    )
    topology.add_node(node)

    engine = SimulationEngine(topology, communication_range=10)
    engine.step(1.0)

    assert node.x == pytest.approx(0)
    assert node.y == pytest.approx(0)
    assert engine.simulation_time == pytest.approx(1.0)


def test_commanded_movement_advances_with_time():
    topology = NetworkTopology()
    node = Node(
        "R01",
        NodeType.RESCUE_TEAM,
        x=0,
        y=0,
        speed=5,
        direction=0,
    )
    topology.add_node(node)

    engine = SimulationEngine(topology, communication_range=10)
    engine.start_movement("R01")
    engine.step(1.0)

    assert node.x == pytest.approx(5.0)
    assert node.y == pytest.approx(0.0)

    engine.stop_movement("R01")
    engine.step(1.0)

    assert node.x == pytest.approx(5.0)
    assert engine.simulation_time == pytest.approx(2.0)


def test_movement_updates_network_connectivity():
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
            direction=0,
        )
    )

    topology.refresh_connections(10)
    assert "R02" in topology.get_neighbors("R01")

    engine = SimulationEngine(topology, communication_range=10)
    engine.start_movement("R02")

    engine.step(2.0)

    assert topology.get_node("R02").x == pytest.approx(15.0)
    assert "R02" not in topology.get_neighbors("R01")

    topology.get_node("R02").direction = 180
    engine.step(2.0)

    assert topology.get_node("R02").x == pytest.approx(5.0)
    assert "R02" in topology.get_neighbors("R01")


@pytest.mark.parametrize("dt", [0, -1, float("nan"), float("inf"), -float("inf")])
def test_engine_rejects_invalid_time_steps(dt):
    topology = NetworkTopology()
    node = Node("R01", NodeType.RESCUE_TEAM, x=0, y=0)
    topology.add_node(node)

    engine = SimulationEngine(topology, communication_range=10)

    with pytest.raises(ValueError):
        engine.step(dt)

    assert engine.simulation_time == 0.0
    assert node.x == 0
    assert node.y == 0
