from app.models.node import Node, NodeType, NodeStatus
from app.network.search import SearchCoordinator
from app.network.topology import NetworkTopology


def build_search_network():
    topology = NetworkTopology()

    topology.add_node(
        Node("R01", NodeType.RESCUE_TEAM, x=0, y=0)
    )
    topology.add_node(
        Node("R02", NodeType.RESCUE_TEAM, x=29, y=60)
    )
    topology.add_node(
        Node("R03", NodeType.RESCUE_TEAM, x=40, y=60)
    )
    topology.add_node(
        Node(
            "R04",
            NodeType.RESCUE_TEAM,
            x=25,
            y=60,
            battery=95,
            signal_strength=95,
        )
    )
    topology.add_node(
        Node("C01", NodeType.COMMAND_CENTER, x=50, y=60)
    )

    topology.connect_nodes("R01", "R04")
    topology.connect_nodes("R04", "R03")
    topology.connect_nodes("R03", "C01")

    return topology


def test_helper_already_inside_search_area():
    topology = build_search_network()
    coordinator = SearchCoordinator(topology)

    result = coordinator.find_search_route(
        helper_id="R04",
        target_x=25,
        target_y=60,
        search_radius=5,
    )

    assert result["route"] == ["R04"]
    assert result["final_node"] == "R04"
    assert result["distance_to_search_area"] == 0
    assert result["travel_required"] is False


def test_search_discovers_lost_node_inside_radius():
    topology = build_search_network()
    coordinator = SearchCoordinator(topology)

    topology.get_node("R02").status = NodeStatus.LOST

    result = coordinator.search_for_node(
        helper_id="R04",
        lost_node_id="R02",
        search_radius=5,
    )

    assert result["discovered"] is True
    assert result["status"] == "FOUND"
    assert result["distance"] == 4
    assert topology.get_node("R02").status == NodeStatus.ONLINE