from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_state
from app.locked_route import LockedRoute
from app.message_requests import MessageRequest
from app.models.message import Message
from app.state import ApplicationState


router = APIRouter(route_class=LockedRoute, prefix="/network/messages", tags=["Messages"])


@router.post("/send")
def send_message(
    request: MessageRequest,
    state: Annotated[ApplicationState, Depends(get_state)],
) -> dict:
    """Send an emergency message through the mesh network."""

    message = Message(
        message_id=request.message_id,
        source_id=request.source_id,
        destination_id=request.destination_id,
        content=request.content,
        priority=request.priority,
    )

    try:
        route = state.message_service.send_message(message)

    except ValueError as error:
        return {
            "message_id": message.message_id,
            "source": message.source_id,
            "destination": message.destination_id,
            "status": "failed",
            "error": str(error),
        }

    return {
        "message_id": message.message_id,
        "source": message.source_id,
        "destination": message.destination_id,
        "content": message.content,
        "priority": message.priority.value,
        "status": "delivered",
        "route": route,
    }
