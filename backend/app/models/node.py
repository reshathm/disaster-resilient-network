from dataclasses import dataclass, field
from enum import Enum
from typing import List


class NodeType(Enum):
    RESCUE_TEAM = "rescue_team"
    AMBULANCE = "ambulance"
    FIRE_RESCUE = "fire_rescue"
    POLICE = "police"
    DRONE = "drone"
    COMMAND_CENTER = "command_center"


class NodeStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    LOST = "lost"


@dataclass
class Node:
    node_id: str
    node_type: NodeType
    status: NodeStatus = NodeStatus.ONLINE
    battery: float = 100.0
    signal_strength: float = 100.0
    neighbors: List[str] = field(default_factory=list)

    # Position and movement tracking
    x: float = 0.0
    y: float = 0.0
    speed: float = 0.0
    direction: float = 0.0