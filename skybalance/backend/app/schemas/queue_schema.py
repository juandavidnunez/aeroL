from pydantic import BaseModel
from app.schemas.flight_schema import FlightCreate
from typing import List, Dict, Any, Optional

class EnqueueRequest(BaseModel):
    flight: FlightCreate

class QueueStatusResponse(BaseModel):
    pending: int
    items: list

class ProcessStepResponse(BaseModel):
    status: str
    flight: Optional[Dict[str, Any]] = None
    tree_changes: Optional[Dict[str, Any]] = None
    balance_conflicts: Optional[List[str]] = None
    remaining_queue: int
    error: Optional[str] = None
    message: Optional[str] = None