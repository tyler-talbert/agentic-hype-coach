import os
import json
from typing import List, Dict, Any
from .models import CoachRequest, CoachResponse
from .tools import get_highlights
from .prompts import SYSTEM_PROMPT, PLANNING_INSTRUCTION, FINAL_INSTRUCTION


class Agent:
    def __init__(self):
        self.llm_mode = os.getenv("LLM_MODE", "stub")
        
    def run(self, request: CoachRequest) -> CoachResponse:
        return CoachResponse(
            speech="This is a placeholder pep talk. You've got this!",
            used_ids=[],
            confidence=0.5
        )
    
    def llm_call(self, messages: List[Dict[str, str]]) -> str:
        if self.llm_mode == "stub":
            return "This is a stub LLM response for testing."
        return "LLM integration not yet implemented."
