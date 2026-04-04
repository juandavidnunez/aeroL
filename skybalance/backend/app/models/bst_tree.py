"""
BSTTree: plain Binary Search Tree without balancing.
Used in parallel with AVLTree during insertion-mode loading.
"""
from __future__ import annotations
from collections import deque
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

    def search(self, code: str) -> Optional[FlightNode]:
        """Return the node with the given code or None."""
        current = self.root
        while current is not None:
            if code == current.code:
                return current
            current = current.left if code < current.code else current.right
        return None

    def delete(self, code: str) -> bool:
        """Delete a single node. Returns True if found and deleted."""
        self.root, deleted = self._delete(self.root, code)
        if self.root is not None:
            self.root.parent = None
        return deleted

    def cancel(self, code: str) -> int:
        """Remove a node and all its descendants. Returns the count removed."""
        self.root, removed = self._cancel_subtree(self.root, code)
        if self.root is not None:
            self.root.parent = None
        return removed

    def bfs(self) -> list:
        if self.root is None:
            return []

        result: list[FlightNode] = []
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            result.append(node)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        return result

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

    def apply_depth_penalties(self, critical_depth: int) -> None:
        """Mark deep nodes as critical and apply a penalty to their price."""

        def _walk(node: Optional[FlightNode], depth: int) -> None:
            if node is None:
                return

            if depth > critical_depth:
                node.is_critical = True
                node.penalty = round(node.base_price * 0.25, 2)
            else:
                node.is_critical = False
                node.penalty = 0.0

            _walk(node.left, depth + 1)
            _walk(node.right, depth + 1)

        _walk(self.root, 0)

    def _delete(self, node: Optional[FlightNode], code: str) -> tuple[Optional[FlightNode], bool]:
        """Delete a single node by code, maintaining BST property. Returns (new_root, was_deleted)."""
        if node is None:
            return None, False

        deleted = False
        if code < node.code:
            node.left, deleted = self._delete(node.left, code)
            if node.left is not None:
                node.left.parent = node
        elif code > node.code:
            node.right, deleted = self._delete(node.right, code)
            if node.right is not None:
                node.right.parent = node
        else:
            # Node found
            deleted = True
            # Case 1: No children
            if node.left is None:
                child = node.right
                if child is not None:
                    child.parent = node.parent
                return child, True
            # Case 2: No right child
            if node.right is None:
                child = node.left
                if child is not None:
                    child.parent = node.parent
                return child, True

            # Case 3: Two children - find successor
            successor = self._min_value_node(node.right)
            node.code = successor.code
            node.origin = successor.origin
            node.destination = successor.destination
            node.base_price = successor.base_price
            node.passengers = successor.passengers
            node.promotion = successor.promotion
            node.penalty = successor.penalty
            node.is_critical = successor.is_critical
            node.priority = successor.priority
            node.alerts = list(successor.alerts)
            node.right, _ = self._delete(node.right, successor.code)
            if node.right is not None:
                node.right.parent = node

        return node, deleted

    def _cancel_subtree(self, node: Optional[FlightNode], code: str) -> tuple[Optional[FlightNode], int]:
        """Remove a node and all its descendants. Returns (new_root, count_removed)."""
        if node is None:
            return None, 0

        removed = 0
        if code < node.code:
            node.left, removed = self._cancel_subtree(node.left, code)
            if node.left is not None:
                node.left.parent = node
        elif code > node.code:
            node.right, removed = self._cancel_subtree(node.right, code)
            if node.right is not None:
                node.right.parent = node
        else:
            # Found the node - remove it and all descendants
            return None, self._node_count(node)

        return node, removed

    def _min_value_node(self, node: Optional[FlightNode]) -> Optional[FlightNode]:
        """Find the node with minimum value (leftmost)."""
        current = node
        while current is not None and current.left is not None:
            current = current.left
        return current