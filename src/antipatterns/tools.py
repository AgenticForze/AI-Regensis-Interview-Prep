"""The toolbox shared by the MCP server, the coach agent and the skill scripts.

Every function takes and returns JSON-serialisable values. ``TOOLS`` holds the tool
definitions (name, description, input schema) used by the Claude API agent; the MCP
server registers the same functions with the same descriptions.
"""
from __future__ import annotations

import random
from pathlib import Path

import yaml

from . import tracker
from .catalog import all_scenarios, get_scenario as _get, get_topic, load_topics, search
from .render import render_arch, render_fix
from .review import list_architectures, load_architecture, report_markdown, review, validate_spec

RUBRIC = {
    "names_antipattern": "Names the anti-pattern or root cause, not just the symptom.",
    "explains_mechanism": "Explains why it breaks (the mechanism), in the scenario's terms.",
    "concrete_fix": "Gives a concrete fix in the right layer (tool, pipeline, policy, data), not 'improve the prompt'.",
    "detection": "Says how to detect or measure it in production or CI.",
    "tradeoff": "Names a trade-off or cost of the fix.",
}


# ------------------------------------------------------------------ catalog
def list_topics() -> list[dict]:
    """All 18 topics with id, title, summary and scenario count."""
    return [{"id": t["id"], "title": t["title"], "summary": t["summary"], "scenarios": len(t["scenarios"])}
            for t in load_topics()]


def search_scenarios(query: str, topic: str | None = None, domain: str | None = None, limit: int = 8) -> list[dict]:
    """Keyword search over the 360 scenarios. Returns id, title, topic, domain, severity."""
    return [{k: s[k] for k in ("id", "title", "topic", "domain", "severity")}
            for s in search(query, topic=topic, domain=domain, limit=limit)]


def get_scenario(scenario_id: str, include_diagram: bool = False) -> dict:
    """Full scenario: situation, analogy, what breaks, root cause, fix, detection, trade-off, variant."""
    s = _get(scenario_id)
    if not s:
        raise ValueError(f"Unknown scenario '{scenario_id}'. Use search_scenarios to find ids.")
    out = {k: v for k, v in s.items() if not k.startswith("_")}
    if include_diagram:
        out["diagram_svg"] = render_fix({**s["diagram"], "title": s["title"]})
    return out


# ------------------------------------------------------------------ interview coach
def next_question(user_id: str = "default", topic: str | None = None, domain: str | None = None,
                  seed: int | None = None) -> dict:
    """Pick the next interview scenario: unanswered first, biased toward the user's weakest topics.

    Returns only the setup (scenario text and title), never the answer.
    """
    rng = random.Random(seed)
    prog = tracker.progress(user_id)
    pool = [s for s in all_scenarios()
            if (not topic or s["topic"] == topic) and (not domain or s["domain"] == domain)]
    if not pool:
        raise ValueError("No scenarios match that topic/domain.")
    fresh = [s for s in pool if s["id"] not in prog["answered"]] or pool
    weak = set(prog["weakest_topics"]) if not topic else set()
    weighted = [s for s in fresh if s["topic"] in weak] if weak and rng.random() < 0.6 else []
    s = rng.choice(weighted or fresh)
    return {
        "scenario_id": s["id"], "topic": s["topic_title"], "domain": s["domain"], "severity": s["severity"],
        "setup": s["scenario"],
        "question": "What is going wrong here, why, and how would you fix and detect it in production?",
    }


def grading_rubric(scenario_id: str) -> dict:
    """The rubric and reference answer for grading a candidate's answer to a scenario.

    Score one point per criterion met (0-5). Use the reference to judge, but accept
    equivalent fixes the reference doesn't list.
    """
    s = _get(scenario_id)
    if not s:
        raise ValueError(f"Unknown scenario '{scenario_id}'")
    return {
        "scenario_id": scenario_id,
        "criteria": RUBRIC,
        "reference": {
            "anti_pattern": s["title"], "root_cause": s["root_cause"], "breaks": s["breaks"],
            "where": s["where"], "fix": s["fix"], "detect": s["detect"], "tradeoff": s["tradeoff"],
            "interview_line": s["line"],
        },
    }


def record_attempt(scenario_id: str, criteria: dict, user_id: str = "default", notes: str = "") -> dict:
    """Store a graded attempt. `criteria` maps each rubric key to true/false."""
    s = _get(scenario_id)
    if not s:
        raise ValueError(f"Unknown scenario '{scenario_id}'")
    unknown = set(criteria) - set(RUBRIC)
    if unknown:
        raise ValueError(f"Unknown rubric keys {sorted(unknown)}; use {sorted(RUBRIC)}")
    clean = {k: bool(criteria.get(k, False)) for k in RUBRIC}
    score = tracker.record(user_id, scenario_id, s["topic"], clean, notes)
    return {"scenario_id": scenario_id, "score": score, "out_of": len(RUBRIC)}


def get_progress(user_id: str = "default") -> dict:
    """Attempts, average score, per-topic averages, weakest topics and most-missed rubric criteria."""
    return tracker.progress(user_id)


# ------------------------------------------------------------------ architecture review
def list_reference_architectures() -> list[dict]:
    """Prebuilt Telco and FinTech architectures that can be reviewed or used as examples."""
    return list_architectures()


def get_reference_architecture(arch_id: str) -> dict:
    """The spec of a reference architecture, as a dict (same format review_architecture takes)."""
    return load_architecture(arch_id)


def architecture_spec_guide() -> str:
    """How to write an architecture spec: shape, node types and the attributes rules read."""
    p = Path(__file__).resolve().parents[2] / "docs" / "architecture-spec.md"
    local = Path(__file__).resolve().parent / "content" / "architecture-spec.md"
    return (local if local.exists() else p).read_text()


def check_architecture_spec(spec: dict) -> dict:
    """Validate a spec without reviewing it. Returns {valid, errors}."""
    errs = validate_spec(spec)
    return {"valid": not errs, "errors": errs}


def render_architecture(spec: dict) -> str:
    """Render a spec as a swimlane SVG without reviewing it."""
    errs = validate_spec(spec)
    if errs:
        raise ValueError("; ".join(errs))
    return render_arch(spec)


def review_architecture(spec: dict, out_dir: str | None = None) -> dict:
    """Run Architecture Review on a spec.

    Returns the numbered findings (each linked to catalog scenarios) and a Markdown report.
    If out_dir is given, also writes before.svg, after.svg and report.md there and returns
    their paths.
    """
    result = review(spec)
    out = {"title": result["title"], "findings": result["findings"]}
    if out_dir:
        d = Path(out_dir)
        d.mkdir(parents=True, exist_ok=True)
        (d / "before.svg").write_text(result["before_svg"])
        (d / "after.svg").write_text(result["after_svg"])
        (d / "fixed-spec.yaml").write_text(yaml.safe_dump(result["fixed_spec"], sort_keys=False))
        (d / "report.md").write_text(report_markdown(result, "before.svg", "after.svg"))
        out["files"] = {k: str(d / f) for k, f in
                        [("before_svg", "before.svg"), ("after_svg", "after.svg"),
                         ("report", "report.md"), ("fixed_spec", "fixed-spec.yaml")]}
    else:
        out["report_markdown"] = report_markdown(result)
        out["before_svg"] = result["before_svg"]
        out["after_svg"] = result["after_svg"]
    return out


def topic_summary(topic_id: str) -> dict:
    t = get_topic(topic_id)
    if not t:
        raise ValueError(f"Unknown topic '{topic_id}'")
    return {"id": t["id"], "title": t["title"], "summary": t["summary"],
            "scenarios": [{k: s[k] for k in ("id", "title", "domain", "severity")} for s in t["scenarios"]]}


# ------------------------------------------------------------------ tool definitions for the Claude API
def _schema(props: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}


_STR = {"type": "string"}
SPEC_SCHEMA = {"type": "object", "description": "Architecture spec; see architecture_spec_guide."}

TOOLS = [
    {"name": "list_topics", "fn": list_topics,
     "description": "List the 18 interview topics with summaries. Use to orient or let the user choose a topic.",
     "input_schema": _schema({}, [])},
    {"name": "search_scenarios", "fn": search_scenarios,
     "description": "Keyword search across the 360 Telco/FinTech anti-pattern scenarios. Returns ids and titles only; "
                    "call get_scenario for details. Use when the user asks about a concept or you need a catalog reference.",
     "input_schema": _schema({"query": _STR, "topic": _STR, "domain": {"type": "string", "enum": ["telco", "fintech"]},
                              "limit": {"type": "integer", "minimum": 1, "maximum": 20}}, ["query"])},
    {"name": "get_scenario", "fn": get_scenario,
     "description": "Full detail for one scenario id (e.g. rag-01): situation, analogy, what breaks, root cause, fix, "
                    "detection, trade-off, other-domain variant and interview line.",
     "input_schema": _schema({"scenario_id": _STR}, ["scenario_id"])},
    {"name": "next_question", "fn": next_question,
     "description": "Pick the next interview scenario for the user, favouring unanswered scenarios and weak topics. "
                    "Returns only the setup. Present the setup and question; never reveal the answer before the user tries.",
     "input_schema": _schema({"user_id": _STR, "topic": _STR, "domain": {"type": "string", "enum": ["telco", "fintech"]}}, [])},
    {"name": "grading_rubric", "fn": grading_rubric,
     "description": "Rubric (5 binary criteria) and reference answer for a scenario. Call after the user answers, "
                    "grade each criterion true/false, then call record_attempt.",
     "input_schema": _schema({"scenario_id": _STR}, ["scenario_id"])},
    {"name": "record_attempt", "fn": record_attempt,
     "description": "Save a graded attempt. criteria maps names_antipattern, explains_mechanism, concrete_fix, detection, "
                    "tradeoff to true/false.",
     "input_schema": _schema({"scenario_id": _STR, "criteria": {"type": "object"}, "user_id": _STR, "notes": _STR},
                             ["scenario_id", "criteria"])},
    {"name": "get_progress", "fn": get_progress,
     "description": "The user's progress: attempts, average score, per-topic averages, weakest topics, most-missed criteria.",
     "input_schema": _schema({"user_id": _STR}, [])},
    {"name": "list_reference_architectures", "fn": list_reference_architectures,
     "description": "Prebuilt Telco and FinTech agentic architectures (SIM swap, roaming RAG, port-in, card disputes...).",
     "input_schema": _schema({}, [])},
    {"name": "get_reference_architecture", "fn": get_reference_architecture,
     "description": "The spec of a reference architecture by id. Useful as an example when writing a new spec.",
     "input_schema": _schema({"arch_id": _STR}, ["arch_id"])},
    {"name": "architecture_spec_guide", "fn": architecture_spec_guide,
     "description": "How to write an architecture spec: lanes, node types and the attributes the rules read. Read before "
                    "writing a spec from a user's scenario.",
     "input_schema": _schema({}, [])},
    {"name": "check_architecture_spec", "fn": check_architecture_spec,
     "description": "Validate a spec (ids, node types, edges, label lengths) without reviewing it.",
     "input_schema": _schema({"spec": SPEC_SCHEMA}, ["spec"])},
    {"name": "review_architecture", "fn": review_architecture,
     "description": "Run Architecture Review on a spec: numbered failure points from the rule catalog, fixes linked to "
                    "scenarios, a fixed design, two SVG diagrams and a Markdown report. Pass out_dir to write files.",
     "input_schema": _schema({"spec": SPEC_SCHEMA, "out_dir": _STR}, ["spec"])},
]
TOOL_FUNCS = {t["name"]: t["fn"] for t in TOOLS}


def api_tools() -> list[dict]:
    """Tool definitions in Claude API format."""
    return [{k: t[k] for k in ("name", "description", "input_schema")} for t in TOOLS]
