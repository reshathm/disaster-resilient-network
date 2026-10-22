from threading import enumerate as active_threads
from time import monotonic, sleep

from fastapi.testclient import TestClient

from app.main import app


def test_lifespan_runs_and_stops_simulation_worker():
    with TestClient(app) as client:
        try:
            assert client.post("/network/reset").status_code == 200
            assert client.post("/simulation/nodes/R02/start").status_code == 200

            deadline = monotonic() + 2.0
            moved = False

            while monotonic() < deadline:
                nodes = client.get("/network/nodes")
                assert nodes.status_code == 200

                r02 = next(
                    node for node in nodes.json()
                    if node["node_id"] == "R02"
                )

                if r02["x"] < 5.0:
                    moved = True
                    break

                sleep(0.02)

            assert moved, "Background worker did not move R02"

            status = client.get("/simulation/status")
            assert status.status_code == 200
            assert status.json()["simulation_time"] > 0

        finally:
            client.post("/network/reset")

    assert not any(
        thread.name == "simulation-worker" and thread.is_alive()
        for thread in active_threads()
    ), "Simulation worker remained alive after shutdown"
