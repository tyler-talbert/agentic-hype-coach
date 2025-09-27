from pydantic import BaseModel
from typing import List


class Achievement(BaseModel):
    id: str
    title: str
    tags: List[str]
    text: str
    metrics: dict


class CoachRequest(BaseModel):
    scenario: str
    energy: int = 2


class CoachResponse(BaseModel):
    speech: str
    used_ids: List[str]
    confidence: float
