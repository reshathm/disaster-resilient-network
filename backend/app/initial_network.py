from app.network.topology import NetworkTopology
from app.network_config import build_topology, load_network_config


_CONFIG = load_network_config()

COMMUNICATION_RANGE = _CONFIG.communication_range


def build_initial_network() -> NetworkTopology:
    """Build a fresh copy of the configured initial network."""

    return build_topology(_CONFIG)
