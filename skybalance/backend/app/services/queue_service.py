from app.core import state
from app.services.flight_service import add_flight


def enqueue(flight_data: dict) -> int:
    state.insertion_queue.append(flight_data)
    return len(state.insertion_queue)


def process_queue() -> list:
    log = []
    while state.insertion_queue:
        flight_data = state.insertion_queue.pop(0)
        try:
            node = add_flight(flight_data)
            log.append({"code": node.code, "status": "inserted"})
        except Exception as e:
            log.append({"code": flight_data.get("code"), "status": "error", "detail": str(e)})
    return log


def get_queue() -> list:
    return list(state.insertion_queue)


def clear_queue() -> None:
    state.insertion_queue.clear()