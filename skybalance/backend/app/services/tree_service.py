"""
TreeService: orchestrates AVL operations and persistence.
"""
import copy

from app.core import state
from app.models.avl_tree import AVLTree
from app.models.bst_tree import BSTTree
from app.utils.serializer import dict_to_node


def _snapshot() -> dict:
    return copy.deepcopy(state.avl_tree.to_dict())


def _stats_for(tree, tree_type: str) -> dict:
    rotations = getattr(tree, "rotations", {"LL": 0, "RR": 0, "LR": 0, "RL": 0})
    mass_cancellations = getattr(tree, "mass_cancellation_count", 0)
    return {
        "tree_type": tree_type,
        "root_code": tree.root.code if tree.root else None,
        "total_height": tree.height(),
        "leaf_count": tree.leaf_count(),
        "node_count": tree.node_count() if hasattr(tree, "node_count") else 0,
        "rotations": rotations,
        "mass_cancellations": mass_cancellations,
    }


def load_from_json(data: dict, mode: str) -> dict:
    """
    mode='topology'  -> rebuild respecting parent/child structure.
    mode='insertion' -> insert one by one (AVL + BST in parallel).
    Returns comparison stats for the UI.
    """
    normalized_mode = (mode or "").strip().lower()
    if not normalized_mode and isinstance(data, dict):
        normalized_mode = str(data.get("mode", data.get("modo", ""))).strip().lower()

    if normalized_mode not in {"topology", "insertion"}:
        raise ValueError("El modo debe ser 'topology' o 'insertion'.")

    previous_snapshot = _snapshot()
    new_avl = AVLTree()
    new_bst = BSTTree()

    if normalized_mode == "topology":
        payload = data
        if isinstance(data, dict):
            payload = (
                data.get("tree")
                or data.get("root")
                or data.get("arbol")
                or data.get("raiz")
                or data
            )
        new_avl.from_topology(payload)
    else:
        if isinstance(data, list):
            flights = data
        elif isinstance(data, dict):
            flights = data.get("flights") or data.get("vuelos") or []
        else:
            flights = []

        if not isinstance(flights, list) or len(flights) == 0:
            raise ValueError("Para el modo 'insertion' se requiere una lista 'flights' o 'vuelos'.")

        try:
            for flight in flights:
                new_avl.insert(dict_to_node(flight))
                new_bst.insert(dict_to_node(flight))
        except (TypeError, KeyError, ValueError) as exc:
            raise ValueError(f"El JSON de vuelos no tiene el formato esperado: {exc}") from exc

    if previous_snapshot.get("root") is not None:
        state.undo_stack.append(previous_snapshot)

    state.avl_tree = new_avl
    state.bst_tree = new_bst

    return {
        "mode": normalized_mode,
        "message": f"Árbol cargado correctamente en modo {normalized_mode}.",
        "avl": state.avl_tree.to_dict(),
        "bst": state.bst_tree.to_dict(),
        "avl_stats": _stats_for(state.avl_tree, "avl"),
        "bst_stats": _stats_for(state.bst_tree, "bst"),
    }


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