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
