import pytest
import json
import tempfile
import os
from src.tools import get_highlights, load_achievements, build_cache
from src.models import Achievement


def test_get_highlights_returns_achievements():
    """Ensure get_highlights returns at most k items, each an Achievement."""
    results = get_highlights("running", k=2)
    
    assert len(results) <= 2
    for result in results:
        assert isinstance(result, Achievement)


def test_get_highlights_respects_k_limit():
    """Test that get_highlights respects the k parameter."""
    results = get_highlights("test", k=1)
    assert len(results) <= 1


def test_load_achievements_missing_file():
    """Ensure load_achievements raises FileNotFoundError with clear message if path missing."""
    with pytest.raises(FileNotFoundError) as exc_info:
        load_achievements("nonexistent.json")
    
    assert "Achievement file not found: nonexistent.json" in str(exc_info.value)


def test_load_achievements_valid_file():
    """Test load_achievements with valid file."""
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
        results = load_achievements(temp_file)
        assert len(results) == 1
        assert isinstance(results[0], Achievement)
        assert results[0].id == "T1"
    finally:
        os.unlink(temp_file)


def test_build_cache():
    """Test that build_cache returns proper structure."""
    cache = build_cache()
    
    assert "achievements_by_id" in cache
    assert "selector" in cache
    assert isinstance(cache["achievements_by_id"], dict)
