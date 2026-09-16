from dataclasses import dataclass
from typing import Dict, List, Optional

from app.models.node import NodeStatus


@dataclass
class Connection:
    """Represents a weighted connection between two nodes."""

    source_id: str
    target_id: str
    weight: float


class NetworkTopology:
    """Manages nodes and their weighted connections."""

    def __init__(self) -> None:
        self.nodes: Dict[str, object] = {}
        self.connections: Dict[str, Dict[str, float]] = {}

    def add_node(self, node) -> None:
        """Add a node to the network."""
        if node.node_id in self.nodes:
            raise ValueError(f"Node '{node.node_id}' already exists.")

        self.nodes[node.node_id] = node
        self.connections[node.node_id] = {}

    def remove_node(self, node_id: str) -> None:
        """Remove a node and all of its connections."""
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' does not exist.")

        for neighbor_id in list(self.connections[node_id]):
            self.disconnect_nodes(node_id, neighbor_id)

        del self.connections[node_id]
        del self.nodes[node_id]

    def connect_nodes(
        self,
        first_id: str,
        second_id: str,
        weight: float = 1.0,
    ) -> None:
        """Create a two-way weighted connection."""
        if weight <= 0:
            raise ValueError("Connection weight must be greater than zero.")

        first_node = self._get_node(first_id)
        second_node = self._get_node(second_id)

        self.connections[first_id][second_id] = weight
        self.connections[second_id][first_id] = weight

        if second_id not in first_node.neighbors:
            first_node.neighbors.append(second_id)

        if first_id not in second_node.neighbors:
            second_node.neighbors.append(first_id)

    def disconnect_nodes(self, first_id: str, second_id: str) -> None:
        """Remove a two-way connection."""
        first_node = self._get_node(first_id)
        second_node = self._get_node(second_id)

        self.connections[first_id].pop(second_id, None)
        self.connections[second_id].pop(first_id, None)

        if second_id in first_node.neighbors:
            first_node.neighbors.remove(second_id)

        if first_id in second_node.neighbors:
            second_node.neighbors.remove(first_id)

    def refresh_connections(self, communication_range: float) -> None:
        """Remove connections between nodes that are now out of range."""
        import math

        if communication_range <= 0:
            raise ValueError("Communication range must be greater than zero.")

        checked_pairs = set()

        for first_id in list(self.connections):
            for second_id in list(self.connections[first_id]):
                pair = tuple(sorted((first_id, second_id)))

                if pair in checked_pairs:
                    continue

                checked_pairs.add(pair)

                first_node = self.nodes[first_id]
                second_node = self.nodes[second_id]

                distance = math.sqrt(
                    (first_node.x - second_node.x) ** 2
                    + (first_node.y - second_node.y) ** 2
                )

                if distance > communication_range:
                    self.disconnect_nodes(first_id, second_id)

    def reconnect_node(
        self,
        node_id: str,
        communication_range: float,
    ) -> List[str]:
        """Reconnect a recovered node to all currently reachable online nodes."""
        import math

        if communication_range <= 0:
            raise ValueError("Communication range must be greater than zero.")

        node = self._get_node(node_id)
        connected_nodes = []

        for other_node in self.get_all_nodes():
            if other_node.node_id == node_id:
                continue

            if other_node.status != NodeStatus.ONLINE:
                continue

            distance = math.sqrt(
                (node.x - other_node.x) ** 2
                + (node.y - other_node.y) ** 2
            )

            if distance <= communication_range:
                if other_node.node_id not in self.connections[node_id]:
                    self.connect_nodes(
                        node_id,
                        other_node.node_id,
                    )

                connected_nodes.append(other_node.node_id)

        return connected_nodes

    def get_node(self, node_id: str) -> Optional[object]:
        """Return a node if it exists, otherwise None."""
        return self.nodes.get(node_id)

    def get_all_nodes(self) -> List[object]:
        """Return all nodes currently in the network."""
        return list(self.nodes.values())

    def get_weight(self, first_id: str, second_id: str) -> float:
        """Return the weight of a connection."""
        self._get_node(first_id)
        self._get_node(second_id)

        if second_id not in self.connections[first_id]:
            raise ValueError(
                f"No connection exists between '{first_id}' and '{second_id}'."
            )

        return self.connections[first_id][second_id]

    def get_neighbors(self, node_id: str) -> Dict[str, float]:
        """Return neighboring node IDs and their connection weights."""
        self._get_node(node_id)
        return dict(self.connections[node_id])

    def _get_node(self, node_id: str):
        """Return a node or raise an error if it doesn't exist."""
        node = self.get_node(node_id)

        if node is None:
            raise ValueError(f"Node '{node_id}' does not exist.")

        return node