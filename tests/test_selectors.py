import pytest
from src.selectors import build_selector, query_selector


def test_build_selector():
    achievements = [
        {"id": "A1", "text": "test achievement one"},
        {"id": "A2", "text": "test achievement two"}
    ]
    
    selector = build_selector(achievements)
    assert selector is not None


def test_query_selector():
    achievements = [
        {"id": "A1", "text": "marathon running fitness"},
        {"id": "A2", "text": "public speaking presentation"}
    ]
    
    selector = build_selector(achievements)
    results = query_selector(selector, "running", k=1)
    
    assert len(results) <= 1 
    assert isinstance(results[0], tuple) # each res should be tuple
    assert len(results[0]) == 2 # ex [("A1", 0.91)]


def test_selector_known_tag_rank_one():
    """Build selector over 3 items; query containing known tag returns its id at rank 1."""
    achievements = [
        {"id": "A1", "title": "Marathon", "tags": ["running", "fitness"], "text": "Completed marathon", "metrics": {"time": "4:15"}},
        {"id": "A2", "title": "Speech", "tags": ["speaking", "confidence"], "text": "Gave keynote", "metrics": {"audience": 200}},
        {"id": "A3", "title": "Career", "tags": ["learning", "growth"], "text": "Changed careers", "metrics": {"salary": 40}}
    ]
    
    selector = build_selector(achievements)
    results = query_selector(selector, "running", k=3)
    
    assert len(results) >= 1
    assert results[0][0] == "A1"  # First result should be A1 (contains "running" tag)
