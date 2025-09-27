from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class TextIndex:
    def __init__(self, achievements: List[Dict[str, Any]]):
        self.ids = [a["id"] for a in achievements]
        docs = [self._flatten(a) for a in achievements]
        # training on achievement txt
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
        self.matrix = self.vectorizer.fit_transform(docs)

    def _flatten(self, a: Dict[str, Any]) -> str:
        title = a.get("title", "")
        tags = " ".join(a.get("tags", []))
        text = a.get("text", "")
        metrics = " ".join(f"{k} {v}" for k, v in a.get("metrics", {}).items())
        return f"{title} {tags} {text} {metrics}".lower()

    def query(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        user_query_vector = self.vectorizer.transform([query.lower()]) # Turn user query to TF-IDF vector
        sims = cosine_similarity(user_query_vector, self.matrix).flatten() #1-D array of ach vec (vector determine how close each ach is to userQueryVector)
        k = min(k, len(self.ids))
        top = np.argsort(sims)[::-1][:k]
        return [(self.ids[i], float(sims[i])) for i in top] # [("A2", 0.91), ("A3", 0.34)]


def build_selector(achievements: List[Dict[str, Any]]) -> object:
    """Uses methods above to extract achievements and vectorize them"""
    return TextIndex(achievements)


def query_selector(selector: object, query: str, k: int) -> List[Tuple[str, float]]:
    """Returns the k most similar vectors based on the build_selector method"""
    return selector.query(query, k)
