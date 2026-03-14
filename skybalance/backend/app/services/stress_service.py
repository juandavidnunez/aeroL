from app.core import state


def activate_stress() -> None:
    state.stress_mode = True
    state.avl_tree.stress_mode = True


def deactivate_stress_and_rebalance() -> dict:
    state.stress_mode = False
    state.avl_tree.stress_mode = False
    return state.avl_tree.global_rebalance()


def audit_avl() -> dict:
    if not state.stress_mode:
        return {"error": "Audit only available in stress mode"}
    return state.avl_tree.verify_avl_property()