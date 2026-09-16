import heapq
from typing import List, Tuple

from app.models.message import Message, MessagePriority


class MessageQueue:
    """Stores messages according to their priority."""

    PRIORITY_ORDER = {
        MessagePriority.CRITICAL: 1,
        MessagePriority.HIGH: 2,
        MessagePriority.NORMAL: 3,
    }

    def __init__(self) -> None:
        self._queue: List[Tuple[int, int, Message]] = []
        self._sequence = 0

    def enqueue(self, message: Message) -> None:
        """Add a message to the queue."""
        priority = self.PRIORITY_ORDER[message.priority]

        heapq.heappush(
            self._queue,
            (priority, self._sequence, message),
        )

        self._sequence += 1

    def dequeue(self) -> Message:
        """Remove and return the highest-priority message."""
        if not self._queue:
            raise ValueError("Message queue is empty.")

        _, _, message = heapq.heappop(self._queue)
        return message

    def is_empty(self) -> bool:
        """Return whether the queue contains no messages."""
        return len(self._queue) == 0