import math

from app.models.node import NodeStatus
from app.network.routing import NetworkRouter
from app.network.topology import NetworkTopology


class SearchCoordinator:
    """Coordinates A* search and simulated lost-node discovery."""

    def __init__(self, topology: NetworkTopology) -> None:
        self.topology = topology
        self.router = NetworkRouter(topology)

    def find_search_route(
        self,
        helper_id: str,
        target_x: float,
        target_y: float,
        search_radius: float = 0.0,
    ) -> dict:
        """Plan helper movement toward a predicted search area."""

        helper = self.topology.get_node(helper_id)

        if helper is None:
            raise ValueError(
                f"Helper node '{helper_id}' does not exist."
            )

        distance = math.sqrt(
            (helper.x - target_x) ** 2
            + (helper.y - target_y) ** 2
        )

        if distance <= search_radius:
            return {
                "helper_id": helper_id,
                "target": {
                    "x": target_x,
                    "y": target_y,
                },
                "route": [helper_id],
                "final_node": helper_id,
                "distance_to_search_area": distance,
                "travel_required": False,
            }

        return {
            "helper_id": helper_id,
            "target": {
                "x": target_x,
                "y": target_y,
            },
            "route": [helper_id, "SEARCH_AREA"],
            "final_node": "SEARCH_AREA",
            "distance_to_search_area": distance,
            "travel_required": True,
        }

    def search_for_node(
        self,
        helper_id: str,
        lost_node_id: str,
        search_radius: float,
        target_x: float | None = None,
        target_y: float | None = None,
    ) -> dict:
        """Simulate a helper searching for a lost node."""

        helper = self.topology.get_node(helper_id)
        lost_node = self.topology.get_node(lost_node_id)

        if helper is None:
            raise ValueError(
                f"Helper node '{helper_id}' does not exist."
            )

        if lost_node is None:
            raise ValueError(
                f"Lost node '{lost_node_id}' does not exist."
            )

        if lost_node.status != NodeStatus.LOST:
            raise ValueError(
                f"Node '{lost_node_id}' is not currently lost."
            )

        if target_x is not None and target_y is not None:
            # Search against the predicted location.
            distance = math.sqrt(
                (helper.x - target_x) ** 2
                + (helper.y - target_y) ** 2
            )
        else:
            # Fall back to the lost node's known simulated position.
            distance = math.sqrt(
                (helper.x - lost_node.x) ** 2
                + (helper.y - lost_node.y) ** 2
            )

        discovered = distance <= search_radius

        if discovered:
            lost_node.status = NodeStatus.ONLINE

        return {
            "helper_id": helper_id,
            "lost_node_id": lost_node_id,
            "distance": distance,
            "search_radius": search_radius,
            "discovered": discovered,
            "status": "FOUND" if discovered else "NOT_FOUND",
        }