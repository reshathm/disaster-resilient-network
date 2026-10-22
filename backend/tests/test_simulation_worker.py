from threading import Event
from unittest.mock import Mock

import pytest

from app.initial_network import COMMUNICATION_RANGE, build_initial_network
from app.simulation.worker import SimulationWorker
from app.state import ApplicationState


@pytest.fixture
def state():
    return ApplicationState(build_initial_network(), COMMUNICATION_RANGE)


def test_invalid_worker_intervals(state):
    for interval in (0, -1, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            SimulationWorker(state, interval=interval)


def test_worker_advances_simulation(state):
    worker = SimulationWorker(state, interval=0.01)
    state.driver.update = Mock()
    updated = Event()
    state.driver.update.side_effect = lambda elapsed: updated.set()

    try:
        worker.start()
        assert updated.wait(timeout=1.0)
        assert state.driver.update.call_count >= 1
        assert state.driver.update.call_args.args[0] >= 0
    finally:
        worker.stop()


def test_worker_stops_cleanly(state):
    worker = SimulationWorker(state, interval=0.01)
    worker.start()
    worker.stop()

    assert worker._thread is None


def test_start_does_not_create_duplicate_thread(state):
    worker = SimulationWorker(state, interval=0.01)

    try:
        worker.start()
        first_thread = worker._thread
        worker.start()
        assert worker._thread is first_thread
    finally:
        worker.stop()


def test_worker_uses_new_driver_after_reset(state):
    worker = SimulationWorker(state, interval=0.01)
    old_driver = state.driver
    old_driver.update = Mock()
    updated = Event()

    try:
        worker.start()
        state.reset(build_initial_network())
        state.driver.update = Mock(
            side_effect=lambda elapsed: updated.set()
        )

        assert updated.wait(timeout=1.0)
        assert state.driver is not old_driver
        assert state.driver.update.call_count >= 1
    finally:
        worker.stop()
