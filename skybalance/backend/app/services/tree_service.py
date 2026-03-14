"""
TreeService: orchestrates AVL operations and persistence.
"""
import copy
from app.core import state
from app.models.flight_node import FlightNode


def _snapshot() -> dict:
    return copy.deepcopy(state.avl_tree.to_dict())


def load_from_json(data: dict, mode: str) -> dict:
    """
    mode='topology'  -> rebuild respecting parent/child structure.
    mode='insertion' -> insert one by one (AVL + BST in parallel).
    Returns comparison stats if mode=='insertion'.
    """
    # TODO: implement
    return {}


def undo_last_action() -> bool:
    if not state.undo_stack:
        return False
    snapshot = state.undo_stack.pop()
    state.avl_tree.from_topology(snapshot)
    return True


def save_named_version(name: str) -> None:
    state.named_versions[name] = _snapshot()


def restore_named_version(name: str) -> bool:
    snap = state.named_versions.get(name)
    if snap is None:
        return False
    state.undo_stack.append(_snapshot())
    state.avl_tree.from_topology(snap)
    return True


def set_critical_depth(depth: int) -> None:
    state.critical_depth = depth
    state.avl_tree.apply_depth_penalties(depth)


def push_undo_snapshot() -> None:
    state.undo_stack.append(_snapshot())