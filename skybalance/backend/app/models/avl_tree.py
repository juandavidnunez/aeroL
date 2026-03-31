"""
AVLTree: core AVL self-balancing binary search tree.
Key = FlightNode.code (lexicographic comparison).
"""
from __future__ import annotations

from collections import deque
from typing import Optional

from app.models.flight_node import FlightNode
from app.utils.serializer import dict_to_node, node_to_dict


class AVLTree:
    def __init__(self):
        self.root: Optional[FlightNode] = None
        self.rotations: dict = {"LL": 0, "RR": 0, "LR": 0, "RL": 0}
        self.mass_cancellation_count: int = 0
        self.stress_mode: bool = False

    # ── API pública ─────────────────────────────────────────

    def insert(self, node: FlightNode) -> None:
        """Insert a flight node and rebalance unless stress mode is active."""
        node.left = None
        node.right = None
        node.parent = None
        node.height = 1
        node.balance_factor = 0
        self.root = self._insert(self.root, node)

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
        if removed > 0:
            self.mass_cancellation_count += 1
        return removed

    def search(self, code: str) -> Optional[FlightNode]:
        """Return the node with the given code or None."""
        current = self.root
        while current is not None:
            if code == current.code:
                return current
            current = current.left if code < current.code else current.right
        return None

    def update(self, code: str, **kwargs) -> bool:
        """Update fields of an existing node."""
        node = self.search(code)
        if node is None:
            return False

        for key, value in kwargs.items():
            if hasattr(node, key):
                setattr(node, key, value)
        return True

    # ── Traversals ──────────────────────────────────────────

    def inorder(self) -> list:
        result: list[FlightNode] = []
        self._inorder_recursive(self.root, result)
        return result

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

    def dfs_preorder(self) -> list:
        result: list[FlightNode] = []
        self._preorder_recursive(self.root, result)
        return result

    # ── Metrics ─────────────────────────────────────────────

    def height(self) -> int:
        return self._get_height(self.root)

    def leaf_count(self) -> int:
        return self._leaf_count(self.root)

    def node_count(self) -> int:
        return self._count_nodes(self.root)

    # ── AVL validation ──────────────────────────────────────

    def verify_avl_property(self) -> dict:
        """Check that heights and balance factors are consistent across the tree."""
        inconsistent_nodes = []
        total_nodes_checked = 0

        def _audit(node: Optional[FlightNode]) -> int:
            nonlocal total_nodes_checked
            if node is None:
                return 0

            total_nodes_checked += 1
            left_height = _audit(node.left)
            right_height = _audit(node.right)
            expected_height = 1 + max(left_height, right_height)
            expected_balance = left_height - right_height

            if (
                node.height != expected_height
                or node.balance_factor != expected_balance
                or abs(expected_balance) > 1
            ):
                inconsistent_nodes.append(
                    {
                        "code": node.code,
                        "stored_height": node.height,
                        "expected_height": expected_height,
                        "stored_balance": node.balance_factor,
                        "expected_balance": expected_balance,
                    }
                )

            return expected_height

        _audit(self.root)
        return {
            "valid": len(inconsistent_nodes) == 0,
            "inconsistent_nodes": inconsistent_nodes,
            "total_nodes_checked": total_nodes_checked,
        }

    # ── Extra business operations ───────────────────────────

    def global_rebalance(self) -> dict:
        """Rebuild the tree from its current nodes to restore AVL balance."""
        nodes = [self._clone_node_data(node) for node in self.inorder()]
        before_rotations = sum(self.rotations.values())

        self.root = None
        self.stress_mode = False
        for node in nodes:
            self.insert(node)

        after_rotations = sum(self.rotations.values())
        return {
            "rotations_applied": after_rotations - before_rotations,
            "nodes_fixed": len(nodes),
        }

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

    def find_least_profitable(self) -> Optional[FlightNode]:
        """Return the least profitable node, preferring deeper nodes on ties."""
        best: Optional[FlightNode] = None
        best_depth = -1

        def _walk(node: Optional[FlightNode], depth: int) -> None:
            nonlocal best, best_depth
            if node is None:
                return

            if (
                best is None
                or node.profitability < best.profitability
                or (
                    node.profitability == best.profitability
                    and (depth > best_depth or (depth == best_depth and node.code > best.code))
                )
            ):
                best = node
                best_depth = depth

            _walk(node.left, depth + 1)
            _walk(node.right, depth + 1)

        _walk(self.root, 0)
        return best

    # ── Serialization ───────────────────────────────────────

    def to_dict(self) -> dict:
        return {"root": node_to_dict(self.root)}

    def from_topology(self, data: Optional[dict]) -> None:
        if data is None:
            self.root = None
            return

        payload = data
        if isinstance(data, dict):
            payload = data.get("tree") or data.get("root") or data.get("arbol") or data.get("raiz") or data

        self.root = self._build_from_dict(payload)
        if self.root is not None:
            self.root.parent = None

    def from_insertion_list(self, flights: list) -> None:
        self.root = None
        for flight in flights:
            node = flight if isinstance(flight, FlightNode) else dict_to_node(flight)
            self.insert(node)

    # ── Internal helpers ────────────────────────────────────

    def _inorder_recursive(self, node: Optional[FlightNode], result: list) -> None:
        if node is None:
            return
        self._inorder_recursive(node.left, result)
        result.append(node)
        self._inorder_recursive(node.right, result)

    def _preorder_recursive(self, node: Optional[FlightNode], result: list) -> None:
        if node is None:
            return
        result.append(node)
        self._preorder_recursive(node.left, result)
        self._preorder_recursive(node.right, result)

    def _rotate_right(self, y: FlightNode) -> FlightNode:
        x = y.left
        if x is None:
            return y

        t2 = x.right
        x.right = y
        y.left = t2

        x.parent = y.parent
        y.parent = x
        if t2 is not None:
            t2.parent = y

        self._update_height(y)
        self._get_balance(y)
        self._update_height(x)
        self._get_balance(x)

        self.rotations["LL"] += 1
        return x

    def _rotate_left(self, x: FlightNode) -> FlightNode:
        y = x.right
        if y is None:
            return x

        t2 = y.left
        y.left = x
        x.right = t2

        y.parent = x.parent
        x.parent = y
        if t2 is not None:
            t2.parent = x

        self._update_height(x)
        self._get_balance(x)
        self._update_height(y)
        self._get_balance(y)

        self.rotations["RR"] += 1
        return y

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
            self._copy_payload(current, node)
            return current

        self._update_height(current)
        self._get_balance(current)
        if self.stress_mode:
            return current
        return self._rebalance(current)

    def _delete(self, node: Optional[FlightNode], code: str) -> tuple[Optional[FlightNode], bool]:
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
            deleted = True
            if node.left is None:
                child = node.right
                if child is not None:
                    child.parent = node.parent
                return child, True
            if node.right is None:
                child = node.left
                if child is not None:
                    child.parent = node.parent
                return child, True

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

        self._update_height(node)
        self._get_balance(node)
        if self.stress_mode:
            return node, deleted
        return self._rebalance(node), deleted

    def _cancel_subtree(self, node: Optional[FlightNode], code: str) -> tuple[Optional[FlightNode], int]:
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
            return None, self._count_nodes(node)

        if removed > 0:
            self._update_height(node)
            self._get_balance(node)
            if not self.stress_mode:
                node = self._rebalance(node)
        return node, removed

    def _rebalance(self, node: FlightNode) -> FlightNode:
        balance = self._get_balance(node)

        if balance > 1:
            left_balance = self._get_balance(node.left)
            if left_balance < 0 and node.left is not None:
                self.rotations["LR"] += 1
                node.left = self._rotate_left(node.left)
                if node.left is not None:
                    node.left.parent = node
            return self._rotate_right(node)

        if balance < -1:
            right_balance = self._get_balance(node.right)
            if right_balance > 0 and node.right is not None:
                self.rotations["RL"] += 1
                node.right = self._rotate_right(node.right)
                if node.right is not None:
                    node.right.parent = node
            return self._rotate_left(node)

        return node

    def _build_from_dict(self, data: Optional[dict]) -> Optional[FlightNode]:
        if data is None:
            return None

        node = dict_to_node(data)
        left_data = data.get("left") if "left" in data else data.get("izquierdo")
        right_data = data.get("right") if "right" in data else data.get("derecho")

        node.left = self._build_from_dict(left_data)
        node.right = self._build_from_dict(right_data)
        if node.left is not None:
            node.left.parent = node
        if node.right is not None:
            node.right.parent = node

        self._update_height(node)
        self._get_balance(node)
        return node

    def _copy_payload(self, target: FlightNode, source: FlightNode) -> None:
        target.code = source.code
        target.origin = source.origin
        target.destination = source.destination
        target.base_price = source.base_price
        target.passengers = source.passengers
        target.promotion = source.promotion
        target.penalty = source.penalty
        target.is_critical = source.is_critical
        target.priority = source.priority
        target.alerts = list(source.alerts)

    def _clone_node_data(self, node: FlightNode) -> FlightNode:
        return FlightNode(
            code=node.code,
            origin=node.origin,
            destination=node.destination,
            base_price=node.base_price,
            passengers=node.passengers,
            promotion=node.promotion,
            penalty=node.penalty,
            is_critical=node.is_critical,
            priority=node.priority,
            alerts=list(node.alerts),
        )

    def _min_value_node(self, node: FlightNode) -> FlightNode:
        current = node
        while current.left is not None:
            current = current.left
        return current

    def _leaf_count(self, node: Optional[FlightNode]) -> int:
        if node is None:
            return 0
        if node.left is None and node.right is None:
            return 1
        return self._leaf_count(node.left) + self._leaf_count(node.right)

    def _count_nodes(self, node: Optional[FlightNode]) -> int:
        if node is None:
            return 0
        return 1 + self._count_nodes(node.left) + self._count_nodes(node.right)

    def _get_height(self, node: Optional[FlightNode]) -> int:
        return node.height if node else 0

    def _update_height(self, node: FlightNode) -> None:
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

    def _get_balance(self, node: Optional[FlightNode]) -> int:
        if node is None:
            return 0

        bf = self._get_height(node.left) - self._get_height(node.right)
        node.balance_factor = bf
        return bf