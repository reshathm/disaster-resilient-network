from typing import List

from app.network.failure_detection import FailureDetector
from app.network.routing import NetworkRouter
from app.network.topology import NetworkTopology


class SelfHealingManager:
    """Handles automatic route recovery after network failures."""

    def __init__(self, topology: NetworkTopology) -> None:
        self.topology = topology
        self.router = NetworkRouter(topology)
        self.failure_detector = FailureDetector(topology)

    def recover_route(self, source_id: str, destination_id: str) -> List[str]:
        """Find a route that avoids currently failed nodes."""

        failed_nodes = self.failure_detector.detect_failures()

        route = self.router.find_route(source_id, destination_id)

        if any(node_id in failed_nodes for node_id in route):
            raise ValueError("Route contains a failed node.")

        return route