from app.core import state
from app.models.flight_node import FlightNode
from app.services.tree_service import push_undo_snapshot
from typing import Optional


def add_flight(data: dict) -> FlightNode:
    push_undo_snapshot()
    node = FlightNode(**data)
    state.avl_tree.insert(node)
    state.avl_tree.apply_depth_penalties(state.critical_depth)
    return node


def remove_flight(code: str) -> bool:
    push_undo_snapshot()
    return state.avl_tree.delete(code)


def cancel_flight(code: str) -> int:
    push_undo_snapshot()
    removed = state.avl_tree.cancel(code)
    state.stats["mass_cancellations"] += 1
    return removed


def modify_flight(code: str, updates: dict) -> bool:
    push_undo_snapshot()
    return state.avl_tree.update(code, **updates)


def get_flight(code: str) -> Optional[FlightNode]:
    return state.avl_tree.search(code)


def eliminate_least_profitable() -> Optional[str]:
    node = state.avl_tree.find_least_profitable()
    if node is None:
        return None
    cancel_flight(node.code)
    return node.code