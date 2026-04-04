from datetime import date
from app.core import state
from app.models.flight_node import FlightNode
from app.services.tree_service import push_undo_snapshot
from typing import Optional


def add_flight(data: dict) -> FlightNode:
    push_undo_snapshot()
    node = FlightNode(**data)

    state.avl_tree.insert(node)
    # Solo insertar en BST si tiene contenido (modo inserción)
    if state.bst_tree.root is not None:
        state.bst_tree.insert(node)
    state.avl_tree.apply_depth_penalties(state.critical_depth)
    if state.bst_tree.root is not None:
        state.bst_tree.apply_depth_penalties(state.critical_depth)  # Aplicar penalizaciones a ambos
    return node


def remove_flight(code: str) -> bool:
    push_undo_snapshot()
    # AVL es obligatorio (siempre está cargado)
    avl_result = state.avl_tree.delete(code)
    # BST es opcional (vacío en modo topología)
    if state.bst_tree.root is not None:
        state.bst_tree.delete(code)
    # Reaplicar penalizaciones después de eliminar
    state.avl_tree.apply_depth_penalties(state.critical_depth)
    if state.bst_tree.root is not None:
        state.bst_tree.apply_depth_penalties(state.critical_depth)
    return avl_result


def cancel_flight(code: str) -> int:
    push_undo_snapshot()
    # AVL es obligatorio (siempre está cargado)
    avl_removed = state.avl_tree.cancel(code)
    # BST es opcional (vacío en modo topología)
    if state.bst_tree.root is not None:
        state.bst_tree.cancel(code)
    # Reaplicar penalizaciones después de cancelar
    state.avl_tree.apply_depth_penalties(state.critical_depth)
    if state.bst_tree.root is not None:
        state.bst_tree.apply_depth_penalties(state.critical_depth)
    return avl_removed  # Retornar el número de eliminaciones del AVL


def modify_flight(code: str, updates: dict) -> bool:
    print(f"🔵 MODIFY: código original={code}, updates={updates}")
    
    # Buscar el nodo existente en AVL (siempre se carga)
    avl_node = state.avl_tree.search(code)
    if not avl_node:
        print(f"❌ Nodo {code} no encontrado en AVL")
        return False
    
    # BST puede estar vacío en modo topología, así que es opcional
    bst_node = state.bst_tree.search(code)
    
    print(f"✅ Nodo encontrado: {avl_node.code}")
    
    # Si el código cambió
    if "code" in updates and str(updates["code"]) != str(code):
        new_code = str(updates["code"])
        print(f"🔄 Cambiando código: {code} → {new_code}")
        
        # Crear nuevo nodo
        new_node = FlightNode(
            code=new_code,
            origin=updates.get("origin", avl_node.origin),
            destination=updates.get("destination", avl_node.destination),
            base_price=float(updates.get("base_price", avl_node.base_price)),
            passengers=int(updates.get("passengers", avl_node.passengers)),
            promotion=float(updates.get("promotion", avl_node.promotion)),
            priority=int(updates.get("priority", avl_node.priority)),
        )
        
        # Eliminar original e insertar nuevo en AVL (siempre)
        state.avl_tree.delete(code)
        state.avl_tree.insert(new_node)
        
        # Si BST existe (modo inserción) también actualizar allí
        if bst_node:
            state.bst_tree.delete(code)
            state.bst_tree.insert(new_node)
        
        # Reaplicar penalizaciones
        state.avl_tree.apply_depth_penalties(state.critical_depth)
        if bst_node:  # Solo si BST tiene contenido
            state.bst_tree.apply_depth_penalties(state.critical_depth)
        
        print(f"✅ Cambio completado")
        return True
    
    else:
        print(f"✏️ Solo actualizando campos")
        for key, value in updates.items():
            if hasattr(avl_node, key) and key != "code":
                setattr(avl_node, key, value)
        
        # Si BST existe, también actualizar allí
        if bst_node:
            for key, value in updates.items():
                if hasattr(bst_node, key) and key != "code":
                    setattr(bst_node, key, value)
        
        return True


def get_flight(code: str) -> Optional[FlightNode]:
    return state.avl_tree.search(code)


def eliminate_least_profitable() -> Optional[str]:
    node = state.avl_tree.find_least_profitable()
    if node is None:
        return None
    cancel_flight(node.code)
    return node.code