from concurrent.futures import ThreadPoolExecutor
from threading import Event, Lock
from time import sleep
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI
from fastapi.testclient import TestClient

from app.dependencies import get_state
from app.locked_route import LockedRoute
from app.state import ApplicationState


def test_locked_routes_serialize_concurrent_requests():
    test_app = FastAPI()
    router = APIRouter(route_class=LockedRoute)

    counter_lock = Lock()
    active = 0
    maximum_active = 0

    @router.get("/test")
    def endpoint(state: Annotated[ApplicationState, Depends(get_state)]):
        nonlocal active, maximum_active

        with counter_lock:
            active += 1
            maximum_active = max(maximum_active, active)

        sleep(0.01)

        with counter_lock:
            active -= 1

        return {"ok": True}

    test_app.include_router(router)

    with TestClient(test_app) as client:
        with ThreadPoolExecutor(max_workers=8) as executor:
            responses = list(
                executor.map(lambda _: client.get("/test"), range(16))
            )

    assert all(response.status_code == 200 for response in responses)
    assert maximum_active == 1


def test_reset_waits_for_shared_lock():
    state = get_state()
    entered = Event()
    release = Event()
    completed = Event()

    def hold_lock():
        with state.lock:
            entered.set()
            release.wait(timeout=2)

    def reset_network():
        from app.initial_network import build_initial_network

        state.reset(build_initial_network())
        completed.set()

    with ThreadPoolExecutor(max_workers=2) as executor:
        holder = executor.submit(hold_lock)
        assert entered.wait(timeout=2)

        resetter = executor.submit(reset_network)

        try:
            assert not completed.wait(timeout=0.05)
        finally:
            release.set()

        holder.result(timeout=2)
        resetter.result(timeout=2)

    assert completed.is_set()
