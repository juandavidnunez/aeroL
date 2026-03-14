from fastapi import APIRouter
from app.services import metrics_service

router = APIRouter()

@router.get("/")
def get_metrics():
    return metrics_service.get_metrics()