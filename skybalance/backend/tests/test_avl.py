import pytest
from app.models.avl_tree import AVLTree
from app.models.flight_node import FlightNode


def make_flight(code: str, price: float = 100.0) -> FlightNode:
    return FlightNode(code=code, origin="BOG", destination="MED", base_price=price, passengers=100)

def test_insert_single():
    tree = AVLTree()
    tree.insert(make_flight("SKY001"))
    assert tree.root is not None
    assert tree.root.code == "SKY001"

def test_search_existing():
    tree = AVLTree()
    tree.insert(make_flight("SKY001"))
    assert tree.search("SKY001") is not None

def test_search_missing():
    tree = AVLTree()
    assert tree.search("MISSING") is None

def test_delete():
    tree = AVLTree()
    tree.insert(make_flight("SKY001"))
    tree.delete("SKY001")
    assert tree.search("SKY001") is None

def test_avl_balance_after_inserts():
    tree = AVLTree()
    for i in range(1, 8):
        tree.insert(make_flight(f"SKY{i:03}"))
    report = tree.verify_avl_property()
    assert report["valid"] is True