from app.models.flight_node import FlightNode
from typing import Optional


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


def dict_to_node(data: dict) -> FlightNode:
    return FlightNode(
        code=data["code"],
        origin=data["origin"],
        destination=data["destination"],
        base_price=data["base_price"],
        passengers=data["passengers"],
        promotion=data.get("promotion", 0.0),
        penalty=data.get("penalty", 0.0),
        is_critical=data.get("is_critical", False),
        priority=data.get("priority", 1),
        alerts=data.get("alerts", []),
        height=data.get("height", 1),
        balance_factor=data.get("balance_factor", 0),
    )