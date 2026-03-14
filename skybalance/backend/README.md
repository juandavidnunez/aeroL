# SkyBalance AVL - Backend

## Inicio rapido
  cd backend
  python -m venv venv
  venv\Scripts\activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload

## TODOs pendientes
  models/avl_tree.py    -> insert, delete, cancel, search, inorder, bfs,
                           dfs_preorder, height, leaf_count, node_count,
                           verify_avl_property, global_rebalance,
                           apply_depth_penalties, find_least_profitable,
                           to_dict, from_topology, _rotate_right, _rotate_left
  models/bst_tree.py    -> insert, to_dict, height, leaf_count
  services/tree_service.py -> load_from_json