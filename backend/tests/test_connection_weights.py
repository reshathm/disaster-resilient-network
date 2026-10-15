import math

import pytest

from app.models.node import Node, NodeType
from app.network.topology import NetworkTopology


@pytest.mark.parametrize("weight", [
    -1,
    0,
    float("nan"),
    float("inf"),
    float("-inf"),
])
def test_invalid_connection_weights_are_rejected(weight):
    topology = NetworkTopology()

    topology.add_node(Node("A", NodeType.RESCUE_TEAM))
    topology.add_node(Node("B", NodeType.RESCUE_TEAM))

    with pytest.raises(ValueError):
        topology.connect_nodes("A", "B", weight=weight)


@pytest.mark.parametrize("weight", [0.5, 1.0, 10.0])
def test_valid_connection_weights_are_accepted(weight):
    topology = NetworkTopology()

    topology.add_node(Node("A", NodeType.RESCUE_TEAM))
    topology.add_node(Node("B", NodeType.RESCUE_TEAM))

    topology.connect_nodes("A", "B", weight=weight)

    assert math.isclose(topology.get_weight("A", "B"), weight)
    assert math.isclose(topology.get_weight("B", "A"), weight)
