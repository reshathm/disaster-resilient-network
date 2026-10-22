import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        test_client.post("/network/reset")
        try:
            yield test_client
        finally:
            test_client.post("/network/reset")


def test_simulation_status_starts_at_zero(client):
    response = client.get("/simulation/status")
    assert response.status_code == 200
    data = response.json()
    assert data["simulation_time"] == 0.0
    assert data["paused"] is False
    assert data["speed"] == 1.0
    assert data["moving_nodes"] == []


def test_start_and_step_moves_node(client):
    assert client.post("/simulation/nodes/R02/start").status_code == 200

    response = client.post("/simulation/step", json={"elapsed": 0.5})
    assert response.status_code == 200
    assert response.json()["steps"] == 5
    assert response.json()["advanced_time"] == pytest.approx(0.5)

    nodes = client.get("/network/nodes").json()
    r02 = next(node for node in nodes if node["node_id"] == "R02")
    assert r02["x"] == pytest.approx(2.5)


def test_stop_prevents_further_movement(client):
    client.post("/simulation/nodes/R02/start")
    client.post("/simulation/step", json={"elapsed": 0.2})

    response = client.post("/simulation/nodes/R02/stop")
    assert response.status_code == 200

    before = next(
        n for n in client.get("/network/nodes").json()
        if n["node_id"] == "R02"
    )["x"]

    client.post("/simulation/step", json={"elapsed": 0.5})

    after = next(
        n for n in client.get("/network/nodes").json()
        if n["node_id"] == "R02"
    )["x"]

    assert after == pytest.approx(before)


@pytest.mark.parametrize("action", ["start", "stop"])
def test_unknown_node_returns_404(client, action):
    response = client.post(f"/simulation/nodes/UNKNOWN/{action}")
    assert response.status_code == 404


@pytest.mark.parametrize("elapsed", [-1, "NaN", "Infinity"])
def test_invalid_elapsed_returns_422(client, elapsed):
    response = client.post("/simulation/step", json={"elapsed": elapsed})
    assert response.status_code == 422


def test_step_respects_catch_up_limit(client):
    response = client.post("/simulation/step", json={"elapsed": 10})
    assert response.status_code == 200
    assert response.json()["steps"] == 10
    assert response.json()["simulation_time"] == pytest.approx(1.0)


def test_reset_clears_simulation_state(client):
    client.post("/simulation/nodes/R02/start")
    client.post("/simulation/step", json={"elapsed": 0.5})

    assert client.post("/network/reset").status_code == 200

    status = client.get("/simulation/status").json()
    assert status["simulation_time"] == 0.0
    assert status["moving_nodes"] == []


def test_pause_and_resume(client):
    pause = client.post("/simulation/pause")
    assert pause.status_code == 200
    assert pause.json() == {"paused": True}

    status = client.get("/simulation/status").json()
    assert status["paused"] is True

    resume = client.post("/simulation/resume")
    assert resume.status_code == 200
    assert resume.json() == {"paused": False}

    status = client.get("/simulation/status").json()
    assert status["paused"] is False


def test_paused_simulation_does_not_advance(client):
    assert client.post("/simulation/pause").status_code == 200

    response = client.post(
        "/simulation/step",
        json={"elapsed": 0.5},
    )

    assert response.status_code == 200
    assert response.json()["steps"] == 0
    assert response.json()["simulation_time"] == 0.0


def test_simulation_resumes_advancement(client):
    client.post("/simulation/pause")
    client.post("/simulation/step", json={"elapsed": 0.5})
    client.post("/simulation/resume")

    response = client.post(
        "/simulation/step",
        json={"elapsed": 0.3},
    )

    assert response.status_code == 200
    assert response.json()["steps"] == 3
    assert response.json()["simulation_time"] == pytest.approx(0.3)


def test_simulation_speed_control(client):
    response = client.post(
        "/simulation/speed",
        json={"speed": 2.0},
    )

    assert response.status_code == 200
    assert response.json() == {"speed": 2.0}

    status = client.get("/simulation/status").json()
    assert status["speed"] == 2.0


def test_speed_multiplier_affects_advancement(client):
    client.post("/simulation/speed", json={"speed": 2.0})

    response = client.post(
        "/simulation/step",
        json={"elapsed": 0.2},
    )

    assert response.status_code == 200
    assert response.json()["steps"] == 4
    assert response.json()["simulation_time"] == pytest.approx(0.4)


@pytest.mark.parametrize(
    "speed",
    [0, -1, "NaN", "Infinity", "-Infinity"],
)
def test_invalid_simulation_speed_returns_422(client, speed):
    response = client.post(
        "/simulation/speed",
        json={"speed": speed},
    )

    assert response.status_code == 422
    assert client.get("/simulation/status").json()["speed"] == 1.0
