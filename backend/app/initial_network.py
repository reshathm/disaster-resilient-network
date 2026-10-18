from app.models.node import Node, NodeType
from app.network.topology import NetworkTopology


COMMUNICATION_RANGE = 16.0


def build_initial_network() -> NetworkTopology:
    """Build the default 5-node fully connected demo topology."""

    topology = NetworkTopology()

    topology.add_node(
        Node("R01", NodeType.RESCUE_TEAM, x=0, y=0)
    )

    topology.add_node(
        Node(
            "R02",
            NodeType.RESCUE_TEAM,
            x=5,
            y=0,
            speed=5,
            direction=180,
        )
    )

    topology.add_node(
        Node("R03", NodeType.DRONE, x=10, y=0)
    )

    topology.add_node(
        Node("R04", NodeType.FIRE_RESCUE, x=5, y=5)
    )

    topology.add_node(
        Node("C01", NodeType.COMMAND_CENTER, x=15, y=0)
    )

    # Fully connected mesh
    topology.connect_nodes("R01", "R02")
    topology.connect_nodes("R01", "R03")
    topology.connect_nodes("R01", "R04")
    topology.connect_nodes("R01", "C01")

    topology.connect_nodes("R02", "R03")
    topology.connect_nodes("R02", "R04")
    topology.connect_nodes("R02", "C01")

    topology.connect_nodes("R03", "R04")
    topology.connect_nodes("R03", "C01")

    topology.connect_nodes("R04", "C01")

    return topology
