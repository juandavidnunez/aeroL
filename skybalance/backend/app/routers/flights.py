from fastapi import APIRouter, HTTPException
from app.schemas.flight_schema import FlightCreate, FlightUpdate
from app.services import flight_service

router = APIRouter()

@router.post("/", status_code=201)
def create_flight(data: FlightCreate):
    node = flight_service.add_flight(data.model_dump())
    return {"code": node.code, "message": "Flight inserted"}

# IMPORTANTE: este endpoint debe ir ANTES de /{code}
# de lo contrario FastAPI interpreta "least-profitable" como un {code}
@router.delete("/least-profitable")
def eliminate_least_profitable():
    result = flight_service.eliminate_least_profitable()
    if result is None:
        raise HTTPException(status_code=404, detail="No hay vuelos en el árbol")
    return result

@router.get("/{code}")
def get_flight(code: str):
    node = flight_service.get_flight(code)
    if not node:
        raise HTTPException(status_code=404, detail="Flight not found")
    return node

@router.put("/{code}")
def update_flight(code: str, data: FlightUpdate):
    ok = flight_service.modify_flight(code, data.model_dump(exclude_none=True))
    if not ok:
        raise HTTPException(status_code=404, detail="Flight not found")
    return {"updated": True}

@router.delete("/{code}")
def delete_flight(code: str):
    ok = flight_service.remove_flight(code)
    if not ok:
        raise HTTPException(status_code=404, detail="Flight not found")
    return {"deleted": True}

@router.delete("/{code}/cancel")
def cancel_flight(code: str):
    removed = flight_service.cancel_flight(code)
    return {"cancelled": True, "nodes_removed": removed}