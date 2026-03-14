from pydantic import BaseModel
from typing import Optional

class LoadTreeRequest(BaseModel):
    mode: str
    data: dict

class TreeStatsResponse(BaseModel):
    root_code: Optional[str]
    total_height: int
    leaf_count: int
    node_count: int
    rotations: dict
    mass_cancellations: int

class AVLAuditReport(BaseModel):
    valid: bool
    inconsistent_nodes: list
    total_nodes_checked: int