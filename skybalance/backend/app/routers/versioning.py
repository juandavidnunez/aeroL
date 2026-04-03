from fastapi import APIRouter, HTTPException
from app.schemas.version_schema import SaveVersionRequest, VersionListResponse
from app.services import tree_service
from app.core import state

router = APIRouter()

@router.get("/", response_model=VersionListResponse)
def list_versions():
    return {"versions": list(state.named_versions.keys())}

@router.post("/save")
def save_version(request: SaveVersionRequest):
    tree_service.save_named_version(request.name)
    return {"saved": request.name}

@router.post("/restore/{name}")
def restore_version(name: str):
    ok = tree_service.restore_named_version(name)
    if not ok:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"restored": name}

@router.delete("/{name}")
def delete_version(name: str):
    ok = tree_service.delete_named_version(name)
    if not ok:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"deleted": name}