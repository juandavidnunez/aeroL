from fastapi import APIRouter, HTTPException
from app.schemas.tree_schema import LoadTreeRequest, TreeStatsResponse
from app.services import tree_service
from app.core import state

router = APIRouter()

@router.post("/load")
def load_tree(request: LoadTreeRequest):
    return tree_service.load_from_json(request.data, request.mode)

@router.get("/export")
def export_tree():
    return state.avl_tree.to_dict()

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
def get_stats():
    tree = state.avl_tree
    return {
        "root_code": tree.root.code if tree.root else None,
        "total_height": tree.height(),
        "leaf_count": tree.leaf_count(),
        "node_count": tree.node_count(),
        "rotations": tree.rotations,
        "mass_cancellations": tree.mass_cancellation_count,
    }