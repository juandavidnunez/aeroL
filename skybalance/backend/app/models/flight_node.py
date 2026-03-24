"""
FlightNode: single flight / AVL tree node with all business fields.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FlightNode:
    # Identity
    code: str
    origin: str
    destination: str

    # Economics
    base_price: float
    passengers: int
    promotion: float = 0.0
    penalty: float = 0.0

    # Status
    is_critical: bool = False
    priority: int = 1
    alerts: list = field(default_factory=list)

    # AVL structural
    height: int = 1
    balance_factor: int = 0

    # Tree links
    left: Optional["FlightNode"] = field(default=None, repr=False)
    right: Optional["FlightNode"] = field(default=None, repr=False)
    parent: Optional["FlightNode"] = field(default=None, repr=False)

    @property
    def final_price(self) -> float:
        return max(self.base_price + self.penalty - self.promotion, 0.0)

    @property
    def profitability(self) -> float:
        return self.passengers * self.final_price - self.promotion + self.penalty