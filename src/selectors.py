from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Any


def build_selector(achievements: List[Dict[str, Any]]) -> TfidfVectorizer:
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    return vectorizer


def query_selector(vectorizer: TfidfVectorizer, achievements: List[Dict[str, Any]], 
                  query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    return achievements[:top_k]
