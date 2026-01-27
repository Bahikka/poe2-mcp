import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.parsers.passive_tree_resolver import PassiveTreeResolver


def test_class_start_and_connectivity_with_ascendancy():
    resolver = PassiveTreeResolver(data_dir=Path("data"))
    resolver._ensure_loaded()

    start_node = 44683
    assert start_node in resolver._nodes

    neighbors = [
        nid
        for nid in resolver._nodes[start_node].get("connections", [])
        if nid in resolver._nodes and not resolver._nodes[nid].get("is_ascendancy", False)
    ]
    assert neighbors

    ascendancy_node = next(
        nid for nid, data in resolver._nodes.items() if data.get("is_ascendancy", False)
    )

    node_ids = [start_node, neighbors[0], ascendancy_node]
    analysis = resolver.analyze_build(node_ids, find_recommendations=False)

    assert analysis.class_start == "MONK"
    assert analysis.is_connected is True
    assert ascendancy_node in analysis.ascendancy_nodes_present
