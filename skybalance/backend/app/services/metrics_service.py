from app.core import state


def get_metrics() -> dict:
    tree = state.avl_tree
    return {
        "root_code": tree.root.code if tree.root else None,
        "height": tree.height(),
        "leaf_count": tree.leaf_count(),
        "node_count": tree.node_count(),
        "rotations": dict(tree.rotations),
        "mass_cancellations": tree.mass_cancellation_count,
        "bfs_order": [n.code for n in tree.bfs()],
        "dfs_preorder": [n.code for n in tree.dfs_preorder()],
        "inorder": [n.code for n in tree.inorder()],
        "stress_mode": state.stress_mode,
        "critical_depth": state.critical_depth,
    }