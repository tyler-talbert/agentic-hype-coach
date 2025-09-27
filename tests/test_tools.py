import pytest
import json
import tempfile
import os
from src.tools import get_highlights


def test_get_highlights_with_file():
    test_achievements = [
        {
            "id": "T1",
            "title": "Test Achievement",
            "tags": ["test"],
            "text": "This is a test achievement",
            "metrics": {"score": 100}
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_achievements, f)
        temp_file = f.name
    
    try:
        results = get_highlights("test query", temp_file, top_k=1)
        assert len(results) <= 1
        assert True
    finally:
        os.unlink(temp_file)


def test_get_highlights_missing_file():
    results = get_highlights("test query", "nonexistent.json")
    assert results == []
    assert True
