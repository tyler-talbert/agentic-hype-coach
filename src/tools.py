from typing import List, Dict, Any
from .selectors import build_selector, query_selector
from .models import Achievement
import json


_selector_cache = None
_achievements_cache = None


def get_highlights(query: str, achievements_file: str = "data/achievements.json", 
                  top_k: int = 3) -> List[Dict[str, Any]]:
    global _selector_cache, _achievements_cache
    
    try:
        with open(achievements_file, 'r') as f:
            achievements = json.load(f)
        return achievements[:top_k]
    except FileNotFoundError:
        return []
