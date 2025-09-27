import os
import pytest
from unittest.mock import patch
from src.agent import Agent
from src.models import CoachRequest, CoachResponse
from src.prompts import FINAL_INSTRUCTION


def test_plan_stage_returns_tool_call():
    """Stub planning should return a JSON command with the scenario."""
    with patch.dict(os.environ, {"LLM_MODE": "stub"}):
        agent = Agent()
        req = CoachRequest(scenario="job interview", energy=2)
        resp = agent.llm_call([
            {"role": "system", "content": "system"},
            {"role": "user", "content": f"Scenario: {req.scenario}"},
            {"role": "system", "content": "planning"}
        ])
        assert '"action":"get_highlights"' in resp
        assert req.scenario in resp


def test_final_stage_stubbed_when_flag_set():
    """Stub final output should include USED_IDS if LLM_STUB_FINAL=1."""
    with patch.dict(os.environ, {"LLM_MODE": "stub", "LLM_STUB_FINAL": "1"}):
        agent = Agent()
        resp = agent.llm_call([
            {"role": "system", "content": "system"},
            {"role": "user", "content": "Scenario: practice"},
            {"role": "system", "content": FINAL_INSTRUCTION}
        ])
        assert "USED_IDS" in resp
        assert "[A1" in resp


def test_run_flow_in_stub_mode():
    """End-to-end run should produce a CoachResponse with ids + speech."""
    with patch.dict(os.environ, {"LLM_MODE": "stub", "LLM_STUB_FINAL": "1"}):
        agent = Agent()
        req = CoachRequest(scenario="interview", energy=2)
        out = agent.run(req)

        assert isinstance(out, CoachResponse)
        assert out.used_ids == ["A1", "A2"]
        assert out.confidence == 0.8
        # The speech should not contain the raw USED_IDS tag
        assert "USED_IDS:" not in out.speech


def test_confidence_drops_without_ids():
    """If no USED_IDS are present, confidence falls to 0.4."""
    with patch.dict(os.environ, {"LLM_MODE": "stub"}):
        agent = Agent()
        # Patch llm_call to skip ids
        with patch.object(agent, "llm_call") as mock_call:
            mock_call.side_effect = [
                '{"action":"proceed"}',  # planning
                "Just pep talk text"     # final
            ]
            req = CoachRequest(scenario="test", energy=1)
            out = agent.run(req)
            assert out.used_ids == []
            assert out.confidence == 0.4


def test_non_json_planning_treated_as_final():
    """If planning isn’t JSON, it’s just the final output."""
    with patch.dict(os.environ, {"LLM_MODE": "stub"}):
        agent = Agent()
        with patch.object(agent, "llm_call", return_value="Direct pep\nUSED_IDS: [A1]"):
            req = CoachRequest(scenario="hello", energy=1)
            out = agent.run(req)
            assert out.used_ids == ["A1"]
            assert "Direct pep" in out.speech
