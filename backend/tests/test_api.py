from fastapi.testclient import TestClient

from app.main import app


def test_node_failure_and_network_reset():
    with TestClient(app) as client:
        try:
            response = client.post("/network/reset")
            assert response.status_code == 200

            nodes = client.get("/network/nodes")
            assert nodes.status_code == 200
            assert len(nodes.json()) == 5

            failure = client.post("/network/nodes/R02/fail")
            assert failure.status_code == 200

            nodes = client.get("/network/nodes").json()
            r02 = next(
                node for node in nodes
                if node["node_id"] == "R02"
            )
            assert r02["status"] == "offline"

            reset = client.post("/network/reset")
            assert reset.status_code == 200

            nodes = client.get("/network/nodes").json()
            assert len(nodes) == 5

            r02 = next(
                node for node in nodes
                if node["node_id"] == "R02"
            )
            assert r02["status"] == "online"

        finally:
            client.post("/network/reset")


def test_node_recovery_after_reset():
    """Recovery must use the current services after network reset."""

    with TestClient(app) as client:
        try:
            assert client.post("/network/reset").status_code == 200

            for cycle in range(2):
                failure = client.post("/network/nodes/R02/fail")
                assert failure.status_code == 200
                assert failure.json()["status"] == "offline"

                status = client.get("/network/status")
                assert status.status_code == 200
                assert status.json()["offline_nodes"] == 1

                recovery = client.post("/network/nodes/R02/recover")
                assert recovery.status_code == 200
                assert recovery.json()["status"] == "online"

                status = client.get("/network/status").json()
                assert status["offline_nodes"] == 0

                events = client.get("/network/events").json()
                event_types = {event["event_type"] for event in events}

                assert "NODE_OFFLINE" in event_types
                assert "NODE_ONLINE" in event_types

                if cycle == 0:
                    assert client.post("/network/reset").status_code == 200

        finally:
            client.post("/network/reset")


def test_message_delivery_via_api():
    """A message should be delivered through the HTTP API."""

    with TestClient(app) as client:
        try:
            assert client.post("/network/reset").status_code == 200

            response = client.post(
                "/network/messages/send",
                json={
                    "message_id": "API-M001",
                    "source_id": "R01",
                    "destination_id": "C01",
                    "content": "Emergency evacuation required",
                    "priority": "critical",
                },
            )

            assert response.status_code == 200

            result = response.json()

            assert result["message_id"] == "API-M001"
            assert result["status"] == "delivered"
            assert result["priority"] == "critical"
            assert result["source"] == "R01"
            assert result["destination"] == "C01"
            assert result["route"][0] == "R01"
            assert result["route"][-1] == "C01"

        finally:
            client.post("/network/reset")


def test_node_movement_via_api():
    """Moving a node should update its position through the API."""

    with TestClient(app) as client:
        try:
            assert client.post("/network/reset").status_code == 200

            response = client.post(
                "/network/nodes/R02/move",
                json={
                    "x": 5.0,
                    "y": 5.0,
                },
            )

            assert response.status_code == 200

            result = response.json()

            assert result["node_id"] == "R02"
            assert result["x"] == 5.0
            assert result["y"] == 5.0
            assert result["lost_detected"] is False

            nodes = client.get("/network/nodes")
            assert nodes.status_code == 200

            r02 = next(
                node for node in nodes.json()
                if node["node_id"] == "R02"
            )

            assert r02["x"] == 5.0
            assert r02["y"] == 5.0

        finally:
            client.post("/network/reset")


def test_lost_node_recovery_via_api():
    """Move R02 out of range, then recover it through the API."""

    with TestClient(app) as client:
        try:
            assert client.post("/network/reset").status_code == 200

            moved = client.post(
                "/network/nodes/R02/move",
                json={"x": 32.0, "y": 0.0},
            )
            assert moved.status_code == 200
            moved = moved.json()
            assert moved["lost_detected"] is True
            assert moved["status"] == "lost"

            recovery = client.post(
                "/network/nodes/R02/recover-lost",
                json={"elapsed_time": 3.0},
            )
            assert recovery.status_code == 200
            result = recovery.json()

            assert result["status"] == "FOUND"
            assert abs(result["prediction"]["predicted_x"] - 17.0) < 1e-6
            assert abs(result["prediction"]["predicted_y"]) < 1e-6
            assert set(result["reconnected_to"]) == {"R03", "R04", "C01"}

            nodes = client.get("/network/nodes").json()
            r02 = next(n for n in nodes if n["node_id"] == "R02")
            assert r02["status"] == "online"
            assert abs(r02["x"] - 17.0) < 1e-6

            events = client.get("/network/events").json()
            event_types = {e["event_type"] for e in events}

            for expected in (
                "NODE_LOST",
                "PREDICTION",
                "HELPER_SELECTED",
                "ASTAR_SEARCH",
                "NODE_FOUND",
                "TOPOLOGY_REBUILT",
            ):
                assert expected in event_types

        finally:
            client.post("/network/reset")
