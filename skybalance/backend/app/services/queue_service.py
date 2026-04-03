from app.core import state
from app.services.flight_service import add_flight


def enqueue(flight_data: dict) -> int:
    state.insertion_queue.append(flight_data)
    return len(state.insertion_queue)


def process_queue_step() -> dict:
    """Process a single item from the queue and return detailed information"""
    if not state.insertion_queue:
        return {"status": "empty", "message": "No items in queue"}

    flight_data = state.insertion_queue.pop(0)

    # Get tree state before insertion
    before_height = state.avl_tree.height()
    before_rotations = {
        "LL": state.avl_tree.rotations.get("LL", 0),
        "RR": state.avl_tree.rotations.get("RR", 0),
        "LR": state.avl_tree.rotations.get("LR", 0),
        "RL": state.avl_tree.rotations.get("RL", 0)
    }

    try:
        node = add_flight(flight_data)

        # Get tree state after insertion
        after_height = state.avl_tree.height()
        after_rotations = {
            "LL": state.avl_tree.rotations.get("LL", 0),
            "RR": state.avl_tree.rotations.get("RR", 0),
            "LR": state.avl_tree.rotations.get("LR", 0),
            "RL": state.avl_tree.rotations.get("RL", 0)
        }

        # Check for critical balance issues
        balance_conflicts = []
        if after_height > state.critical_depth:
            balance_conflicts.append(f"Height exceeded critical depth ({state.critical_depth})")

        # Check for excessive rotations
        rotation_increase = {
            k: after_rotations[k] - before_rotations[k]
            for k in before_rotations.keys()
        }

        total_rotations = sum(rotation_increase.values())
        if total_rotations > 2:  # More than 2 rotations might indicate imbalance
            balance_conflicts.append(f"High rotation count ({total_rotations} rotations)")

        return {
            "status": "inserted",
            "flight": {
                "code": node.code,
                "origin": node.origin,
                "destination": node.destination,
                "final_price": node.final_price
            },
            "tree_changes": {
                "height_before": before_height,
                "height_after": after_height,
                "rotations_before": before_rotations,
                "rotations_after": after_rotations,
                "rotations_increase": rotation_increase
            },
            "balance_conflicts": balance_conflicts,
            "remaining_queue": len(state.insertion_queue)
        }

    except Exception as e:
        return {
            "status": "error",
            "flight": {"code": flight_data.get("code")},
            "error": str(e),
            "remaining_queue": len(state.insertion_queue)
        }


def process_queue() -> list:
    """Process entire queue at once (legacy method)"""
    log = []
    while state.insertion_queue:
        flight_data = state.insertion_queue.pop(0)
        try:
            node = add_flight(flight_data)
            log.append({"code": node.code, "status": "inserted"})
        except Exception as e:
            log.append({"code": flight_data.get("code"), "status": "error", "detail": str(e)})
    return log


def get_queue() -> list:
    return list(state.insertion_queue)


def clear_queue() -> None:
    state.insertion_queue.clear()