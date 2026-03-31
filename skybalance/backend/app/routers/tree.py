from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from app.schemas.tree_schema import LoadTreeRequest, TreeStatsResponse
from app.services import tree_service
from app.core import state
from app.persistence.json_handler import JSONHandler

router = APIRouter()


def _json_handler() -> JSONHandler:
    return JSONHandler(state.avl_tree, state.bst_tree)

@router.post("/load")
def load_tree(request: LoadTreeRequest):
    try:
        return tree_service.load_from_json(request.data, request.mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/load-json")
async def load_json_from_file(file: UploadFile = File(...)):
    """
    Receive the JSON file from the frontend (Angular)
    """
    print("🔵 Recibiendo archivo...")
    print("🔵 Nombre:", file.filename)
    print("🔵 Tipo:", file.content_type)
    

    # Leer el contenido del archivo
    content = await file.read()
    json_str = content.decode('utf-8')
    
    # Process with JSONHandler to load the tree
    result = _json_handler().process_json_content(json_str)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return result

@router.get("/export")
def export_tree(tree_type: str = Query("avl", pattern="^(avl|bst)$")):
    tree = state.avl_tree if tree_type == "avl" else state.bst_tree
    return tree.to_dict()


@router.get("/export-json")
def export_tree_json():
    """
    Export the current tree to JSON format for download from the frontend
    """
    result = _json_handler().export_to_json()
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("message"))
    
    return result

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