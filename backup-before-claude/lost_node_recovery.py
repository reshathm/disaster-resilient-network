from typing import Dict

from app.models.node import NodeStatus
from app.network.helper_selection import HelperSelector
from app.network.location_tracker import LocationTracker
from app.network.search import SearchCoordinator
from app.network.topology import NetworkTopology


class LostNodeRecovery:
    """Coordinates the complete lost-node recovery workflow."""

    def __init__(
        self,
        topology: NetworkTopology,
        location_tracker: LocationTracker,
        communication_range: float = 10.0,
    ) -> None:
        self.topology = topology
        self.location_tracker = location_tracker
        self.communication_range = communication_range

        self.helper_selector = HelperSelector(topology)
        self.search_coordinator = SearchCoordinator(topology)

        self.lost_nodes: Dict[str, dict] = {}

    def mark_lost(self, node_id: str) -> None:
        """Mark a node as lost and begin recovery tracking."""

        node = self.topology.get_node(node_id)

        if node is None:
            raise ValueError(f"Node '{node_id}' does not exist.")

        node.status = NodeStatus.LOST

        self.lost_nodes[node_id] = {
            "status": "LOST",
            "node_id": node_id,
        }

    def predict_search_area(
        self,
        node_id: str,
        elapsed_time: float,
    ) -> dict:
        """Predict the lost node's position and search radius."""

        if node_id not in self.lost_nodes:
            raise ValueError(
                f"Node '{node_id}' is not marked as lost."
            )

        predicted_x, predicted_y = (
            self.location_tracker.predict_position(
                node_id,
                elapsed_time,
            )
        )

        radius = self.location_tracker.get_search_radius(
            node_id,
            elapsed_time,
        )

        result = {
            "node_id": node_id,
            "predicted_x": predicted_x,
            "predicted_y": predicted_y,
            "search_radius": radius,
        }

        self.lost_nodes[node_id].update(result)

        return result

    def recover(
        self,
        node_id: str,
        elapsed_time: float,
    ) -> dict:
        """Execute the complete lost-node recovery workflow."""

        if node_id not in self.lost_nodes:
            raise ValueError(
                f"Node '{node_id}' is not marked as lost."
            )

        prediction = self.predict_search_area(
            node_id,
            elapsed_time,
        )

        helper = self.helper_selector.select_helper(
            node_id,
            prediction["predicted_x"],
            prediction["predicted_y"],
        )

        search_route = self.search_coordinator.find_search_route(
            helper["node_id"],
            prediction["predicted_x"],
            prediction["predicted_y"],
            prediction["search_radius"],
        )

        helper_travelled = search_route["travel_required"]

        if helper_travelled:
            helper_node = self.topology.get_node(
                helper["node_id"]
            )

            helper_node.x = prediction["predicted_x"]
            helper_node.y = prediction["predicted_y"]

        search_result = self.search_coordinator.search_for_node(
            helper["node_id"],
            node_id,
            prediction["search_radius"],
            target_x=(
                prediction["predicted_x"]
                if helper_travelled
                else None
            ),
            target_y=(
                prediction["predicted_y"]
                if helper_travelled
                else None
            ),
        )

        if not search_result["discovered"]:
            self.lost_nodes[node_id]["status"] = "SEARCHING"

            return {
                "status": "SEARCHING",
                "prediction": prediction,
                "helper": helper,
                "search": search_route,
                "discovery": search_result,
            }

        # The simulated search has discovered the lost node
        # at the predicted search location.
        node = self.topology.get_node(node_id)

        node.x = prediction["predicted_x"]
        node.y = prediction["predicted_y"]
        node.status = NodeStatus.ONLINE

        # Rebuild the node's connections using its newly
        # discovered simulated position.
        connections = self.topology.reconnect_node(
            node_id,
            self.communication_range,
        )

        self.lost_nodes[node_id].update(
            {
                "status": "FOUND",
                "connections": connections,
            }
        )

        return {
            "status": "FOUND",
            "prediction": prediction,
            "helper": helper,
            "search": search_route,
            "discovery": search_result,
            "reconnected_to": connections,
        }

    def get_status(self, node_id: str) -> dict:
        """Return the current recovery information."""

        if node_id not in self.lost_nodes:
            raise ValueError(
                f"Node '{node_id}' does not exist in recovery tracking."
            )

        return dict(self.lost_nodes[node_id])