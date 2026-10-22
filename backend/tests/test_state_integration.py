from concurrent.futures import ThreadPoolExecutor
from threading import Event

from app.initial_network import COMMUNICATION_RANGE, build_initial_network
from app.state import ApplicationState


def make_state():
    return ApplicationState(build_initial_network(), COMMUNICATION_RANGE)


def test_engine_shares_the_application_lock():
    state = make_state()

    assert state.engine.lock is state.lock


def test_engine_moves_the_applications_own_network():
    state = make_state()

    state.engine.start_movement("R02")
    state.engine.step(1.0)

    r02 = state.network.get_node("R02")

    assert abs(r02.x - 0.0) < 1e-9  # speed 5, direction 180, from x=5
    assert abs(r02.y) < 1e-9
    assert state.engine.simulation_time == 1.0


def test_driver_drives_the_applications_engine():
    state = make_state()

    state.engine.start_movement("R02")
    steps = state.driver.update(0.5)

    assert state.driver.engine is state.engine
    assert steps == 5
    assert abs(state.network.get_node("R02").x - 2.5) < 1e-9


def test_reset_rebuilds_engine_and_driver_for_the_new_network():
    state = make_state()
    old_engine = state.engine
    old_network = state.network

    state.engine.start_movement("R02")
    state.engine.step(1.0)
    state.driver.pause()

    state.reset(build_initial_network())

    assert state.engine is not old_engine
    assert state.engine.topology is state.network
    assert state.network is not old_network
    assert state.driver.engine is state.engine
    assert state.engine.lock is state.lock

    # Fresh clock, no leftover movement, simulation controls reset.
    assert state.engine.simulation_time == 0.0
    assert state.driver.paused is False
    assert state.network.get_node("R02").x == 5

    state.engine.step(1.0)

    assert state.network.get_node("R02").x == 5  # nothing commanded
    assert old_network.get_node("R02").x == 0  # old network untouched now


def test_engine_step_waits_for_the_shared_lock():
    state = make_state()
    state.engine.start_movement("R02")

    entered = Event()
    release = Event()
    finished = Event()

    def hold_lock():
        with state.lock:
            entered.set()
            release.wait(timeout=2)

    def run_step():
        state.engine.step(1.0)
        finished.set()

    with ThreadPoolExecutor(max_workers=2) as executor:
        holder = executor.submit(hold_lock)
        assert entered.wait(timeout=2)

        stepper = executor.submit(run_step)

        try:
            assert not finished.wait(timeout=0.05)
            assert state.network.get_node("R02").x == 5  # not moved yet
        finally:
            release.set()

        holder.result(timeout=2)
        stepper.result(timeout=2)

    assert finished.is_set()
    assert abs(state.network.get_node("R02").x - 0.0) < 1e-9
