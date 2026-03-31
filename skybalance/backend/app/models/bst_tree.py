"""
BSTTree: plain Binary Search Tree without balancing.
Used in parallel with AVLTree during insertion-mode loading.
"""
from __future__ import annotations
from typing import Optional

from app.models.flight_node import FlightNode
from app.utils.serializer import node_to_dict


class BSTTree:
    def __init__(self):
        self.root: Optional[FlightNode] = None

    def insert(self, node: FlightNode) -> None:
        """Insert without any balancing."""
        node.left = None
        node.right = None
        node.parent = None
        node.height = 1
        node.balance_factor = 0
        self.root = self._insert(self.root, node)

    def to_dict(self) -> dict:
        return {"root": node_to_dict(self.root)}

    def height(self) -> int:
        return self._height(self.root)

    def leaf_count(self) -> int:
        return self._leaf_count(self.root)

    def node_count(self) -> int:
        return self._node_count(self.root)

    def _insert(self, current: Optional[FlightNode], node: FlightNode) -> FlightNode:
        if current is None:
            return node

        if node.code < current.code:
            current.left = self._insert(current.left, node)
            if current.left is not None:
                current.left.parent = current
        elif node.code > current.code:
            current.right = self._insert(current.right, node)
            if current.right is not None:
                current.right.parent = current
        else:
            current.origin = node.origin
            current.destination = node.destination
            current.base_price = node.base_price
            current.passengers = node.passengers
            current.promotion = node.promotion
            current.penalty = node.penalty
            current.is_critical = node.is_critical
            current.priority = node.priority
            current.alerts = list(node.alerts)
            return current

        current.height = 1 + max(self._height(current.left), self._height(current.right))
        current.balance_factor = self._height(current.left) - self._height(current.right)
        return current

    def _height(self, node: Optional[FlightNode]) -> int:
        if node is None:
            return 0
        return 1 + max(self._height(node.left), self._height(node.right))

    def _leaf_count(self, node: Optional[FlightNode]) -> int:
        if node is None:
            return 0
        if node.left is None and node.right is None:
            return 1
        return self._leaf_count(node.left) + self._leaf_count(node.right)

    def _node_count(self, node: Optional[FlightNode]) -> int:
        if node is None:
            return 0
        return 1 + self._node_count(node.left) + self._node_count(node.right)