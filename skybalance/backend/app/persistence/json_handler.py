# app/persistence/json_handler.py
import json
from platform import node
from typing import Dict, Any, Optional, List
from app.models.avl_tree import AVLTree
from app.models.bst_tree import BSTTree
from app.models.flight_node import FlightNode


class JSONHandler:
    def __init__(self, avl_tree: AVLTree, bst_tree: BSTTree):
        self.avl = avl_tree
        self.bst = bst_tree
    


    def process_json_content(self, content: str) -> Dict[str, Any]:
        try:
            data = json.loads(content)
            print("✅ JSON parseado correctamente")
            print("📄 Claves del JSON:", list(data.keys()))
            return self._process_json(data)
        except json.JSONDecodeError as e:
            print(f"❌ Error JSON: {e}")
            return {"success": False, "message": f"Error parsing JSON: {str(e)}"}
        except Exception as e:
            print(f"❌ Error general: {type(e).__name__} - {e}")  # ← Esto mostrará el error real
            import traceback
            traceback.print_exc()  # ← Imprime toda la pila del error
            return {"success": False, "message": f"Error: {str(e)}"}
        

    
    def _process_json(self, data: Dict) -> Dict[str, Any]:
        # Si tiene "codigo" (español), es un nodo suelto
        if "codigo" in data:
            return self._load_topology({"root": data})
        
        # Si tiene "root" o "raiz"
        if "root" in data or "raiz" in data:
            return self._load_topology(data)
        
        # Si tiene "vuelos" o "flights"
        if "vuelos" in data or "flights" in data or "lista" in data:
            return self._load_insertion_list(data)
        
        # Si tiene "code" (inglés)
        if "code" in data:
            return self._load_topology({"root": data})
        
        return {"success": False, "message": f"Formato no reconocido. Claves: {list(data.keys())}"}
                
    # ── FORMATO TOPOLOGÍA ──────────────────────────────────────
    
    def _load_topology(self, data: Dict) -> Dict[str, Any]:
        try:
            self.avl.root = None
            self.bst.root = None
            
            # Si el JSON tiene "root" o "raiz", úsalo; si no, asume que el objeto es la raíz
            if "root" in data:
                root_data = data["root"]
            elif "raiz" in data:
                root_data = data["raiz"]
            else:
                root_data = data  # ← El JSON completo es la raíz
            
            self.avl.root = self._build_node_from_dict(root_data)
            
            # Construir BST a partir del AVL para comparación
            self._build_bst_from_avl()
            
            # Calcular métricas
            avl_height = self.avl.height() if hasattr(self.avl, 'height') else 0
            avl_leaves = self.avl.leaf_count() if hasattr(self.avl, 'leaf_count') else 0
            
            return {
                "success": True,
                "message": "Árbol cargado exitosamente desde topología",
                "format": "topology",
                "avl": {
                    "node_count": self.avl.node_count(),
                    "height": avl_height,
                    "leaf_count": avl_leaves
                },
                "bst": {
                    "node_count": self._bst_node_count(self.bst.root),
                    "height": self._bst_height(self.bst.root),
                    "leaf_count": self._bst_leaf_count(self.bst.root)
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error cargando topología: {str(e)}"}
    

    def _build_node_from_dict(self, data: Dict) -> Optional[FlightNode]:
        if not data:
            return None
        
        # Acepta nombres en español E inglés
        node = FlightNode(
            code=str(data.get("codigo", data.get("code", ""))),  # ← español e inglés
            origin=data.get("origen", data.get("origin", "")),
            destination=data.get("destino", data.get("destination", "")),
            base_price=float(data.get("precioBase", data.get("base_price", 0))),
            passengers=int(data.get("pasajeros", data.get("passengers", 0))),
            promotion=float(data.get("promocion", data.get("promotion", 0))),
            penalty=float(data.get("penalizacion", data.get("penalty", 0))),
            is_critical=bool(data.get("es_critico", data.get("is_critical", False))),
            priority=int(data.get("prioridad", data.get("priority", 1))),
            alerts=data.get("alertas", data.get("alerts", []))
        )
        
        node.height = int(data.get("altura", data.get("height", 1)))
        node.balance_factor = int(data.get("factorEquilibrio", data.get("balance_factor", 0)))
        
        # Acepta izquierdo/derecho en español
        left_data = data.get("izquierdo", data.get("left"))
        if left_data:
            node.left = self._build_node_from_dict(left_data)
            if node.left:
                node.left.parent = node
        
        right_data = data.get("derecho", data.get("right"))
        if right_data:
            node.right = self._build_node_from_dict(right_data)
            if node.right:
                node.right.parent = node
        
        return node

    
    def _load_insertion_list(self, data: Dict) -> Dict[str, Any]:
        """Loads flights one by one (with automatic balancing in AVL)"""
        try:
            # Limpiar árboles
            self.avl.root = None
            self.bst.root = None
            
            # Obtener lista de vuelos
            flights = data.get("flights", data.get("vuelos", data.get("lista", [])))
            
            if not flights:
                return {"success": False, "message": "Lista de vuelos vacía"}
            
            avl_count = 0
            bst_count = 0
            errors = []
            
            for flight_data in flights:
                try:
                    # Crear nodo
                    node = FlightNode(
                        code=flight_data.get("code", ""),
                        origin=flight_data.get("origin", ""),
                        destination=flight_data.get("destination", ""),
                        base_price=flight_data.get("base_price", flight_data.get("precio_base", 0.0)),
                        passengers=flight_data.get("passengers", flight_data.get("pasajeros", 0)),
                        promotion=flight_data.get("promotion", flight_data.get("promocion", 0.0)),
                        priority=flight_data.get("priority", flight_data.get("prioridad", 1))
                    )
                    
                    # Insert en AVL (con balanceo)
                    self.avl.insert(node)
                    avl_count += 1
                    
                    # Insertar en BST (sin balanceo) para comparación
                    self._insert_bst(node)
                    bst_count += 1
                    
                except Exception as e:
                    errors.append(f"Error en vuelo {flight_data.get('code', 'desconocido')}: {str(e)}")
            
            # Calcular métricas
            avl_height = self.avl.height() if hasattr(self.avl, 'height') else 0
            avl_leaves = self.avl.leaf_count() if hasattr(self.avl, 'leaf_count') else 0
            
            return {
                "success": True,
                "message": f"Insertados {avl_count} vuelos en AVL y {bst_count} en BST",
                "format": "insertion_list",
                "avl": {
                    "node_count": self.avl.node_count(),
                    "height": avl_height,
                    "leaf_count": avl_leaves
                },
                "bst": {
                    "node_count": self._bst_node_count(self.bst.root),
                    "height": self._bst_height(self.bst.root),
                    "leaf_count": self._bst_leaf_count(self.bst.root)
                },
                "errors": errors if errors else None
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error insertando lista: {str(e)}"}
    
    
    def _insert_bst(self, node: FlightNode) -> None:
        """Inserta en BST sin balanceo"""
        if self.bst.root is None:
            self.bst.root = node
            return
        
        current = self.bst.root
        while True:
            if node.code < current.code:
                if current.left is None:
                    current.left = node
                    node.parent = current
                    break
                current = current.left
            else:
                if current.right is None:
                    current.right = node
                    node.parent = current
                    break
                current = current.right
    
    def _bst_node_count(self, node: Optional[FlightNode]) -> int:
        """Cuenta nodos en BST"""
        if node is None:
            return 0
        return 1 + self._bst_node_count(node.left) + self._bst_node_count(node.right)
    
    def _bst_height(self, node: Optional[FlightNode]) -> int:
        """Calcula altura del BST"""
        if node is None:
            return 0
        return 1 + max(self._bst_height(node.left), self._bst_height(node.right))
    
    def _bst_leaf_count(self, node: Optional[FlightNode]) -> int:
        """Cuenta hojas en BST"""
        if node is None:
            return 0
        if node.left is None and node.right is None:
            return 1
        return self._bst_leaf_count(node.left) + self._bst_leaf_count(node.right)
    
    def _build_bst_from_avl(self) -> None:
        """Construye BST a partir del AVL (para comparación en modo topología)"""
        # Obtener todos los nodos del AVL en inorder
        nodes = self.avl.inorder() if hasattr(self.avl, 'inorder') else []
        
        # Insertar en BST sin balanceo
        for node in nodes:
            new_node = FlightNode(
                code=node.code,
                origin=node.origin,
                destination=node.destination,
                base_price=node.base_price,
                passengers=node.passengers,
                promotion=node.promotion,
                penalty=node.penalty,
                is_critical=node.is_critical,
                priority=node.priority,
                alerts=node.alerts.copy()
            )
            self._insert_bst(new_node)
    

    def export_to_json(self) -> Dict[str, Any]:
        """Exporta árbol actual a diccionario (para enviar al frontend)"""
        try:
            # Convertir árbol a diccionario
            tree_dict = self._node_to_dict(self.avl.root)
            
            # Calcular métricas
            avl_height = self.avl.height() if hasattr(self.avl, 'height') else 0
            avl_leaves = self.avl.leaf_count() if hasattr(self.avl, 'leaf_count') else 0
            
            return {
                "success": True,
                "metadata": {
                    "node_count": self.avl.node_count(),
                    "height": avl_height,
                    "leaf_count": avl_leaves,
                    "rotations": self.avl.rotations,
                    "mass_cancellations": self.avl.mass_cancellation_count,
                    "export_date": str(__import__('datetime').datetime.now())
                },
                "root": tree_dict
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error exportando árbol: {str(e)}"}
    
    def _node_to_dict(self, node: Optional[FlightNode]) -> Optional[Dict]:
        """Convierte nodo y subárbol a diccionario recursivamente"""
        if node is None:
            return None
        
        return {
            "code": node.code,
            "origin": node.origin,
            "destination": node.destination,
            "base_price": node.base_price,
            "passengers": node.passengers,
            "promotion": node.promotion,
            "penalty": node.penalty,
            "is_critical": node.is_critical,
            "priority": node.priority,
            "alerts": node.alerts,
            "height": node.height,
            "balance_factor": node.balance_factor,
            "left": self._node_to_dict(node.left),
            "right": self._node_to_dict(node.right)
        }