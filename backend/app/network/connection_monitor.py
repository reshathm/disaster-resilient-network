import math

from app.models.node import NodeStatus
from app.network.topology import NetworkTopology


class ConnectionMonitor:
    """Detects nodes that have lost communication with the network."""

    def __init__(
        self,
        topology: NetworkTopology,
        communication_range: float = 10.0,
    ) -> None:
        self.topology = topology
        self.communication_range = communication_range

    def check_node(self, node_id: str) -> bool:
        """Return True if the node has at least one reachable neighbor."""
        node = self.topology.get_node(node_id)

        if node is None:
            raise ValueError(f"Node '{node_id}' does not exist.")

        for neighbor_id in node.neighbors:
            neighbor = self.topology.get_node(neighbor_id)

            if neighbor is None:
                continue

            if neighbor.status != NodeStatus.ONLINE:
                continue

            distance = math.sqrt(
                (node.x - neighbor.x) ** 2
                + (node.y - neighbor.y) ** 2
            )

            if distance <= self.communication_range:
                return True

        return False

    def detect_lost_node(self, node_id: str) -> bool:
        """Mark an online node as LOST when it has no reachable neighbors."""
        node = self.topology.get_node(node_id)

        if node is None:
            raise ValueError(f"Node '{node_id}' does not exist.")

        if node.status != NodeStatus.ONLINE:
            return False

        if not self.check_node(node_id):
            node.status = NodeStatus.LOST
            return True

        return False