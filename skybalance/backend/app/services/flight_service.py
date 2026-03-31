from datetime import date
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
    # state.stats["mass_cancellations"] += 1  # Comenta si no existe state.stats
    return removed


def modify_flight(code: str, updates: dict) -> bool:
    print(f"🔵 MODIFY: código original={code}, updates={updates}")
    
    # Buscar el nodo existente
    node = state.avl_tree.search(code)
    if not node:
        print(f"❌ Nodo {code} no encontrado")
        return False
    
    print(f"✅ Nodo encontrado: {node.code}")
    
    # Si el código cambió
    if "code" in updates and str(updates["code"]) != str(code):
        new_code = str(updates["code"])
        print(f"🔄 Cambiando código: {code} → {new_code}")
        
        # Crear nuevo nodo
        new_node = FlightNode(
            code=new_code,
            origin=updates.get("origin", node.origin),
            destination=updates.get("destination", node.destination),
            base_price=float(updates.get("base_price", node.base_price)),
            passengers=int(updates.get("passengers", node.passengers)),
            promotion=float(updates.get("promotion", node.promotion)),
            priority=int(updates.get("priority", node.priority)),
        )
        
        # Eliminar original e insertar nuevo
        state.avl_tree.delete(code)
        state.avl_tree.insert(new_node)
        print(f"✅ Cambio completado")
        return True
    
    else:
        print(f"✏️ Solo actualizando campos")
        for key, value in updates.items():
            if hasattr(node, key) and key != "code":
                setattr(node, key, value)
        return True


def get_flight(code: str) -> Optional[FlightNode]:
    return state.avl_tree.search(code)


def eliminate_least_profitable() -> Optional[str]:
    node = state.avl_tree.find_least_profitable()
    if node is None:
        return None
    cancel_flight(node.code)
    return node.code