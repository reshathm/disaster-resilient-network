import pytest

from app.models.message import Message, MessagePriority
from app.network.message_queue import MessageQueue


def create_message(
    message_id: str,
    priority: MessagePriority,
) -> Message:
    return Message(
        message_id=message_id,
        source_id="R01",
        destination_id="C01",
        content=f"Message {message_id}",
        priority=priority,
    )


def test_critical_messages_are_processed_first():
    queue = MessageQueue()

    queue.enqueue(create_message("M001", MessagePriority.NORMAL))
    queue.enqueue(create_message("M002", MessagePriority.CRITICAL))
    queue.enqueue(create_message("M003", MessagePriority.HIGH))

    assert queue.dequeue().message_id == "M002"
    assert queue.dequeue().message_id == "M003"
    assert queue.dequeue().message_id == "M001"


def test_same_priority_preserves_order():
    queue = MessageQueue()

    queue.enqueue(create_message("M001", MessagePriority.HIGH))
    queue.enqueue(create_message("M002", MessagePriority.HIGH))
    queue.enqueue(create_message("M003", MessagePriority.HIGH))

    assert queue.dequeue().message_id == "M001"
    assert queue.dequeue().message_id == "M002"
    assert queue.dequeue().message_id == "M003"


def test_empty_queue_raises_error():
    queue = MessageQueue()

    with pytest.raises(ValueError, match="Message queue is empty"):
        queue.dequeue()


def test_queue_reports_empty_state():
    queue = MessageQueue()

    assert queue.is_empty()

    queue.enqueue(create_message("M001", MessagePriority.NORMAL))

    assert not queue.is_empty()

    queue.dequeue()

    assert queue.is_empty()