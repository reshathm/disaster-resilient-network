from app.models.node import NodeStatus
from app.network.topology import NetworkTopology


class NetworkSimulator:
    """Simulates failures and recovery of network nodes."""

    def __init__(self, topology: NetworkTopology) -> None:
        self.topology = topology

    def fail_node(self, node_id: str) -> None:
        """Simulate a node failure."""
        node = self._get_node(node_id)

        if node.status == NodeStatus.OFFLINE:
            raise ValueError(f"Node '{node_id}' is already offline.")

        node.status = NodeStatus.OFFLINE

    def recover_node(self, node_id: str) -> None:
        """Simulate a node recovering."""
        node = self._get_node(node_id)

        if node.status == NodeStatus.ONLINE:
            raise ValueError(f"Node '{node_id}' is already online.")

        node.status = NodeStatus.ONLINE

    def _get_node(self, node_id: str):
        """Return a node or raise an error if it doesn't exist."""
        node = self.topology.get_node(node_id)

        if node is None:
            raise ValueError(f"Node '{node_id}' does not exist.")

        return node