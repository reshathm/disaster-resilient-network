from typing import List

from app.models.message import Message
from app.network.routing import NetworkRouter
from app.network.topology import NetworkTopology


class MessageService:
    """Handles sending messages through the network."""

    def __init__(self, topology: NetworkTopology) -> None:
        self.topology = topology
        self.router = NetworkRouter(topology)

    def send_message(self, message: Message) -> List[str]:
        """Send a message and return the route used."""

        route = self.router.find_route(
            message.source_id,
            message.destination_id,
        )

        return route