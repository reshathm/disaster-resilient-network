from app.initial_network import COMMUNICATION_RANGE, build_initial_network
from app.state import ApplicationState


state = ApplicationState(build_initial_network(), COMMUNICATION_RANGE)


def get_state() -> ApplicationState:
    """Provide the shared application state to API endpoints."""
    return state
