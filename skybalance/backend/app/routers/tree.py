from fastapi import APIRouter, HTTPException, Query

from app.core import state
from app.schemas.tree_schema import LoadTreeRequest, TreeStatsResponse
from app.services import tree_service

router = APIRouter()


@router.post("/load")
def load_tree(request: LoadTreeRequest):
    try:
        return tree_service.load_from_json(request.data, request.mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/export")
def export_tree(tree_type: str = Query("avl", pattern="^(avl|bst)$")):
    tree = state.avl_tree if tree_type == "avl" else state.bst_tree
    return tree.to_dict()


@router.post("/undo")
def undo():
    ok = tree_service.undo_last_action()
    if not ok:
        raise HTTPException(status_code=400, detail="Nothing to undo")
    return {"undone": True}


@router.put("/critical-depth/{depth}")
def set_critical_depth(depth: int):
    tree_service.set_critical_depth(depth)
    return {"critical_depth": depth}


@router.get("/stats", response_model=TreeStatsResponse)
def get_stats(tree_type: str = Query("avl", pattern="^(avl|bst)$")):
    tree = state.avl_tree if tree_type == "avl" else state.bst_tree
    rotations = getattr(tree, "rotations", {"LL": 0, "RR": 0, "LR": 0, "RL": 0})
    mass_cancellations = getattr(tree, "mass_cancellation_count", 0)
    node_count = tree.node_count() if hasattr(tree, "node_count") else 0

    return {
        "root_code": tree.root.code if tree.root else None,
        "total_height": tree.height(),
        "leaf_count": tree.leaf_count(),
        "node_count": node_count,
        "rotations": rotations,
        "mass_cancellations": mass_cancellations,
    }