"""Agent loop tests with a scripted fake Claude client (no API key needed)."""
import copy
from types import SimpleNamespace as NS

import pytest

from antipatterns.agent import Coach
from antipatterns.review import load_architecture


def text(t):
    return NS(type="text", text=t)


def tool(id_, name, inp):
    return NS(type="tool_use", id=id_, name=name, input=inp)


class FakeClient:
    """Returns scripted responses in order and records every request."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = []
        self.messages = self

    def create(self, **kw):
        self.calls.append(copy.deepcopy(kw))
        content, stop = self.script.pop(0)
        return NS(content=content, stop_reason=stop)


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("AAP_PROGRESS_DB", str(tmp_path / "p.db"))


def test_interview_round_executes_tools_and_records():
    client = FakeClient([
        ([tool("t1", "next_question", {"topic": "rag"})], "tool_use"),
        ([text("Here is your scenario...")], "end_turn"),
        ([tool("t2", "grading_rubric", {"scenario_id": "rag-01"})], "tool_use"),
        ([tool("t3", "record_attempt", {"scenario_id": "rag-01", "criteria": {
            "names_antipattern": True, "explains_mechanism": True, "concrete_fix": True,
            "detection": False, "tradeoff": False}})], "tool_use"),
        ([text("Score 3/5")], "end_turn"),
    ])
    coach = Coach(client=client, user_id="u1")
    assert coach.chat("start") == "Here is your scenario..."
    tool_result = client.calls[1]["messages"][-1]["content"][0]
    assert tool_result["type"] == "tool_result" and not tool_result["is_error"]
    assert '"scenario_id": "rag-' in tool_result["content"]
    assert coach.chat("my answer") == "Score 3/5"
    from antipatterns.tools import get_progress
    assert get_progress("u1")["attempts"] == 1


def test_unknown_tool_and_bad_id_return_errors_to_model():
    client = FakeClient([
        ([tool("t1", "get_scenario", {"scenario_id": "nope-99"})], "tool_use"),
        ([text("ok")], "end_turn"),
    ])
    Coach(client=client).chat("hi")
    res = client.calls[1]["messages"][-1]["content"][0]
    assert res["is_error"] and "search_scenarios" in res["content"]


def test_extract_spec_retries_on_invalid_spec_then_succeeds():
    good = load_architecture("telco-sim-swap-agent")
    bad = copy.deepcopy(good)
    bad["lanes"][2]["nodes"][0]["type"] = "tool_magic"
    client = FakeClient([
        ([tool("s1", "submit_spec", {"spec": bad})], "tool_use"),
        ([tool("s2", "submit_spec", {"spec": good})], "tool_use"),
    ])
    spec = Coach(client=client).extract_spec("sim swap agent")
    assert spec["title"] == "SIM-swap agent"
    err = client.calls[1]["messages"][-1]["content"][0]
    assert err["is_error"] and "unknown type 'tool_magic'" in err["content"]
    assert client.calls[0]["tool_choice"] == {"type": "tool", "name": "submit_spec"}


def test_extract_spec_asks_one_clarifying_question():
    good = load_architecture("telco-sim-swap-agent")
    client = FakeClient([
        ([tool("s1", "submit_spec", {"spec": {}, "clarifying_question": "How is identity verified?"})], "tool_use"),
        ([tool("s2", "submit_spec", {"spec": good})], "tool_use"),
    ])
    asked = []
    Coach(client=client).extract_spec("sim swap", answer_question=lambda q: asked.append(q) or "SMS OTP")
    assert asked == ["How is identity verified?"]
    assert "SMS OTP" in client.calls[1]["messages"][-1]["content"][0]["content"]


def test_review_scenario_writes_report(tmp_path):
    good = load_architecture("telco-sim-swap-agent")
    client = FakeClient([
        ([tool("s1", "submit_spec", {"spec": good})], "tool_use"),
        ([text("Nothing important is missing.")], "end_turn"),
    ])
    res = Coach(client=client).review_scenario("sim swap", str(tmp_path / "out"))
    report = (tmp_path / "out" / "report.md").read_text()
    assert "Weak identity verification" in report and "Additional risks" in report
    assert (tmp_path / "out" / "before.svg").read_text().startswith("<svg")
    assert len([f for f in res["findings"] if f["scope"] == "component"]) == 6


def test_step_limit_stops_runaway_loop():
    client = FakeClient([([tool(f"t{i}", "list_topics", {})], "tool_use") for i in range(20)])
    out = Coach(client=client).chat("loop")
    assert "step limit" in out
