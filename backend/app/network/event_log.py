from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class NetworkEvent:
    event_type: str
    message: str
    timestamp: datetime


class EventLog:
    """Stores network events in chronological order."""

    def __init__(self) -> None:
        self._events: List[NetworkEvent] = []

    def record(self, event_type: str, message: str) -> None:
        """Record a new network event."""
        event = NetworkEvent(
            event_type=event_type,
            message=message,
            timestamp=datetime.now(),
        )

        self._events.append(event)

    def get_events(self) -> List[NetworkEvent]:
        """Return all recorded events."""
        return list(self._events)

    def clear(self) -> None:
        """Remove all recorded events."""
        self._events.clear()