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
        if self.root is None:
            node.left = node.right = node.parent = None
            self.root = node
            return

        current = self.root
        while True:
            if node.code < current.code:
                if current.left is None:
                    current.left = node
                    node.parent = current
                    break
                current = current.left
            elif node.code > current.code:
                if current.right is None:
                    current.right = node
                    node.parent = current
                    break
                current = current.right
            else:
                break

    def to_dict(self) -> dict:
        # TODO: implement
        return {}

    def height(self) -> int:
        # TODO: implement
        return 0

    def leaf_count(self) -> int:
        # TODO: implement
        return 0