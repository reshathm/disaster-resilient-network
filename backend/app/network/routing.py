from collections import deque
from typing import List

from app.models.node import NodeStatus
from app.network.topology import NetworkTopology


class NetworkRouter:
    """Finds routes between online nodes in the network."""

    def __init__(self, topology: NetworkTopology) -> None:
        self.topology = topology

    def find_route(self, source_id: str, destination_id: str) -> List[str]:
        """Find the shortest available route between two online nodes."""

        source = self.topology.get_node(source_id)
        destination = self.topology.get_node(destination_id)

        if source is None:
            raise ValueError(f"Node '{source_id}' does not exist.")

        if destination is None:
            raise ValueError(f"Node '{destination_id}' does not exist.")

        if source.status == NodeStatus.OFFLINE:
            raise ValueError(f"Node '{source_id}' is offline.")

        if destination.status == NodeStatus.OFFLINE:
            raise ValueError(f"Node '{destination_id}' is offline.")

        if source_id == destination_id:
            return [source_id]

        queue = deque([[source_id]])
        visited = {source_id}

        while queue:
            route = queue.popleft()
            current_id = route[-1]
            current_node = self.topology.get_node(current_id)

            if current_node is None or current_node.status == NodeStatus.OFFLINE:
                continue

            for neighbor_id in current_node.neighbors:
                if neighbor_id in visited:
                    continue

                neighbor = self.topology.get_node(neighbor_id)

                if neighbor is None or neighbor.status == NodeStatus.OFFLINE:
                    continue

                new_route = route + [neighbor_id]

                if neighbor_id == destination_id:
                    return new_route

                visited.add(neighbor_id)
                queue.append(new_route)

        raise ValueError(
            f"No route exists from '{source_id}' to '{destination_id}'."
        )