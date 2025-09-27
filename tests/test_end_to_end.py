import pytest
from src.agent import Agent
from src.models import CoachRequest


def test_end_to_end_smoke(monkeypatch):
    """Smoke test: agent produces speech with achievement references."""
    
    call_count = 0
    
    def mock_llm_call(self, messages):
        nonlocal call_count
        call_count += 1
        
        if call_count == 1:
            # First call is planning
            return '{"action":"get_highlights","args":{"query":"interview","k":3}}'
        else:
            # Second call is final
            return "Good luck with your interview! Your Spanish skills [A5] and leadership experience [A4] will serve you well.\n\nUSED_IDS: [A5, A4]"
    
    monkeypatch.setattr(Agent, "llm_call", mock_llm_call)
    
    request = CoachRequest(scenario="Grafana interview", energy=2)
    agent = Agent()
    response = agent.run(request)
    
    assert len(response.used_ids) >= 2
    assert response.speech.strip()
    assert response.confidence is not None
