"""
BSTTree: plain Binary Search Tree without balancing.
Used in parallel with AVLTree during insertion-mode loading.
"""
from __future__ import annotations
from typing import Optional
from app.models.flight_node import FlightNode


class BSTTree:
    def __init__(self):
        self.root: Optional[FlightNode] = None

    def insert(self, node: FlightNode) -> None:
        """Insert without any balancing."""
        # TODO: implement
        pass

    def to_dict(self) -> dict:
        # TODO: implement
        return {}

    def height(self) -> int:
        # TODO: implement
        return 0

    def leaf_count(self) -> int:
        # TODO: implement
        return 0