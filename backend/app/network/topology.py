from typing import Dict, List, Optional

from app.models.node import Node


class NetworkTopology:
    """Manages nodes and their direct connections."""

    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}

    def add_node(self, node: Node) -> None:
        """Add a node to the network."""
        if node.node_id in self.nodes:
            raise ValueError(f"Node '{node.node_id}' already exists.")

        self.nodes[node.node_id] = node

    def remove_node(self, node_id: str) -> None:
        """Remove a node and its connections from the network."""
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' does not exist.")

        for node in self.nodes.values():
            if node_id in node.neighbors:
                node.neighbors.remove(node_id)

        del self.nodes[node_id]

    def connect_nodes(self, first_id: str, second_id: str) -> None:
        """Create a two-way connection between two nodes."""
        first_node = self._get_node(first_id)
        second_node = self._get_node(second_id)

        if second_id not in first_node.neighbors:
            first_node.neighbors.append(second_id)

        if first_id not in second_node.neighbors:
            second_node.neighbors.append(first_id)

    def disconnect_nodes(self, first_id: str, second_id: str) -> None:
        """Remove a two-way connection between two nodes."""
        first_node = self._get_node(first_id)
        second_node = self._get_node(second_id)

        if second_id in first_node.neighbors:
            first_node.neighbors.remove(second_id)

        if first_id in second_node.neighbors:
            second_node.neighbors.remove(first_id)

    def get_node(self, node_id: str) -> Optional[Node]:
        """Return a node if it exists, otherwise None."""
        return self.nodes.get(node_id)

    def get_all_nodes(self) -> List[Node]:
        """Return all nodes currently in the network."""
        return list(self.nodes.values())

    def _get_node(self, node_id: str) -> Node:
        """Return a node or raise an error if it doesn't exist."""
        node = self.get_node(node_id)

        if node is None:
            raise ValueError(f"Node '{node_id}' does not exist.")

        return node