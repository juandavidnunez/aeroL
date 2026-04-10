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
    print(f"load_from_json called with mode: {mode}, data keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
    normalized_mode = (mode or "").strip().lower()
    if not normalized_mode and isinstance(data, dict):
        normalized_mode = str(data.get("mode", data.get("modo", ""))).strip().lower()

    print(f"normalized_mode: {normalized_mode}")
    if normalized_mode not in {"topology", "insertion"}:
        raise ValueError("El modo debe ser 'topology' o 'insertion'.")

    # Autocorrección defensiva del modo cuando frontend o archivo vienen ambiguos.
    # Si el modo recibido es 'insertion' pero el payload parece topología, forzamos topología.
    if normalized_mode == "insertion" and isinstance(data, dict):
        topology_payload = (
            data.get("tree")
            or data.get("root")
            or data.get("arbol")
            or data.get("raiz")
            or data
        )
        has_flights = isinstance(data.get("flights") or data.get("vuelos"), list)
        print(f"topology_payload type: {type(topology_payload)}, has_flights: {has_flights}")
        if isinstance(topology_payload, dict):
            has_code = isinstance(topology_payload.get("code") or topology_payload.get("codigo"), str)
            has_children = ("left" in topology_payload) or ("right" in topology_payload) or ("izquierdo" in topology_payload) or ("derecho" in topology_payload)
            print(f"has_code: {has_code}, has_children: {has_children}")
            if has_code and has_children and not has_flights:
                normalized_mode = "topology"
                print("Switched to topology mode")

    # Autocorrección inversa: si llega 'topology' pero realmente es lista de vuelos.
    if normalized_mode == "topology":
        if isinstance(data, list):
            normalized_mode = "insertion"
        elif isinstance(data, dict) and isinstance(data.get("flights") or data.get("vuelos"), list):
            normalized_mode = "insertion"

    print(f"Final mode: {normalized_mode}")

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

    # IMPORTANTE: NO guardar snapshot al cargar archivo para que deshacer no vuelva a archivos anteriores
    # El undo_stack solo debe contener cambios DENTRO del archivo actual

    state.avl_tree = new_avl
    state.bst_tree = new_bst
    # Limpiar el undo_stack al cargar un nuevo archivo
    state.undo_stack.clear()

    # Apply critical depth penalties to newly loaded trees
    print(f"🟢 load_from_json() - Aplicando penalizaciones con profundidad crítica = {state.critical_depth}")
    state.avl_tree.apply_depth_penalties(state.critical_depth)
    state.bst_tree.apply_depth_penalties(state.critical_depth)
    
    avl_critical = sum(1 for node in state.avl_tree.bfs() if node.is_critical)
    bst_critical = sum(1 for node in state.bst_tree.bfs() if node.is_critical)
    print(f"   AVL: {avl_critical} nodos críticos | BST: {bst_critical} nodos críticos")
    
    # Guardar snapshot base del archivo cargado
    # Permite deshacer cambios dentro del archivo sin volver a archivos anteriores
    state.undo_stack.append(_snapshot())
    print(f"✅ Snapshot base guardado para permitir deshacer")

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


def delete_named_version(name: str) -> bool:
    if name in state.named_versions:
        del state.named_versions[name]
        return True
    return False


def set_critical_depth(depth: int) -> None:
    """Set critical depth and apply penalties to all nodes in both trees"""
    print(f"🔧 tree_service.set_critical_depth({depth})")
    state.critical_depth = depth
    
    # Aplicar penalizaciones a AVL
    state.avl_tree.apply_depth_penalties(depth)
    avl_critical = sum(1 for node in state.avl_tree.bfs() if node.is_critical)
    print(f"   AVL: {avl_critical} nodos críticos")
    
    # Aplicar penalizaciones a BST
    state.bst_tree.apply_depth_penalties(depth)
    bst_critical = sum(1 for node in state.bst_tree.bfs() if node.is_critical)
    print(f"   BST: {bst_critical} nodos críticos")
    
    print(f"✅ Profundidad crítica actualizada a {depth}")


def push_undo_snapshot() -> None:
    state.undo_stack.append(_snapshot())