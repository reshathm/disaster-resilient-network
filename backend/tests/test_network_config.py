import json

import pytest

from app.initial_network import COMMUNICATION_RANGE, build_initial_network
from app.models.node import Node, NodeStatus, NodeType
from app.network_config import (
    DEFAULT_CONFIG_PATH,
    ConfigError,
    build_topology,
    load_network_config,
    parse_network_config,
)


def valid_config(**changes):
    config = {
        "communication_range": 16.0,
        "nodes": [
            {"id": "A", "type": "rescue_team", "x": 0, "y": 0},
            {"id": "B", "type": "drone", "x": 10, "y": 0},
        ],
    }
    config.update(changes)
    return config


def test_default_network_matches_original_scenario():
    topology = build_initial_network()

    expected = {
        "R01": (NodeType.RESCUE_TEAM, 0, 0, 0.0, 0.0),
        "R02": (NodeType.RESCUE_TEAM, 5, 0, 5, 180),
        "R03": (NodeType.DRONE, 10, 0, 0.0, 0.0),
        "R04": (NodeType.FIRE_RESCUE, 5, 5, 0.0, 0.0),
        "C01": (NodeType.COMMAND_CENTER, 15, 0, 0.0, 0.0),
    }

    assert COMMUNICATION_RANGE == 16.0
    assert [n.node_id for n in topology.get_all_nodes()] == list(expected)

    for node_id, (node_type, x, y, speed, direction) in expected.items():
        node = topology.get_node(node_id)

        assert node.node_type == node_type
        assert (node.x, node.y) == (x, y)
        assert (node.speed, node.direction) == (speed, direction)
        assert node.status == NodeStatus.ONLINE
        assert node.battery == 100.0
        assert node.signal_strength == 100.0


def test_default_network_has_original_links_and_neighbor_order():
    topology = build_initial_network()

    # Original hardcoded mesh: every pair connected, weight 1.0,
    # with neighbors listed in the order the links were created.
    assert topology.get_node("R01").neighbors == ["R02", "R03", "R04", "C01"]
    assert topology.get_node("R02").neighbors == ["R01", "R03", "R04", "C01"]
    assert topology.get_node("R03").neighbors == ["R01", "R02", "R04", "C01"]
    assert topology.get_node("R04").neighbors == ["R01", "R02", "R03", "C01"]
    assert topology.get_node("C01").neighbors == ["R01", "R02", "R03", "R04"]

    link_count = 0

    for node in topology.get_all_nodes():
        for neighbor_id, weight in topology.get_neighbors(node.node_id).items():
            assert weight == 1.0
            link_count += 1

    assert link_count == 20  # 10 two-way links


def test_each_build_returns_an_independent_network():
    first = build_initial_network()
    second = build_initial_network()

    first.get_node("R02").x = 99
    first.disconnect_nodes("R01", "R02")

    assert second.get_node("R02").x == 5
    assert "R02" in second.get_node("R01").neighbors


def test_config_file_is_not_modified_by_simulation():
    path = DEFAULT_CONFIG_PATH
    before = path.read_text(encoding="utf-8")

    topology = build_initial_network()
    topology.get_node("R02").x = 99
    topology.refresh_connections(COMMUNICATION_RANGE)

    assert path.read_text(encoding="utf-8") == before


def test_optional_fields_use_node_defaults():
    config = parse_network_config(valid_config())
    node = build_topology(config).get_node("A")
    default = Node("A", NodeType.RESCUE_TEAM)

    assert node.speed == default.speed
    assert node.direction == default.direction
    assert node.battery == default.battery
    assert node.signal_strength == default.signal_strength


def test_optional_fields_are_applied():
    raw = valid_config()
    raw["nodes"][0].update({"speed": 3, "direction": 45, "battery": 80})

    node = build_topology(parse_network_config(raw)).get_node("A")

    assert (node.speed, node.direction, node.battery) == (3, 45, 80)


def test_links_follow_positions_not_configuration():
    raw = valid_config()
    raw["nodes"][1]["x"] = 40  # outside the 16 unit range

    topology = build_topology(parse_network_config(raw))

    assert topology.get_node("A").neighbors == []
    assert topology.get_node("B").neighbors == []


def test_load_network_config_reads_a_file(tmp_path):
    path = tmp_path / "net.json"
    path.write_text(json.dumps(valid_config()), encoding="utf-8")

    config = load_network_config(path)

    assert config.communication_range == 16.0
    assert [n["node_id"] for n in config.nodes] == ["A", "B"]


def test_missing_and_malformed_files_are_rejected(tmp_path):
    with pytest.raises(ConfigError):
        load_network_config(tmp_path / "missing.json")

    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")

    with pytest.raises(ConfigError):
        load_network_config(bad)


def bad_node(**changes):
    node = {"id": "A", "type": "rescue_team", "x": 0, "y": 0}
    node.update(changes)
    return valid_config(nodes=[node])


@pytest.mark.parametrize(
    "raw",
    [
        [],
        valid_config(communication_range=0),
        valid_config(communication_range=-5),
        valid_config(communication_range="16"),
        valid_config(communication_range=True),
        valid_config(communication_range=float("inf")),
        valid_config(nodes=[]),
        valid_config(nodes="nope"),
        valid_config(extra=1),
        valid_config(
            nodes=[
                {"id": "A", "type": "drone", "x": 0, "y": 0},
                {"id": "A", "type": "drone", "x": 1, "y": 1},
            ]
        ),
        valid_config(nodes=["A"]),
        valid_config(nodes=[{"id": "A", "type": "drone", "x": 0}]),
        bad_node(id=""),
        bad_node(id=7),
        bad_node(type="submarine"),
        bad_node(x="0"),
        bad_node(y=None),
        bad_node(x=float("nan")),
        bad_node(speed=-1),
        bad_node(speed="fast"),
        bad_node(direction=float("inf")),
        bad_node(battery=-1),
        bad_node(battery=101),
        bad_node(colour="red"),
    ],
)
def test_invalid_configs_are_rejected(raw):
    with pytest.raises(ConfigError):
        parse_network_config(raw)
