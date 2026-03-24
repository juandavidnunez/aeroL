import json
from tkinter import filedialog
"a filedialog is used to select the file to save or load the data from"
from tkinter import Tk
" a TK is used to create a root window for the filedialog to work"
from typing import Optional, Dict, Any
"Optional is used to indicate that a variable can be of a certain type or None, Dict is used to indicate that a variable is a dictionary, and Any is used to indicate that a variable can be of any type"
from app.models.avl_tree import AVLTree
from app.models.bst_tree import BSTTree
from app.models.flight_node import FlightNode

class JSONHandler:

    def __init__(self, avl_tree: AVLTree, bst_tree: BSTTree):
        self.avl_tree = avl_tree
        self.bst_tree = bst_tree
        self.current_file: Optional[str] = None
    
    def select_file(self) -> Optional[str]:
        """Open a file dialog to select a JSON file."""
        root = Tk()
        root.withdraw()  # Hide the root window
        file_path = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json")]
        )
        root.destroy()  # Destroy the root window after selection   
        return file_path if file_path else None
    
    def load_from_file(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Load AVL and BST data from a JSON file."""
        if file_path is None:
            file_path = self.select_file()
            if file_path is None:
                return  {"success": False, "message": "No file selected"}  # No file selected
        try:
            with open(file_path, 'r', encoding = 'utf-8') as f:
                data = json.load(f) #Convert JSON data to a Python dictionary

            self.current_file = file_path
            return self._process_json(data)
        
        except Exception as e:
            return {"success": False, "message": f"Error loading file: {str(e)}"}
        
    def _process_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the loaded JSON data and populate AVL and BST trees.
        First the topology structure is loaded, then the AVL and BST trees are populated with the flight nodes.
        Secondly, the list of flight nodes is loaded and inserted into the AVL and BST trees."""

        if "root" in data or "raiz" in data:
            return self._load_topology(data)
        elif "flights" in data or "vuelos" in data or "lista" in data:
            return self._load_insertion_list(data)
        else: 
            return {"success": False, "message": "Invalid JSON structure: missing 'root' or 'flights' key"}
    
    def _load_topology(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Load the topology structure from the JSON data and populate AVL and BST trees."""
        try:
            self.avl_tree.root = None
            self.bst_tree.root = None

            root_data = data.get("root") or data.get("raiz")
            if root_data is None:
                return {"success": False, "message": "Invalid JSON structure: missing 'root' key"}

            self.avl_tree.root = self._build_avl_tree(root_data)
            self.bst_tree.root = self._build_bst_tree(root_data)
            return {"success": True, "message": "Topology loaded successfully"}

        except Exception as e:
            return {"success": False, "message": f"Error processing topology: {str(e)}"}

    def _build_avl_tree(self, data: Dict[str, Any]) -> Optional[FlightNode]:
        """Build tree node references from topology JSON for AVL."""
        return self._build_node_from_dict(data)

    def _build_bst_tree(self, data: Dict[str, Any]) -> Optional[FlightNode]:
        """Build tree node references from topology JSON for BST."""
        return self._build_node_from_dict(data)

    def _build_node_from_dict(self, data: Dict) -> Optional[FlightNode]:
        """Recursively build a FlightNode from a dictionary. This is used for both AVL and BST tree construction."""
        if not data:
            return None
        
        # Create the FlightNode from the dictionary data
        node = FlightNode(
            code=data["code"],
            origin=data.get("origin", ""),
            destination=data.get("destination", ""),
            base_price=data.get("base_price", 0.0),
            passengers=data.get("passengers", 0),
            promotion=data.get("promotion", 0.0),
            penalty=data.get("penalty", 0.0),
            is_critical=data.get("is_critical", False),
            priority=data.get("priority", 1),
            alerts=data.get("alerts", [])
        )
        
        # Set AVL-specifica fields if they exist in the data
        node.height = data.get("height", 1)
        node.balance_factor = data.get("balance_factor", 0)
        
        # Build children recursively
        if "left" in data and data["left"]:
            node.left = self._build_node_from_dict(data["left"])
            node.left.parent = node
        
        if "right" in data and data["right"]:
            node.right = self._build_node_from_dict(data["right"])
            node.right.parent = node
        
        return node

    def _load_insertion_list(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Load the list of flight nodes from the JSON data and insert the nodes in AVL and BST trees."""
        try:
            self.avl_tree.root = None
            self.bst_tree.root = None

            flights = data.get("flights") or data.get("vuelos") or data.get("lista")
            if not flights or not isinstance(flights, list):
                return {"success": False, "message": "Invalid JSON structure: missing or invalid 'flights' array"}

            for flight_data in flights:
                node = FlightNode.from_dict(flight_data)
                self.avl_tree.insert(node)
                self.bst_tree.insert(node)

            return {"success": True, "message": "Insertion list loaded successfully", "count": len(flights)}

        except Exception as e:
            return {"success": False, "message": f"Error processing insertion list: {str(e)}"}


    def _insert_bst(self, node: FlightNode) -> None:
        """Insert a node into the BST without balancing. This is used when building the BST from the AVL topology."""
        if self.bst_tree.root is None:
            self.bst_tree.root = node
            return

        current = self.bst_tree.root
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
        """Count the number of nodes in the BST. This is used for metadata when exporting to JSON."""
        if node is None:
            return 0
        return 1 + self._bst_node_count(node.left) + self._bst_node_count(node.right)
    
    def _build_bst_from_avl(self) -> None:
        """Build the BST tree from the AVL tree topology. This is used when loading a topology JSON to ensure both trees have the same structure."""
        self.bst_tree.root = None

        # Obtener todos los nodos del AVL en inorder
        nodes = self.avl_tree.inorder() if hasattr(self.avl_tree, 'inorder') else []
        
        # Insertar en BST sin balanceo
        for node in nodes:
            # Crear nuevo nodo (sin relaciones)
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
    
    def export_to_file(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Export the current AVL and BST tree data to a JSON file. If no file path is provided, a file dialog will be opened to select the save location."""
        if not file_path:
            file_path = self.select_file()
            if not file_path:
                return {"success": False, "message": "No se seleccionó archivo"}
        
        try:
            # Convertir árbol a diccionario
            tree_dict = self._node_to_dict(self.avl_tree.root)
            
            # Agregar metadata
            output = {
                "metadata": {
                    "node_count": self.avl_tree.node_count() if hasattr(self.avl_tree, 'node_count') else 0,
                    "height": self.avl_tree.height() if hasattr(self.avl_tree, 'height') else 0,
                    "rotations": self.avl_tree.rotations if hasattr(self.avl_tree, 'rotations') else {},
                    "export_date": str(__import__('datetime').datetime.now())
                },
                "root": tree_dict
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            return {"success": True, "message": f"Exportado a {file_path}"}
            
        except Exception as e:
            return {"success": False, "message": f"Error exportando: {str(e)}"}
    
    def _node_to_dict(self, node: Optional[FlightNode]) -> Optional[Dict]:
        """Convert a node and its subtree to a dictionary recursively"""
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
