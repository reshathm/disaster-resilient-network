import math
from typing import Dict, List

from app.models.node import NodeStatus
from app.network.topology import NetworkTopology


class HelperSelector:
    """Selects the most suitable surviving node to search for a lost node."""

    def __init__(self, topology: NetworkTopology) -> None:
        self.topology = topology

    def select_helper(
        self,
        lost_node_id: str,
        predicted_x: float,
        predicted_y: float,
    ) -> Dict:
        """Select the best available helper based on distance and node health."""

        candidates: List[Dict] = []

        for node in self.topology.get_all_nodes():
            if node.node_id == lost_node_id:
                continue

            if node.status != NodeStatus.ONLINE:
                continue

            distance = math.sqrt(
                (node.x - predicted_x) ** 2
                + (node.y - predicted_y) ** 2
            )

            score = self._calculate_score(
                distance,
                node.battery,
                node.signal_strength,
            )

            candidates.append(
                {
                    "node_id": node.node_id,
                    "distance": distance,
                    "battery": node.battery,
                    "signal_strength": node.signal_strength,
                    "score": score,
                }
            )

        if not candidates:
            raise ValueError("No available helper nodes.")

        candidates.sort(key=lambda candidate: candidate["score"])

        return candidates[0]

    def rank_helpers(
        self,
        lost_node_id: str,
        predicted_x: float,
        predicted_y: float,
    ) -> List[Dict]:
        """Return all available helpers ranked by suitability."""

        candidates: List[Dict] = []

        for node in self.topology.get_all_nodes():
            if node.node_id == lost_node_id:
                continue

            if node.status != NodeStatus.ONLINE:
                continue

            distance = math.sqrt(
                (node.x - predicted_x) ** 2
                + (node.y - predicted_y) ** 2
            )

            score = self._calculate_score(
                distance,
                node.battery,
                node.signal_strength,
            )

            candidates.append(
                {
                    "node_id": node.node_id,
                    "distance": distance,
                    "battery": node.battery,
                    "signal_strength": node.signal_strength,
                    "score": score,
                }
            )

        candidates.sort(key=lambda candidate: candidate["score"])

        return candidates

    @staticmethod
    def _calculate_score(
        distance: float,
        battery: float,
        signal_strength: float,
    ) -> float:
        """Calculate a simple suitability score. Lower is better."""

        return (
            distance
            + (100.0 - battery) * 0.2
            + (100.0 - signal_strength) * 0.1
        )