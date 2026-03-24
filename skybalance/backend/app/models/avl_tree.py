"""
AVLTree: core AVL self-balancing binary search tree.
Key = FlightNode.code (lexicographic comparison).
All method bodies contain TODO stubs - implement the logic here.
"""
from __future__ import annotations
from typing import Optional
from app.models.flight_node import FlightNode


class AVLTree:
    def __init__(self):
        self.root: Optional[FlightNode] = None
        self.rotations: dict = {"LL": 0, "RR": 0, "LR": 0, "RL": 0}
        self.mass_cancellation_count: int = 0
        self.stress_mode: bool = False

    # ── Public API ──────────────────────────────────────────

    def insert(self, node: FlightNode) -> None:
        """Insert a FlightNode and rebalance (unless stress_mode)."""
        if self.root is None:
            node.left = node.right = node.parent = None
            self.root = node
            self._update_height(node)
            return

        self.root = self._insert_recursive(self.root, node)
        self.root.parent = None

    def _insert_recursive(self, root: FlightNode, node: FlightNode) -> FlightNode:
        if root is None:
            node.left = node.right = node.parent = None
            return node

        if node.code < root.code:
            root.left = self._insert_recursive(root.left, node)
            root.left.parent = root
        elif node.code > root.code:
            root.right = self._insert_recursive(root.right, node)
            root.right.parent = root
        else:
            return root

        self._update_height(root)
        balance = self._get_balance(root)

        if balance > 1 and node.code < root.left.code:
            return self._rotate_right(root)

        if balance < -1 and node.code > root.right.code:
            return self._rotate_left(root)

        if balance > 1 and node.code > root.left.code:
            root.left = self._rotate_left(root.left)
            root.left.parent = root
            return self._rotate_right(root)

        if balance < -1 and node.code < root.right.code:
            root.right = self._rotate_right(root.right)
            root.right.parent = root
            return self._rotate_left(root)

        return root

    def delete(self, code: str) -> bool:
        """Delete a single node. Returns True if found and deleted."""
        self.root, deleted = self._delete_recursive(self.root, code)
        if self.root:
            self.root.parent = None
        return deleted

    def _min_value_node(self, node: FlightNode) -> FlightNode:
        current = node
        while current.left is not None:
            current = current.left
        return current

    def _delete_recursive(self, root: Optional[FlightNode], code: str) -> tuple[Optional[FlightNode], bool]:
        if root is None:
            return None, False

        deleted = False
        if code < root.code:
            root.left, deleted = self._delete_recursive(root.left, code)
            if root.left:
                root.left.parent = root
        elif code > root.code:
            root.right, deleted = self._delete_recursive(root.right, code)
            if root.right:
                root.right.parent = root
        else:
            deleted = True
            if root.left is None:
                temp = root.right
                return temp, True
            elif root.right is None:
                temp = root.left
                return temp, True
            else:
                temp = self._min_value_node(root.right)
                root.code = temp.code
                root.origin = temp.origin
                root.destination = temp.destination
                root.base_price = temp.base_price
                root.passengers = temp.passengers
                root.promotion = temp.promotion
                root.penalty = temp.penalty
                root.is_critical = temp.is_critical
                root.priority = temp.priority
                root.alerts = temp.alerts[:]
                root.right, _ = self._delete_recursive(root.right, temp.code)

        if root is None:
            return None, deleted

        self._update_height(root)
        balance = self._get_balance(root)

        if balance > 1 and self._get_balance(root.left) >= 0:
            return self._rotate_right(root), deleted

        if balance > 1 and self._get_balance(root.left) < 0:
            root.left = self._rotate_left(root.left)
            if root.left:
                root.left.parent = root
            return self._rotate_right(root), deleted

        if balance < -1 and self._get_balance(root.right) <= 0:
            return self._rotate_left(root), deleted

        if balance < -1 and self._get_balance(root.right) > 0:
            root.right = self._rotate_right(root.right)
            if root.right:
                root.right.parent = root
            return self._rotate_left(root), deleted

        return root, deleted

    def cancel(self, code: str) -> int:
        """Remove node AND all its descendants. Returns count removed."""
        node = self.search(code)
        if node is None:
            return 0
        to_remove = self._count_subtree(node)
        self.delete(code)
        self.mass_cancellation_count += to_remove
        return to_remove

    def _count_subtree(self, node: Optional[FlightNode]) -> int:
        if node is None:
            return 0
        return 1 + self._count_subtree(node.left) + self._count_subtree(node.right)

    def search(self, code: str) -> Optional[FlightNode]:
        """Return node with given code or None."""
        return self._search_recursive(self.root, code)

    def _search_recursive(self, root: Optional[FlightNode], code: str) -> Optional[FlightNode]:
        if root is None:
            return None
        if code == root.code:
            return root
        if code < root.code:
            return self._search_recursive(root.left, code)
        return self._search_recursive(root.right, code)

    def update(self, code: str, **kwargs) -> bool:
        """Update fields of an existing node. Returns True if found."""
        node = self.search(code)
        if node is None:
            return False
        for key, value in kwargs.items():
            if hasattr(node, key):
                setattr(node, key, value)
        return True

    # ── Traversals ──────────────────────────────────────────

    def inorder(self) -> list:
        """Left -> Root -> Right  returns list of nodes in sorted order by code??."""
        result = []
        self.inorder_recursive(self.root, result)
        return result
    
    def inorder_recursive(self, node: Optional[FlightNode], result: list) -> None:
        """Recursive helper for inorder traversal."""
        if node is None:
            return
        self.inorder_recursive(node.left, result)
        result.append(node)
        self.inorder_recursive(node.right, result)



    def bfs(self) -> list:
        """Update fields of an existing node. Returns True if found."""
        node = self.search(code)
        if node is None:
            return False
        for key, value in kwargs.items():
            if hasattr(node, key):
                setattr(node, key, value)
        return True

    # ── Traversals ──────────────────────────────────────────

    def inorder(self) -> list:
        """Left -> Root -> Right  returns list of nodes in sorted order by code??."""
        result = []
        self._inorder_recursive(self.root, result)
        return result
    
    def inorder_recursive(self, node: Optional[FlightNode], result: list) -> None:
        """Recursive helper for inorder traversal."""
        if node is not None:
            return
        self.inorder_recursive(node.left, result)
        result.append(node)
        self.inorder_recursive(node.right, result)



    def bfs(self) -> list:
        """Breadth-First Search"""
        result = []
        # TODO: implement
        return result

    def dfs_preorder(self) -> list:
        """Root -> Left -> Right"""
        result = []
        # TODO: implement
        return result

    # ── Metrics ─────────────────────────────────────────────

    def height(self) -> int:
        # TODO: implement
        return 0

    def leaf_count(self) -> int:
        # TODO: implement
        return 0

    def node_count(self) -> int:
        # TODO: implement
        return 0

    # ── AVL Audit ───────────────────────────────────────────

    def verify_avl_property(self) -> dict:
        """
        Check every node: balance_factor in {-1,0,1} and height correct.
        Returns report dict with list of inconsistent nodes.
        """
        # TODO: implement
        return {"valid": True, "inconsistent_nodes": [], "total_nodes_checked": 0}

    # ── Stress / Global Rebalance ────────────────────────────

    def global_rebalance(self) -> dict:
        """Re-run AVL rotations on every unbalanced node after stress mode."""
        # TODO: implement
        return {"rotations_applied": 0, "nodes_fixed": 0}

    # ── Depth Penalty ────────────────────────────────────────

    def apply_depth_penalties(self, critical_depth: int) -> None:
        """
        For each node at depth > critical_depth:
          - set is_critical = True
          - set penalty = base_price * 0.25
        Otherwise clear flag and penalty.
        """
        # TODO: implement
        pass

    # ── Economic Elimination ─────────────────────────────────

    def find_least_profitable(self) -> Optional[FlightNode]:
        """
        Return node with lowest profitability.
        Tiebreaker: deepest node; if still tied, largest code.
        """
        # TODO: implement
        return None

    # ── Serialization ────────────────────────────────────────

    def to_dict(self) -> dict:
        """Serialize full tree to nested dict for JSON export."""
        # TODO: implement using utils/serializer.py -> node_to_dict
        return {}

    def from_topology(self, data: dict) -> None:
        """Reconstruct tree respecting parent->child topology from dict."""
        # TODO: implement
        pass

    def from_insertion_list(self, flights: list) -> None:
        """Insert flights one by one triggering AVL balancing."""
        for f in flights:
            node = FlightNode(**f)
            self.insert(node)

    # ── Internal Rotation Helpers ────────────────────────────

    def _rotate_right(self, y: FlightNode) -> FlightNode:
        """LL single rotation. Returns new subtree root."""
        # TODO: implement
        self.rotations["LL"] += 1
        return y

    def _rotate_left(self, x: FlightNode) -> FlightNode:
        """RR single rotation. Returns new subtree root."""
        # TODO: implement
        self.rotations["RR"] += 1
        return x

    def _get_height(self, node: Optional[FlightNode]) -> int:
        return node.height if node else 0

    def _update_height(self, node: FlightNode) -> None:
        node.height = 1 + max(
            self._get_height(node.left),
            self._get_height(node.right)
        )

    def _get_balance(self, node: Optional[FlightNode]) -> int:
        if node is None:
            return 0
        bf = self._get_height(node.left) - self._get_height(node.right)
        node.balance_factor = bf
        return bf