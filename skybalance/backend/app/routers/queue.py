from fastapi import APIRouter
from app.schemas.queue_schema import EnqueueRequest, QueueStatusResponse
from app.services import queue_service

router = APIRouter()

@router.get("/", response_model=QueueStatusResponse)
def get_queue():
    items = queue_service.get_queue()
    return {"pending": len(items), "items": items}

@router.post("/enqueue")
def enqueue(request: EnqueueRequest):
    length = queue_service.enqueue(request.flight.model_dump())
    return {"queued": True, "queue_length": length}

@router.post("/process")
def process():
    log = queue_service.process_queue()
    return {"processed": len(log), "log": log}

@router.delete("/clear")
def clear():
    queue_service.clear_queue()
    return {"cleared": True}