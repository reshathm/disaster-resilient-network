from __future__ import annotations

import math
from threading import RLock

from app.network.topology import NetworkTopology


class SimulationEngine:
    """Advance network movement using deterministic simulation time."""

    def __init__(
        self,
        topology: NetworkTopology,
        communication_range: float,
        lock: RLock | None = None,
    ) -> None:
        if not math.isfinite(communication_range) or communication_range <= 0:
            raise ValueError("Communication range must be positive and finite.")

        self.topology = topology
        self.communication_range = communication_range
        self.simulation_time = 0.0
        self._moving_nodes: set[str] = set()
        self.lock = lock if lock is not None else RLock()

    def start_movement(self, node_id: str) -> None:
        """Activate movement using the node's speed and direction."""
        with self.lock:
            self._get_node(node_id)
            self._moving_nodes.add(node_id)

    def stop_movement(self, node_id: str) -> None:
        """Stop movement without changing the node's configured speed."""
        with self.lock:
            self._get_node(node_id)
            self._moving_nodes.discard(node_id)

    def step(self, dt: float) -> None:
        """Advance the simulation by dt seconds."""
        if not math.isfinite(dt) or dt <= 0:
            raise ValueError("Time step must be positive and finite.")

        with self.lock:
            for node_id in sorted(self._moving_nodes):
                node = self._get_node(node_id)

                angle = math.radians(node.direction)
                node.x += node.speed * math.cos(angle) * dt
                node.y += node.speed * math.sin(angle) * dt

            self.topology.refresh_connections(self.communication_range)
            self.simulation_time += dt

    def _get_node(self, node_id: str):
        node = self.topology.get_node(node_id)

        if node is None:
            raise ValueError(f"Node '{node_id}' does not exist.")

        return node
