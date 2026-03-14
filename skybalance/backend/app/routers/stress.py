from fastapi import APIRouter
from app.services import stress_service

router = APIRouter()

@router.post("/activate")
def activate():
    stress_service.activate_stress()
    return {"stress_mode": True}

@router.post("/rebalance")
def rebalance():
    stats = stress_service.deactivate_stress_and_rebalance()
    return {"stress_mode": False, "rebalance_stats": stats}

@router.get("/audit")
def audit():
    return stress_service.audit_avl()