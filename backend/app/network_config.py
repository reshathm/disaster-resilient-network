import json
import math
from dataclasses import dataclass
from pathlib import Path

from app.models.node import Node, NodeType
from app.network.topology import NetworkTopology


DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "default_network.json"
)

REQUIRED_NODE_FIELDS = {"id", "type", "x", "y"}
OPTIONAL_NODE_FIELDS = {"speed", "direction", "battery"}


class ConfigError(ValueError):
    """Raised when a network configuration file is invalid."""


@dataclass(frozen=True)
class NetworkConfig:
    """Validated description of the initial network."""

    communication_range: float
    nodes: tuple[dict, ...]


def load_network_config(
    path: Path = DEFAULT_CONFIG_PATH,
) -> NetworkConfig:
    """Read and validate a network configuration file."""

    try:
        with open(path, encoding="utf-8") as file:
            raw = json.load(file)

    except OSError as error:
        raise ConfigError(
            f"Cannot read network config '{path}': {error}"
        ) from error

    except json.JSONDecodeError as error:
        raise ConfigError(
            f"Network config '{path}' is not valid JSON: {error}"
        ) from error

    return parse_network_config(raw)


def parse_network_config(raw: object) -> NetworkConfig:
    """Validate raw configuration data."""

    if not isinstance(raw, dict):
        raise ConfigError("Network config must be a JSON object.")

    unknown = set(raw) - {"communication_range", "nodes"}

    if unknown:
        raise ConfigError(
            f"Unknown network config fields: {sorted(unknown)}."
        )

    communication_range = _number(
        raw.get("communication_range"),
        "communication_range",
    )

    if communication_range <= 0:
        raise ConfigError("communication_range must be greater than zero.")

    raw_nodes = raw.get("nodes")

    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise ConfigError("nodes must be a non-empty list.")

    seen_ids: set[str] = set()
    nodes = []

    for index, raw_node in enumerate(raw_nodes):
        node = _parse_node(raw_node, index)

        if node["node_id"] in seen_ids:
            raise ConfigError(
                f"Duplicate node id '{node['node_id']}'."
            )

        seen_ids.add(node["node_id"])
        nodes.append(node)

    return NetworkConfig(communication_range, tuple(nodes))


def build_topology(config: NetworkConfig) -> NetworkTopology:
    """Create a fresh topology from a validated configuration.

    Links are not configured: they follow from node positions and
    the communication range, exactly as after a node movement.
    """

    topology = NetworkTopology()

    for node in config.nodes:
        topology.add_node(Node(**node))

    topology.refresh_connections(config.communication_range)

    return topology


def _parse_node(raw_node: object, index: int) -> dict:
    label = f"nodes[{index}]"

    if not isinstance(raw_node, dict):
        raise ConfigError(f"{label} must be an object.")

    missing = REQUIRED_NODE_FIELDS - set(raw_node)

    if missing:
        raise ConfigError(f"{label} is missing fields: {sorted(missing)}.")

    unknown = set(raw_node) - REQUIRED_NODE_FIELDS - OPTIONAL_NODE_FIELDS

    if unknown:
        raise ConfigError(f"{label} has unknown fields: {sorted(unknown)}.")

    node_id = raw_node["id"]

    if not isinstance(node_id, str) or not node_id.strip():
        raise ConfigError(f"{label}.id must be a non-empty string.")

    try:
        node_type = NodeType(raw_node["type"])

    except ValueError:
        valid = sorted(member.value for member in NodeType)
        raise ConfigError(
            f"{label}.type '{raw_node['type']}' is not one of {valid}."
        ) from None

    # Only fields present in the file are passed on, so anything
    # omitted keeps the Node class default.
    node = {
        "node_id": node_id,
        "node_type": node_type,
        "x": _number(raw_node["x"], f"{label}.x"),
        "y": _number(raw_node["y"], f"{label}.y"),
    }

    if "speed" in raw_node:
        speed = _number(raw_node["speed"], f"{label}.speed")

        if speed < 0:
            raise ConfigError(f"{label}.speed must not be negative.")

        node["speed"] = speed

    if "direction" in raw_node:
        node["direction"] = _number(
            raw_node["direction"],
            f"{label}.direction",
        )

    if "battery" in raw_node:
        battery = _number(raw_node["battery"], f"{label}.battery")

        if not 0 <= battery <= 100:
            raise ConfigError(f"{label}.battery must be between 0 and 100.")

        node["battery"] = battery

    return node


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{name} must be a number.")

    if not math.isfinite(value):
        raise ConfigError(f"{name} must be a finite number.")

    return value
