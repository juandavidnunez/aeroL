from __future__ import annotations
from platform import node
from typing import Optional
from app.models.flight_node import FlightNode


class AVLTree:
    def __init__(self):
        self.root: Optional[FlightNode] = None  # Nodo raíz del árbol
        self.rotations: dict = {"LL": 0, "RR": 0, "LR": 0, "RL": 0}  
        # Contador de rotaciones realizadas

        self.mass_cancellation_count: int = 0  
        # Cantidad de cancelaciones masivas realizadas

        self.stress_mode: bool = False  
        # Si está activo, NO se balancea el árbol automáticamente


    # ── API Pública ──────────────────────────────────────────

    def insert(self, node: FlightNode) -> None:
        """Insert a FlightNode and rebalance (unless stress_mode)."""
        # TODO: implement recursive AVL insert + rotations
        if self.root is None:
            self.root = node
        else:
            self._insert_recursive(self.root, node)

    def _insert_recursive(self, current: FlightNode, new_node: FlightNode) -> None:
        if new_node.code < current.code:
            if current.left is None:
                current.left = new_node
            else:
                self._insert_recursive(current.left, new_node)
        else:
            if current.right is None:
                current.right = new_node
            else:
                self._insert_recursive(current.right, new_node)

    def delete(self, code: str) -> bool:
        """Delete a single node. Returns True if found and deleted."""
        # TODO: implement standard BST delete + AVL rebalance
        pass

    def cancel(self, code: str) -> int:
        """Remove node AND all its descendants. Returns count removed."""
        # TODO: implement subtree removal
        self.mass_cancellation_count += 1
        return 0


    def search(self, code: str) -> Optional[FlightNode]:
        """Return node with given code or None."""
        return self._search_recursive(self.root, code)

    def _search_recursive(self, node: Optional[FlightNode], code: str) -> Optional[FlightNode]:
        if node is None:
            return None
        if code == node.code:
            return node
        elif code < node.code:
            return self._search_recursive(node.left, code)
        else:
            return self._search_recursive(node.right, code)
        
    def update(self, code: str, **kwargs) -> bool:
        """
        Actualiza atributos de un nodo existente.
        """
        node = self.search(code)
        if node is None:
            return False

        for key, value in kwargs.items():
            if hasattr(node, key):
                setattr(node, key, value)

        return True


    # ── Recorridos ──────────────────────────────────────────

    def inorder(self) -> list:
        """Left -> Root -> Right"""
        result = []
        self._inorder_recursive(self.root, result)
        return result
    
    def _inorder_recursive(self, node: Optional[FlightNode], result: list) -> None:
        """Recursive helper for inorder traversal."""
        if node is None:
            return
        self._inorder_recursive(node.left, result)
        result.append(node)
        self._inorder_recursive(node.right, result)




    def bfs(self) -> list:
        """
        Recorrido por niveles (anchura)
        """
        result = []
        if self.root is None:
            return result
        queue = [self.root]
        while queue:
            node= queue.pop(0)
            result.append(node)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return result   
    
    def dfs_preorder(self) -> list:
        """
        Recorrido en preorden:
        Raíz → Izquierda → Derecha
        """
        result = []
        self._preorder_recursive(self.root, result)
        return result

    def _preorder_recursive(self, node: Optional[FlightNode], result: list) -> None:
        """Recursive helper for preorder traversal."""
        if node is None:
            return
        result.append(node)
        self._preorder_recursive(node.left, result)
        self._preorder_recursive(node.right, result)

    # ── Métricas ─────────────────────────────────────────────

    def height(self) -> int:
        """
        Altura total del árbol
        """
        return self._get_height(self.root)
        return 0


    def leaf_count(self) -> int:
        """
        Cuenta nodos hoja (sin hijos)
        """
        return self._count_leaves(self.root)
        return 0


    def _count_leaves(self, node: Optional[FlightNode]) -> int:
        if node is None:
            return 0
        if node.left is None and node.right is None:
            return 1
        return self._count_leaves(node.left) + self._count_leaves(node.right)
    
    def node_count(self) -> int:
        """
        Cuenta todos los nodos del árbol
        """
        return self._count_nodes(self.root)
    
    def _count_nodes(self, node: Optional[FlightNode]) -> int:
        if node is None:
            return 0
        return 1 + self._count_nodes(node.left) + self._count_nodes(node.right)
    

    # ── Auditoría AVL ───────────────────────────────────────────

    def verify_avl_property(self) -> dict:
        """
        Verifica que todos los nodos cumplen:
        balance_factor ∈ {-1,0,1}
        """
        # TODO
        return {"valid": True, "inconsistent_nodes": [], "total_nodes_checked": 0}


    # ── Rotaciones (LO MÁS IMPORTANTE) ─────────────────────────

    def _rotate_right(self, y: FlightNode) -> FlightNode:
        """
        Rotación derecha (caso LL)

              y                x
             /                / \
            x      →         A   y
           / \                  / \
          A   B                B   C
        """
        # TODO implementar
        self.rotations["LL"] += 1
        return y


    def _rotate_left(self, x: FlightNode) -> FlightNode:
        """
        Rotación izquierda (caso RR)
        """
        # TODO implementar
        self.rotations["RR"] += 1
        return x


    def _get_height(self, node: Optional[FlightNode]) -> int:
        return node.height if node else 0


    def _update_height(self, node: FlightNode) -> None:
        """
        Actualiza la altura del nodo según sus hijos
        """
        node.height = 1 + max(
            self._get_height(node.left),
            self._get_height(node.right)
        )


    def _get_balance(self, node: Optional[FlightNode]) -> int:
        """
        Calcula factor de balance:
        izquierda - derecha
        """
        if node is None:
            return 0

        bf = self._get_height(node.left) - self._get_height(node.right)
        node.balance_factor = bf
        return bf