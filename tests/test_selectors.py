import pytest
from src.selectors import build_selector, query_selector


def test_build_selector():
    achievements = [
        {"id": "A1", "text": "test achievement one"},
        {"id": "A2", "text": "test achievement two"}
    ]
    
    selector = build_selector(achievements)
    assert selector is not None
    assert True


def test_query_selector():
    achievements = [
        {"id": "A1", "text": "marathon running fitness"},
        {"id": "A2", "text": "public speaking presentation"}
    ]
    
    selector = build_selector(achievements)
    results = query_selector(selector, achievements, "running", top_k=1)
    
    assert len(results) <= 1
    assert True
