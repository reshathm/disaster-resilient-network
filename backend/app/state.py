from threading import RLock

from app.network.event_log import EventLog
from app.network.location_tracker import LocationTracker
from app.network.lost_node_recovery import LostNodeRecovery
from app.network.messaging import MessageService
from app.network.monitor import NetworkMonitor
from app.network.self_healing import SelfHealingManager
from app.network.topology import NetworkTopology
from app.simulation.simulator import NetworkSimulator


class ApplicationState:
    """Manage the shared services used by the simulation."""

    def __init__(
        self,
        topology: NetworkTopology,
        communication_range: float,
    ):
        self.lock = RLock()
        self.communication_range = communication_range
        self.event_log = EventLog()
        self._initialize_services(topology)

    def _initialize_services(self, topology: NetworkTopology):
        self.network = topology
        self.monitor = NetworkMonitor(self.network)
        self.self_healing = SelfHealingManager(self.network)
        self.message_service = MessageService(
            self.network,
            self.event_log,
        )
        self.location_tracker = LocationTracker()
        self.recovery_manager = LostNodeRecovery(
            self.network,
            self.location_tracker,
            communication_range=self.communication_range,
        )
        self.simulator = NetworkSimulator(
            self.network,
            communication_range=self.communication_range,
            recovery_manager=self.recovery_manager,
            location_tracker=self.location_tracker,
        )

    def reset(self, topology: NetworkTopology):
        """Rebuild services while preserving the event log instance."""
        with self.lock:
            self._initialize_services(topology)
            self.event_log.clear()
            self.event_log.record(
                "RESET",
                "Network reset to initial topology.",
            )
