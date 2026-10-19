"""Load, search and validate the scenario catalog in content/topics/*.yaml."""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

from .render import GAP_FIX, INNER_W, label_problems

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content"

REQUIRED = ["id", "title", "domain", "severity", "scenario", "analogy", "breaks", "root_cause",
            "where", "fix", "detect", "tradeoff", "variant", "line", "diagram"]
DOMAINS = {"telco", "fintech"}
SEVERITIES = {"critical", "high", "medium", "low"}


def content_dir() -> Path:
    """Content root. Bundled copies (skill, MCP) may ship content next to the package."""
    local = Path(__file__).resolve().parent / "content"
    return local if local.exists() else CONTENT


@lru_cache(maxsize=1)
def load_topics() -> list[dict]:
    topics = []
    for p in sorted((content_dir() / "topics").glob("*.yaml")):
        try:
            t = yaml.safe_load(p.read_text())
        except yaml.YAMLError as e:
            raise ValueError(f"{p.name}: invalid YAML: {e}") from None
        t["_file"] = p.name
        for s in t["scenarios"]:
            s["topic"] = t["id"]
            s["topic_title"] = t["title"]
        topics.append(t)
    return sorted(topics, key=lambda t: t["order"])


def all_scenarios() -> list[dict]:
    return [s for t in load_topics() for s in t["scenarios"]]


def get_scenario(sid: str) -> dict | None:
    return next((s for s in all_scenarios() if s["id"] == sid), None)


def get_topic(tid: str) -> dict | None:
    return next((t for t in load_topics() if t["id"] == tid), None)


_WORD = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def search(query: str, topic: str | None = None, domain: str | None = None, limit: int = 10) -> list[dict]:
    """Keyword search over titles, scenarios and fixes. Title hits weigh most."""
    q = set(_tokens(query))
    results = []
    for s in all_scenarios():
        if topic and s["topic"] != topic:
            continue
        if domain and s["domain"] != domain:
            continue
        title = set(_tokens(s["title"]))
        body = set(_tokens(" ".join([s["scenario"], s["root_cause"], " ".join(s["fix"]), " ".join(s.get("tags", []))])))
        score = 3 * len(q & title) + len(q & body)
        if score or not q:
            results.append((score, s))
    results.sort(key=lambda r: (-r[0], r[1]["id"]))
    return [s for _, s in results[:limit]]


def summary(s: dict) -> dict:
    return {k: s[k] for k in ("id", "title", "topic", "domain", "severity")}


def validate() -> list[str]:
    """Return a list of problems; empty means the catalog is valid."""
    errs: list[str] = []
    topics = load_topics()
    ids: set[str] = set()
    box_w = (INNER_W - GAP_FIX * 3) / 4
    for t in topics:
        for key in ("id", "order", "title", "summary", "prefix", "scenarios"):
            if key not in t:
                errs.append(f"{t['_file']}: missing topic field '{key}'")
        if len(t.get("scenarios", [])) != 20:
            errs.append(f"{t['_file']}: has {len(t.get('scenarios', []))} scenarios, expected 20")
        for s in t.get("scenarios", []):
            sid = s.get("id", "?")
            for k in REQUIRED:
                if not s.get(k):
                    errs.append(f"{sid}: missing '{k}'")
            if sid in ids:
                errs.append(f"{sid}: duplicate id")
            ids.add(sid)
            if not sid.startswith(t.get("prefix", "") + "-"):
                errs.append(f"{sid}: id should start with '{t.get('prefix')}-'")
            if s.get("domain") not in DOMAINS:
                errs.append(f"{sid}: domain must be one of {sorted(DOMAINS)}")
            if s.get("severity") not in SEVERITIES:
                errs.append(f"{sid}: severity must be one of {sorted(SEVERITIES)}")
            for k in ("breaks", "fix", "detect"):
                if k in s and not isinstance(s[k], list):
                    errs.append(f"{sid}: '{k}' must be a list")
                elif k in s and not all(isinstance(i, str) for i in s[k]):
                    errs.append(f"{sid}: every item in '{k}' must be plain text (check for a stray ': ')")
            for k in ("scenario", "analogy", "root_cause", "where", "tradeoff", "variant", "line"):
                if k in s and not isinstance(s[k], str):
                    errs.append(f"{sid}: '{k}' must be text")
            d = s.get("diagram") or {}
            for lane in ("bad", "good"):
                boxes = d.get(lane) or []
                if not 2 <= len(boxes) <= 4:
                    errs.append(f"{sid}: diagram.{lane} needs 2-4 boxes")
                w = (INNER_W - GAP_FIX * (len(boxes) - 1)) / max(len(boxes), 1)
                for b in boxes:
                    for p in label_problems(b[0], b[1] if len(b) > 1 else "", min(w, box_w if len(boxes) == 4 else w)):
                        errs.append(f"{sid}: diagram.{lane}: {p}")
            for lbl in ("bad_label", "good_label"):
                if len(d.get(lbl, "")) > 70:
                    errs.append(f"{sid}: diagram.{lbl} longer than 70 chars")
    for s in all_scenarios():
        for r in s.get("related", []):
            if r not in ids:
                errs.append(f"{s['id']}: related id '{r}' does not exist")
    return errs
