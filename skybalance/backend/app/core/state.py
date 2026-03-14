"""
Global in-memory state: AVL tree, undo stack, versions, queue.
"""
from app.models.avl_tree import AVLTree

avl_tree: AVLTree = AVLTree()
undo_stack: list = []
named_versions: dict = {}
insertion_queue: list = []
stress_mode: bool = False
critical_depth: int = 5
stats: dict = {
    "rotations_ll": 0,
    "rotations_rr": 0,
    "rotations_lr": 0,
    "rotations_rl": 0,
    "mass_cancellations": 0,
}