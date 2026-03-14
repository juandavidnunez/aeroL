from pydantic import BaseModel
from app.schemas.flight_schema import FlightCreate

class EnqueueRequest(BaseModel):
    flight: FlightCreate

class QueueStatusResponse(BaseModel):
    pending: int
    items: list