import asyncio
import json
import sys
from pathlib import Path

import pytest

from antipatterns import tools as T

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("AAP_PROGRESS_DB", str(tmp_path / "p.db"))


def test_catalog_shape():
    topics = T.list_topics()
    assert len(topics) == 18 and all(t["scenarios"] == 20 for t in topics)
    assert T.search_scenarios("idempotency retry payment")[0]["id"] in {"agf-06", "tool-15"}


def test_next_question_hides_answer_and_prefers_unanswered():
    q = T.next_question("u", topic="rag", seed=1)
    assert set(q) == {"scenario_id", "topic", "domain", "severity", "setup", "question"}
    T.record_attempt(q["scenario_id"], {k: True for k in T.RUBRIC}, user_id="u")
    seen = {T.next_question("u", topic="rag", seed=s)["scenario_id"] for s in range(30)}
    assert q["scenario_id"] not in seen


def test_record_attempt_rejects_unknown_criteria():
    with pytest.raises(ValueError):
        T.record_attempt("rag-01", {"vibes": True})


def test_api_tool_schemas_are_complete():
    for t in T.api_tools():
        assert t["description"] and t["input_schema"]["type"] == "object"


@pytest.mark.skipif(sys.version_info < (3, 10), reason="mcp needs 3.10+")
def test_mcp_server_lists_and_calls_tools(tmp_path):
    mcp = pytest.importorskip("mcp")
    from mcp.client.stdio import StdioServerParameters, stdio_client

    async def run():
        p = StdioServerParameters(command=sys.executable, args=[str(ROOT / "mcp_server/server.py")],
                                  env={"AAP_PROGRESS_DB": str(tmp_path / "m.db")})
        async with stdio_client(p) as (r, w):
            async with mcp.ClientSession(r, w) as s:
                await s.initialize()
                names = {t.name for t in (await s.list_tools()).tools}
                res = await s.call_tool("get_scenario", {"scenario_id": "rag-01"})
                return names, json.loads(res.content[0].text)

    names, scen = asyncio.run(run())
    assert {"next_question", "review_architecture", "grading_rubric"} <= names
    assert scen["title"].startswith("Fixed-size chunking")
