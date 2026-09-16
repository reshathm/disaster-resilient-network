from typing import List

from app.models.message import Message
from app.network.event_log import EventLog
from app.network.self_healing import SelfHealingManager
from app.network.topology import NetworkTopology


class MessageService:
    """Handles sending messages through the network."""

    def __init__(
        self,
        topology: NetworkTopology,
        event_log: EventLog,
    ) -> None:
        self.topology = topology
        self.self_healing = SelfHealingManager(topology)
        self.event_log = event_log

    def send_message(self, message: Message) -> List[str]:
        """Send a message using the current available route."""

        route = self.self_healing.recover_route(
            message.source_id,
            message.destination_id,
        )

        self.event_log.record(
            "MESSAGE_DELIVERED",
            f"{message.message_id} delivered via {' -> '.join(route)}",
        )

        return route