from typing import List

from app.models.node import NodeStatus
from app.network.topology import NetworkTopology


class FailureDetector:
    """Detects nodes that are currently offline."""

    def __init__(self, topology: NetworkTopology) -> None:
        self.topology = topology

    def detect_failures(self) -> List[str]:
        """Return the IDs of all currently offline nodes."""

        failed_nodes = []

        for node in self.topology.get_all_nodes():
            if node.status == NodeStatus.OFFLINE:
                failed_nodes.append(node.node_id)

        return failed_nodes