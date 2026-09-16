from typing import Dict, List

from app.models.node import NodeStatus
from app.network.topology import NetworkTopology


class NetworkMonitor:
    """Provides the current health state of the network."""

    def __init__(self, topology: NetworkTopology) -> None:
        self.topology = topology

    def get_online_nodes(self) -> List[str]:
        """Return IDs of all online nodes."""
        return [
            node.node_id
            for node in self.topology.get_all_nodes()
            if node.status == NodeStatus.ONLINE
        ]

    def get_offline_nodes(self) -> List[str]:
        """Return IDs of all offline nodes."""
        return [
            node.node_id
            for node in self.topology.get_all_nodes()
            if node.status == NodeStatus.OFFLINE
        ]

    def get_network_summary(self) -> Dict[str, int]:
        """Return basic network health statistics."""
        online = self.get_online_nodes()
        offline = self.get_offline_nodes()

        return {
            "total_nodes": len(online) + len(offline),
            "online_nodes": len(online),
            "offline_nodes": len(offline),
        }