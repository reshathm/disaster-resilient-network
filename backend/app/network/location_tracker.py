import math
from typing import Dict


class LocationTracker:
    """Tracks and predicts the location of network nodes."""

    def __init__(self) -> None:
        self.last_known: Dict[str, dict] = {}

    def update(
        self,
        node_id: str,
        x: float,
        y: float,
        speed: float,
        direction: float,
    ) -> None:
        """Store the latest known movement state of a node."""
        self.last_known[node_id] = {
            "x": x,
            "y": y,
            "speed": speed,
            "direction": direction,
        }

    def predict_position(
        self,
        node_id: str,
        elapsed_time: float,
    ) -> tuple[float, float]:
        """Predict a node's position after the given time."""
        if node_id not in self.last_known:
            raise ValueError(f"No location data for node '{node_id}'.")

        data = self.last_known[node_id]
        angle = math.radians(data["direction"])

        x = data["x"] + data["speed"] * math.cos(angle) * elapsed_time
        y = data["y"] + data["speed"] * math.sin(angle) * elapsed_time

        return x, y

    def get_search_radius(
        self,
        node_id: str,
        elapsed_time: float,
    ) -> float:
        """Calculate the uncertainty radius around the predicted position."""
        if node_id not in self.last_known:
            raise ValueError(f"No location data for node '{node_id}'.")

        speed = self.last_known[node_id]["speed"]

        return max(5.0, speed * elapsed_time * 0.2)