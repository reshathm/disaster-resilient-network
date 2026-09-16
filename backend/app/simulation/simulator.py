from app.models.node import NodeStatus
from app.network.connection_monitor import ConnectionMonitor
from app.network.location_tracker import LocationTracker
from app.network.lost_node_recovery import LostNodeRecovery
from app.network.topology import NetworkTopology


class NetworkSimulator:
    """Simulates movement, failures, and recovery of network nodes."""

    def __init__(
        self,
        topology: NetworkTopology,
        communication_range: float = 10.0,
        recovery_manager: LostNodeRecovery | None = None,
        location_tracker: LocationTracker | None = None,
    ) -> None:
        self.topology = topology
        self.communication_range = communication_range

        self.connection_monitor = ConnectionMonitor(
            topology,
            communication_range,
        )

        self.recovery_manager = recovery_manager

        self.location_tracker = (
            location_tracker
            if location_tracker is not None
            else LocationTracker()
        )

    def fail_node(self, node_id: str) -> None:
        """Simulate a node failure."""
        node = self._get_node(node_id)

        if node.status == NodeStatus.OFFLINE:
            raise ValueError(
                f"Node '{node_id}' is already offline."
            )

        node.status = NodeStatus.OFFLINE

    def recover_node(self, node_id: str) -> None:
        """Simulate a node recovering."""
        node = self._get_node(node_id)

        if node.status == NodeStatus.ONLINE:
            raise ValueError(
                f"Node '{node_id}' is already online."
            )

        node.status = NodeStatus.ONLINE

    def move_node(
        self,
        node_id: str,
        x: float,
        y: float,
    ) -> bool:
        """Move a node, track its location, and detect communication loss."""

        node = self._get_node(node_id)

        node.x = x
        node.y = y

        self.location_tracker.update(
            node_id,
            node.x,
            node.y,
            node.speed,
            node.direction,
        )

        self.topology.refresh_connections(
            self.communication_range
        )

        lost_detected = self.connection_monitor.detect_lost_node(
            node_id
        )

        if lost_detected and self.recovery_manager is not None:
            self.recovery_manager.mark_lost(node_id)

        return lost_detected

    def _get_node(self, node_id: str):
        """Return a node or raise an error if it doesn't exist."""
        node = self.topology.get_node(node_id)

        if node is None:
            raise ValueError(
                f"Node '{node_id}' does not exist."
            )

        return node