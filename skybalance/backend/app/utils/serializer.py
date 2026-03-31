from typing import Any, Optional

from app.models.flight_node import FlightNode


def node_to_dict(node: Optional[FlightNode]) -> Optional[dict]:
    if node is None:
        return None
    return {
        "code": node.code,
        "origin": node.origin,
        "destination": node.destination,
        "base_price": node.base_price,
        "final_price": node.final_price,
        "passengers": node.passengers,
        "promotion": node.promotion,
        "penalty": node.penalty,
        "is_critical": node.is_critical,
        "priority": node.priority,
        "alerts": node.alerts,
        "height": node.height,
        "balance_factor": node.balance_factor,
        "left": node_to_dict(node.left),
        "right": node_to_dict(node.right),
    }


def _pick(data: dict, *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return default


def _to_float(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_flight_data(data: dict) -> dict:
    code_value = _pick(data, "code", "codigo", "id", default="")
    base_price = _to_float(_pick(data, "base_price", "precioBase", "precio_base", default=0.0), 0.0)
    promotion_value = _pick(data, "promotion", "promocion", "descuento", default=0.0)
    penalty_value = _pick(data, "penalty", "penalizacion", "multa", default=0.0)

    promotion = 0.0 if isinstance(promotion_value, bool) else _to_float(promotion_value, 0.0)
    penalty = 0.0 if isinstance(penalty_value, bool) else _to_float(penalty_value, 0.0)

    final_price = _pick(data, "final_price", "precioFinal")
    if final_price is not None and promotion == 0.0 and penalty == 0.0:
        difference = _to_float(final_price, base_price) - base_price
        if difference > 0:
            penalty = round(difference, 2)
        elif difference < 0:
            promotion = round(-difference, 2)

    alert_flag = bool(_pick(data, "is_critical", "alerta", default=False))
    raw_alerts = _pick(data, "alerts", "alertas", default=[])
    if isinstance(raw_alerts, list):
        alerts = list(raw_alerts)
    elif raw_alerts:
        alerts = [str(raw_alerts)]
    else:
        alerts = []

    if alert_flag and "alerta" not in alerts:
        alerts.append("alerta")

    return {
        "code": str(code_value),
        "origin": str(_pick(data, "origin", "origen", default="")),
        "destination": str(_pick(data, "destination", "destino", default="")),
        "base_price": base_price,
        "passengers": _to_int(_pick(data, "passengers", "pasajeros", default=0), 0),
        "promotion": promotion,
        "penalty": penalty,
        "is_critical": alert_flag,
        "priority": _to_int(_pick(data, "priority", "prioridad", default=1), 1),
        "alerts": alerts,
        "height": max(_to_int(_pick(data, "height", "altura", default=1), 1), 1),
        "balance_factor": _to_int(_pick(data, "balance_factor", "factorEquilibrio", "factor_equilibrio", default=0), 0),
    }


def dict_to_node(data: dict) -> FlightNode:
    normalized = normalize_flight_data(data)
    return FlightNode(**normalized)