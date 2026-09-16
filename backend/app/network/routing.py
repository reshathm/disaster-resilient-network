import heapq
import math
from typing import Dict, List

from app.models.node import NodeStatus
from app.network.topology import NetworkTopology


class NetworkRouter:
    """Finds routes between online nodes using Dijkstra and A*."""

    def __init__(self, topology: NetworkTopology) -> None:
        self.topology = topology

    def find_route(self, source_id: str, destination_id: str) -> List[str]:
        """Find the lowest-cost route using Dijkstra's algorithm."""

        self._validate_nodes(source_id, destination_id)

        if source_id == destination_id:
            return [source_id]

        distances: Dict[str, float] = {
            node.node_id: float("inf")
            for node in self.topology.get_all_nodes()
        }

        previous: Dict[str, str] = {}
        distances[source_id] = 0.0

        priority_queue = [(0.0, source_id)]

        while priority_queue:
            current_distance, current_id = heapq.heappop(priority_queue)

            if current_distance > distances[current_id]:
                continue

            if current_id == destination_id:
                break

            current_node = self.topology.get_node(current_id)

            if current_node is None:
                continue

            if current_node.status == NodeStatus.OFFLINE:
                continue

            for neighbor_id, weight in self.topology.get_neighbors(
                current_id
            ).items():

                neighbor = self.topology.get_node(neighbor_id)

                if neighbor is None:
                    continue

                if neighbor.status == NodeStatus.OFFLINE:
                    continue

                new_distance = current_distance + weight

                if new_distance < distances[neighbor_id]:
                    distances[neighbor_id] = new_distance
                    previous[neighbor_id] = current_id

                    heapq.heappush(
                        priority_queue,
                        (new_distance, neighbor_id),
                    )

        if distances[destination_id] == float("inf"):
            raise ValueError(
                f"No route exists from '{source_id}' to '{destination_id}'."
            )

        return self._build_route(previous, source_id, destination_id)

    def find_route_a_star(
        self,
        source_id: str,
        destination_id: str,
    ) -> List[str]:
        """Find a route using the A* search algorithm."""

        self._validate_nodes(source_id, destination_id)

        if source_id == destination_id:
            return [source_id]

        distances: Dict[str, float] = {
            node.node_id: float("inf")
            for node in self.topology.get_all_nodes()
        }

        previous: Dict[str, str] = {}
        distances[source_id] = 0.0

        source = self.topology.get_node(source_id)
        destination = self.topology.get_node(destination_id)

        priority_queue = [
            (
                self._heuristic(source, destination),
                0.0,
                source_id,
            )
        ]

        while priority_queue:
            _, current_distance, current_id = heapq.heappop(
                priority_queue
            )

            if current_distance > distances[current_id]:
                continue

            if current_id == destination_id:
                break

            current_node = self.topology.get_node(current_id)

            if current_node is None:
                continue

            if current_node.status == NodeStatus.OFFLINE:
                continue

            for neighbor_id, weight in self.topology.get_neighbors(
                current_id
            ).items():

                neighbor = self.topology.get_node(neighbor_id)

                if neighbor is None:
                    continue

                if neighbor.status == NodeStatus.OFFLINE:
                    continue

                new_distance = current_distance + weight

                if new_distance < distances[neighbor_id]:
                    distances[neighbor_id] = new_distance
                    previous[neighbor_id] = current_id

                    heuristic = self._heuristic(
                        neighbor,
                        destination,
                    )

                    estimated_total = new_distance + heuristic

                    heapq.heappush(
                        priority_queue,
                        (
                            estimated_total,
                            new_distance,
                            neighbor_id,
                        ),
                    )

        if distances[destination_id] == float("inf"):
            raise ValueError(
                f"No route exists from '{source_id}' to '{destination_id}'."
            )

        return self._build_route(previous, source_id, destination_id)

    def get_route_cost(
        self,
        source_id: str,
        destination_id: str,
    ) -> float:
        """Return the total cost of the Dijkstra route."""

        route = self.find_route(source_id, destination_id)

        return self._calculate_route_cost(route)

    def get_a_star_route_cost(
        self,
        source_id: str,
        destination_id: str,
    ) -> float:
        """Return the total cost of the A* route."""

        route = self.find_route_a_star(source_id, destination_id)

        return self._calculate_route_cost(route)

    def _heuristic(self, first_node, second_node) -> float:
        """Calculate Euclidean distance between two nodes."""

        return math.sqrt(
            (first_node.x - second_node.x) ** 2
            + (first_node.y - second_node.y) ** 2
        )

    def _calculate_route_cost(self, route: List[str]) -> float:
        """Calculate the total weight of a route."""

        total_cost = 0.0

        for first_id, second_id in zip(route, route[1:]):
            total_cost += self.topology.get_weight(
                first_id,
                second_id,
            )

        return total_cost

    def _build_route(
        self,
        previous: Dict[str, str],
        source_id: str,
        destination_id: str,
    ) -> List[str]:
        """Reconstruct a route from the predecessor map."""

        route = [destination_id]
        current_id = destination_id

        while current_id != source_id:
            current_id = previous[current_id]
            route.append(current_id)

        route.reverse()

        return route

    def _validate_nodes(
        self,
        source_id: str,
        destination_id: str,
    ) -> None:
        """Validate source and destination nodes."""

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