import pytest

from app.models.node import Node, NodeType
from app.network.topology import NetworkTopology
from app.simulation.driver import SimulationDriver
from app.simulation.engine import SimulationEngine


def make_driver(max_steps=10):
    topology = NetworkTopology()
    node = Node(
        "R01", NodeType.RESCUE_TEAM,
        x=0, y=0, speed=5, direction=0,
    )
    topology.add_node(node)
    engine = SimulationEngine(topology, communication_range=10)
    engine.start_movement("R01")
    return SimulationDriver(engine, max_steps_per_update=max_steps), engine, node


def test_fractional_time_accumulates():
    driver, engine, node = make_driver()

    assert driver.update(0.04) == 0
    assert engine.simulation_time == 0

    assert driver.update(0.06) == 1
    assert engine.simulation_time == pytest.approx(0.1)
    assert node.x == pytest.approx(0.5)


def test_pause_and_resume():
    driver, engine, _ = make_driver()

    driver.pause()
    assert driver.update(1.0) == 0
    assert engine.simulation_time == 0

    driver.resume()
    assert driver.update(0.1) == 1
    assert engine.simulation_time == pytest.approx(0.1)


def test_speed_multiplier():
    driver, engine, node = make_driver()

    driver.set_speed(2.0)
    assert driver.update(0.1) == 2
    assert engine.simulation_time == pytest.approx(0.2)
    assert node.x == pytest.approx(1.0)


def test_catch_up_cap_retains_backlog():
    driver, engine, _ = make_driver(max_steps=3)

    assert driver.update(1.0) == 3
    assert engine.simulation_time == pytest.approx(0.3)
    assert driver.accumulator == pytest.approx(0.3)

    assert driver.update(0.0) == 3
    assert engine.simulation_time == pytest.approx(0.6)


@pytest.mark.parametrize("elapsed", [-1, float("nan"), float("inf")])
def test_invalid_elapsed_rejected(elapsed):
    driver, engine, _ = make_driver()

    with pytest.raises(ValueError):
        driver.update(elapsed)

    assert engine.simulation_time == 0


@pytest.mark.parametrize("speed", [0, -1, float("nan"), float("inf")])
def test_invalid_speed_rejected(speed):
    driver, _, _ = make_driver()

    with pytest.raises(ValueError):
        driver.set_speed(speed)


def test_excessive_backlog_is_bounded():
    driver, engine, _ = make_driver(max_steps=3)

    assert driver.update(60.0) == 3
    assert engine.simulation_time == pytest.approx(0.3)

    # Keep at most one additional update's worth of catch-up work.
    assert driver.accumulator <= 0.3 + 1e-9
