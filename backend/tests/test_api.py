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
