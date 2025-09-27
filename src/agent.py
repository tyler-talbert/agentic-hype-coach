import os
import json
import requests
from typing import List, Dict, Any
from .models import CoachRequest, CoachResponse
from .tools import get_highlights
from .prompts import SYSTEM_PROMPT, PLANNING_INSTRUCTION, FINAL_INSTRUCTION, GENERAL_RESPONSE_INSTRUCTION


class Agent:
    def __init__(self):
        self.llm_plan_mode = os.getenv("LLM_PLAN_MODE", "stub")
        self.llm_final_mode = os.getenv("LLM_FINAL_MODE", "stub")
        
    def _detect_stage(self, messages: List[Dict[str, str]]) -> str:
        """Detect if this is planning or final stage based on messages."""
        for msg in reversed(messages):
            if msg["role"] == "system" and msg["content"] == FINAL_INSTRUCTION:
                return "final"
        return "plan"
    
    def _extract_scenario(self, messages: List[Dict[str, str]]) -> str:
        for msg in reversed(messages):
            if msg["role"] == "user":
                for line in msg["content"].split('\n'):
                    if line.lower().startswith('scenario:'):
                        return line.split(':', 1)[1].strip()
        return ""
        
    def llm_call(self, messages: List[Dict[str, str]]) -> str:
        stage = self._detect_stage(messages)
        
        if stage == "plan" and self.llm_plan_mode == "stub":
            scenario = self._extract_scenario(messages)
            return f'{{"action":"get_highlights","args":{{"query":"{scenario}","k":3}}}}'
        
        elif stage == "final" and self.llm_final_mode == "stub":
            scenario = self._extract_scenario(messages)
            return f"""Quick boost for you: Based on your achievements [A1], [A2], you've already proven resilience and skill. That same grit applies here with your scenario: {scenario}.

Remember... you've done harder things before! Step in with confidence.

USED_IDS: [A1, A2]"""
        
        # Ollama integration (for non-stub mode or stub final without LLM_STUB_FINAL=1)
        try:
            prompt = self._build_prompt(messages)
            response = requests.post(
                f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/generate",
                json={
                    "model": os.getenv('OLLAMA_MODEL', 'llama3.1:8b'),
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get('response', 'No response from model')
            else:
                return f"Ollama error: {response.status_code}"
        except Exception as e:
            return f"LLM error: {str(e)}"
    
    def _build_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Flatten structured messages into a readable prompt for Ollama."""
        #  messages = [
        #   {"role": "system", "content": "You are Hype Coach"}]
        parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"].strip()

            if role == "system":
                parts.append(f"[SYSTEM]\n{content}")
            elif role == "user":
                parts.append(f"[USER]\n{content}")
            elif role == "tool":
                parts.append(f"[TOOL RESULTS]\n{content}")
            else:
                parts.append(f"[{role.upper()}]\n{content}")

        return "\n\n".join(parts)
        
    def run(self, request: CoachRequest) -> CoachResponse:
        # Step 1: Build initial messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Scenario: {request.scenario}\nEnergy level: {request.energy}"},
            {"role": "system", "content": PLANNING_INSTRUCTION}
        ]
        
        # Step 2: Get planning response
        planning_response = self.llm_call(messages)
        tool_called = False
        highlights = []
        similarity_scores = []
        
        # Step 3: Check if planning response is JSON
        try:
            plan = json.loads(planning_response.strip())
            action = plan.get("action", "")
            # The LLM has been consistently making a random typo with highights instead of highlights <-- Strange!! 
            if action in ["get_highlights", "get_highights", "get_highlight"]:
                tool_called = True
                # Get highlights with scores
                highlights_with_scores = get_highlights(request.scenario, k=3)
                highlights = [ach for ach, score in highlights_with_scores]
                similarity_scores = [score for ach, score in highlights_with_scores]
                
                # Step 4: Append tool message
                tool_summary = []
                for ach in highlights:
                    tool_summary.append(f"[{ach.id}] {ach.title} — {ach.text[:50]}...")
                
                messages.append({
                    "role": "tool", 
                    "content": "Retrieved achievements:\n" + "\n".join(tool_summary)
                })
                
                # Step 5: Append final instruction and get final response
                messages.append({"role": "system", "content": FINAL_INSTRUCTION})
                final_response = self.llm_call(messages)
            elif action == "proceed":
                # No tool needed, generate general response
                # Remove the planning instruction and replace with general instruction
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Scenario: {request.scenario}\nEnergy level: {request.energy}"},
                    {"role": "system", "content": GENERAL_RESPONSE_INSTRUCTION}
                ]
                final_response = self.llm_call(messages)
            else:
                final_response = planning_response
        except (json.JSONDecodeError, KeyError):
            # Non-JSON planning = final output
            final_response = planning_response
        
        # Step 6: Parse final output
        # LLM should return plain text based on FINAL_INSTRUCTION
        
        lines = final_response.strip().split('\n')
        used_ids = []
        speech_lines = []
        
        for line in lines:
            if line.startswith('USED_IDS:'):
                # Parse USED_IDS: [A1, A2] format
                try:
                    ids_part = line.split('USED_IDS:')[1].strip()
                    if ids_part.startswith('[') and ids_part.endswith(']'):
                        ids_str = ids_part[1:-1]  # Remove brackets
                        used_ids = [id.strip() for id in ids_str.split(',') if id.strip()]
                except Exception as e:
                    pass
            else:
                speech_lines.append(line)
        
        speech = '\n'.join(speech_lines).strip()
        
        # Step 7: Calculate confidence based on tool usage and similarity scores
        if not tool_called:
            # No tool called - general conversation, no confidence needed
            confidence = None
        elif similarity_scores and used_ids:
            # Tool called and achievements used - base confidence on similarity scores
            avg_similarity = sum(similarity_scores) / len(similarity_scores)
            # Convert similarity to confidence (scores are 0-1)
            confidence = min(0.95, max(0.3, avg_similarity))
        elif tool_called and not used_ids:
            # Tool called but no achievements referenced - low confidence
            confidence = 0.3
        else:
            # Fallback
            confidence = 0.5
        
        return CoachResponse(
            speech=speech,
            used_ids=used_ids,
            confidence=confidence
        )
