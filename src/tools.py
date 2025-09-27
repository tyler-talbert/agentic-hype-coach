from typing import List, Dict, Any, Optional
from .selectors import build_selector, query_selector
from .models import Achievement
import json


_module_cache = None


def load_achievements(path: str = "data/achievements.json") -> List[Achievement]:
    """Parse JSON into Achievement objects."""
    try:
        with open(path, 'r') as data_file:
            data = json.load(data_file)
        return [Achievement(**item) for item in data]
    except FileNotFoundError:
        raise FileNotFoundError(f"Achievement file not found: {path}")


def build_cache() -> Dict[str, Any]:
    """Build once: achievements_by_id dict and selector."""
    achievements_list = load_achievements()
    achievements_data = [ach.model_dump() for ach in achievements_list]
    
    achievements_by_id = {ach.id: ach for ach in achievements_list}
    selector = build_selector(achievements_data)
    
    return {
        "achievements_by_id": achievements_by_id,
        "selector": selector
    }


def get_highlights(query: str, k: int = 3, cache: Optional[Dict[str, Any]] = None) -> List[Achievement]:
    """Use query_selector to get ids, map to Achievement, return up to k."""
    global _module_cache
    
    if cache is None:
        if _module_cache is None:
            _module_cache = build_cache()
        cache = _module_cache
    
    selector = cache["selector"]
    achievements_by_id = cache["achievements_by_id"]
    
    # Get (id, score) tuples from selector
    results = query_selector(selector, query, k)
    
    # Map ids to Achievement objects
    highlights = []
    for achievement_id, score in results:
        if achievement_id in achievements_by_id:
            highlights.append(achievements_by_id[achievement_id])
    
    return highlights[:k]
