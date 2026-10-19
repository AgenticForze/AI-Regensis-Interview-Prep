"""Coach agent: mock interviewer and Architecture Review, on the Claude Messages API.

Design (see docs/agent-architecture.md):
* The LLM handles conversation, judgement and spec extraction.
* Everything factual or deterministic is a tool: catalog lookup, rubric, progress
  tracking, rule-based review and rendering. The model never invents catalog content.
* Loops are capped (MAX_STEPS) and every tool error goes back to the model as a
  structured, actionable message.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable

import yaml

from . import tools as T
from .review import load_architecture, report_markdown, review, validate_spec

MODEL = os.environ.get("AAP_MODEL", "claude-sonnet-5-5")
MAX_STEPS = 12
MAX_SPEC_ATTEMPTS = 3

COACH_SYSTEM = """\
You are an interview coach for senior engineers preparing for agentic-AI interviews in Telco BSS and
FinTech. You run mock interviews from a catalog of 360 production anti-pattern scenarios.

How each round works:
1. Call next_question (pass the user's topic or domain if they named one). Present the setup and the
   question in your own words. Don't hint at the answer.
2. Wait for the user's answer.
3. Call grading_rubric. Judge each of the 5 criteria strictly as true or false against the user's
   answer; accept good fixes the reference doesn't list.
4. Reply with: score out of 5, one line per criterion (met or missed and why), the reference fix in
   2-4 bullets, the analogy, and the interview line. Keep it under 250 words.
5. Call record_attempt with the criteria.
If the user asks about progress, call get_progress and suggest the weakest topic next.
If the user asks a concept question, answer it, citing scenario ids from search_scenarios.
Use plain, direct language.
"""

EXTRACT_SYSTEM = """\
You convert a plain-language description of an agentic AI system into an architecture spec for
Architecture Review. Follow the spec guide exactly. Rules:
- Use 3-6 lanes, top to bottom: inputs/channel, orchestration, tools/knowledge, systems of record.
  Max 4 nodes per lane. Use a spacer next to a lone channel or agent so the review can add controls.
- Choose the most specific node type. Write/payment/provision tools are separate nodes.
- Set attributes only from what the description states or clearly implies. If a control isn't
  mentioned, leave its attribute out: absence means "not in place".
- Keep titles to ~16 characters and subtitles to ~19.
- If something critical to the review is genuinely unknown (for example how identity is verified
  before an irreversible action), set clarifying_question to ONE short question. Otherwise omit it.
Call submit_spec exactly once per attempt.

SPEC GUIDE:
{guide}

EXAMPLE SPEC (telco-sim-swap-agent):
{example}
"""

SUBMIT_SPEC_TOOL = {
    "name": "submit_spec",
    "description": "Submit the architecture spec, or a single clarifying question if something critical is unknown.",
    "input_schema": {
        "type": "object",
        "properties": {
            "spec": {"type": "object", "description": "The architecture spec (title, domain, scenario, lanes, edges, bus)."},
            "clarifying_question": {"type": "string"},
        },
        "required": ["spec"],
    },
}

EXTRA_RISKS_SYSTEM = """\
You are reviewing an agentic AI architecture. A deterministic rule catalog already found the issues
listed below. Add at most 3 further risks that are specific to this scenario and NOT already covered.
For each, call search_scenarios to find the closest catalog scenario and cite its id. Answer in
Markdown: a heading per risk, then Why, Fix and Catalog reference lines. If nothing important is
missing, say so in one sentence.
"""


def _block_to_dict(b: Any) -> dict:
    if isinstance(b, dict):
        return b
    if b.type == "text":
        return {"type": "text", "text": b.text}
    if b.type == "tool_use":
        return {"type": "tool_use", "id": b.id, "name": b.name, "input": b.input}
    return {"type": b.type}


def run_tool(name: str, args: dict, extra: dict[str, Callable] | None = None) -> tuple[str, bool]:
    """Execute a tool and return (content, is_error). Errors are returned, never raised."""
    funcs = {**T.TOOL_FUNCS, **(extra or {})}
    fn = funcs.get(name)
    if not fn:
        return f"Unknown tool '{name}'. Available: {sorted(funcs)}", True
    try:
        result = fn(**args)
        return (result if isinstance(result, str) else json.dumps(result, indent=1, default=str)), False
    except TypeError as e:
        return f"Bad arguments for {name}: {e}", True
    except (ValueError, KeyError) as e:
        return str(e), True


class Coach:
    def __init__(self, client: Any = None, model: str = MODEL, user_id: str = "default"):
        if client is None:
            import anthropic
            client = anthropic.Anthropic()
        self.client = client
        self.model = model
        self.user_id = user_id
        self.messages: list[dict] = []

    # ---------------------------------------------------------- generic tool loop
    def _loop(self, system: str, messages: list[dict], tools: list[dict], max_tokens: int = 2000) -> str:
        for _ in range(MAX_STEPS):
            resp = self.client.messages.create(model=self.model, max_tokens=max_tokens, system=system,
                                               tools=tools, messages=messages)
            content = [_block_to_dict(b) for b in resp.content]
            messages.append({"role": "assistant", "content": content})
            calls = [b for b in content if b["type"] == "tool_use"]
            if resp.stop_reason != "tool_use" or not calls:
                return "\n".join(b["text"] for b in content if b["type"] == "text").strip()
            results = []
            for c in calls:
                args = dict(c["input"])
                if c["name"] in ("next_question", "record_attempt", "get_progress"):
                    args.setdefault("user_id", self.user_id)
                out, err = run_tool(c["name"], args)
                results.append({"type": "tool_result", "tool_use_id": c["id"], "content": out, "is_error": err})
            messages.append({"role": "user", "content": results})
        return "(stopped: step limit reached; ask again to continue)"

    # ---------------------------------------------------------- interview mode
    def chat(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})
        return self._loop(COACH_SYSTEM, self.messages, T.api_tools())

    # ---------------------------------------------------------- review mode
    def extract_spec(self, scenario: str, answer_question: Callable[[str], str] | None = None) -> dict:
        system = EXTRACT_SYSTEM.format(
            guide=T.architecture_spec_guide(),
            example=yaml.safe_dump(load_architecture("telco-sim-swap-agent"), sort_keys=False))
        messages: list[dict] = [{"role": "user", "content": f"Scenario:\n{scenario}"}]
        asked = False
        errs = ["no spec submitted"]
        for _ in range(MAX_SPEC_ATTEMPTS + 1):
            resp = self.client.messages.create(
                model=self.model, max_tokens=4000, system=system, messages=messages,
                tools=[SUBMIT_SPEC_TOOL], tool_choice={"type": "tool", "name": "submit_spec"})
            content = [_block_to_dict(b) for b in resp.content]
            messages.append({"role": "assistant", "content": content})
            call = next(b for b in content if b["type"] == "tool_use")
            q = call["input"].get("clarifying_question")
            if q and not asked and answer_question:
                asked = True
                messages.append({"role": "user", "content": [{
                    "type": "tool_result", "tool_use_id": call["id"],
                    "content": f"Answer from the user: {answer_question(q)}. Submit the spec now."}]})
                continue
            spec = call["input"].get("spec") or {}
            spec.setdefault("scenario", scenario)
            errs = validate_spec(spec)
            if not errs:
                return spec
            messages.append({"role": "user", "content": [{
                "type": "tool_result", "tool_use_id": call["id"], "is_error": True,
                "content": "Spec invalid, fix these and resubmit:\n- " + "\n- ".join(errs)}]})
        raise ValueError("Could not produce a valid spec: " + "; ".join(errs))

    def extra_risks(self, spec: dict, findings: list[dict]) -> str:
        found = "\n".join(f"- {f['label']}. {f['title']}" for f in findings)
        messages = [{"role": "user", "content": f"Scenario:\n{spec.get('scenario', '')}\n\n"
                                                f"Spec:\n{yaml.safe_dump(spec, sort_keys=False)}\n"
                                                f"Already found:\n{found}"}]
        tools = [t for t in T.api_tools() if t["name"] in ("search_scenarios", "get_scenario")]
        return self._loop(EXTRA_RISKS_SYSTEM, messages, tools, max_tokens=1500)

    def review_scenario(self, scenario: str, out_dir: str,
                        answer_question: Callable[[str], str] | None = None) -> dict:
        spec = self.extract_spec(scenario, answer_question)
        result = review(spec)
        extra = self.extra_risks(spec, result["findings"])
        d = Path(out_dir)
        d.mkdir(parents=True, exist_ok=True)
        (d / "spec.yaml").write_text(yaml.safe_dump(spec, sort_keys=False))
        (d / "fixed-spec.yaml").write_text(yaml.safe_dump(result["fixed_spec"], sort_keys=False))
        (d / "before.svg").write_text(result["before_svg"])
        (d / "after.svg").write_text(result["after_svg"])
        report = report_markdown(result, "before.svg", "after.svg")
        report += "\n## 5. Additional risks (model judgement, not from the rule catalog)\n\n" + extra + "\n"
        (d / "report.md").write_text(report)
        return {"spec": spec, "findings": result["findings"], "report_path": str(d / "report.md"),
                "out_dir": str(d)}
