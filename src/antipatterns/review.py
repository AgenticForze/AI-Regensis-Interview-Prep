"""Architecture Review: find failure points in an agentic architecture and propose fixes.

Input is an architecture *spec* (see content/architectures/*.yaml and
docs/architecture-spec.md): swimlanes of typed nodes with attributes, edges and an
optional tool bus. ``review(spec)`` runs the deterministic rule catalog in
content/rules.yaml, numbers the failure points, renders an annotated "as described"
diagram, builds a fixed architecture by applying each rule's patch, renders it, and
produces a Markdown report whose findings link back to scenario ids in the catalog.

``site/src/review.js`` is a port of this module used by the website; the parity test
keeps both outputs identical.
"""
from __future__ import annotations

import copy
from functools import lru_cache
from pathlib import Path

import yaml

from .catalog import content_dir, get_scenario
from .render import GAP_ARCH, INNER_W, label_problems, render_arch

NODE_TYPES = {
    "channel", "agent", "router", "retriever", "knowledge", "vector_store", "tool_read",
    "tool_write", "tool_payment", "tool_provision", "tool_identity", "tool_fraud",
    "tool_notify", "tool_code", "system_of_record", "policy", "human_approval",
    "guardrail", "memory", "cache", "gateway", "observability", "eval", "audit",
    "queue", "external_agent", "spacer",
}
PURPLE_TYPES = {"agent", "router"}
MAX_PER_LANE = 4
BEFORE_LEGEND = "Red numbered markers = failure points"
AFTER_LEGEND = "Teal = new or changed control"


# ------------------------------------------------------------------ loading
@lru_cache(maxsize=1)
def load_rules() -> list[dict]:
    return yaml.safe_load((content_dir() / "rules.yaml").read_text())["rules"]


def list_architectures() -> list[dict]:
    out = []
    for p in sorted((content_dir() / "architectures").glob("*.yaml")):
        spec = yaml.safe_load(p.read_text())
        out.append({"id": p.stem, "title": spec["title"], "domain": spec.get("domain", ""),
                    "summary": spec.get("summary", "")})
    return out


def load_architecture(arch_id: str) -> dict:
    p = content_dir() / "architectures" / f"{arch_id}.yaml"
    if not p.exists():
        raise KeyError(f"unknown architecture '{arch_id}'")
    return yaml.safe_load(p.read_text())


# ------------------------------------------------------------------ helpers
def _nodes(spec: dict) -> list[tuple[int, int, dict]]:
    return [(li, ni, n) for li, lane in enumerate(spec["lanes"]) for ni, n in enumerate(lane["nodes"])]


def _attr(node: dict, key: str):
    return (node.get("attrs") or {}).get(key)


def _match(node: dict, cond: dict) -> bool:
    if node.get("type") not in cond.get("type", []):
        return False
    for k, v in (cond.get("attrs") or {}).items():
        if _attr(node, k) != v:
            return False
    for k, v in (cond.get("not") or {}).items():
        if _attr(node, k) == v:
            return False
    return True


def _first(spec: dict, types: list[str]):
    for li, ni, n in _nodes(spec):
        if n.get("type") in types:
            return li, ni, n
    return None


def default_kind(node: dict) -> str:
    t = node.get("type", "")
    if t == "spacer":
        return "spacer"
    if node.get("kind"):
        return node["kind"]
    return "agent" if t in PURPLE_TYPES or t.startswith("tool_") else "neutral"


# ------------------------------------------------------------------ validation
def validate_spec(spec: dict) -> list[str]:
    errs: list[str] = []
    if not spec.get("lanes"):
        return ["spec has no lanes"]
    ids: set[str] = set()
    for lane in spec["lanes"]:
        if not lane.get("nodes"):
            errs.append(f"lane '{lane.get('name')}' has no nodes")
            continue
        if len(lane["nodes"]) > MAX_PER_LANE:
            errs.append(f"lane '{lane['name']}' has more than {MAX_PER_LANE} nodes; split it")
        total = sum(n.get("span", 1) for n in lane["nodes"])
        usable = INNER_W - GAP_ARCH * (len(lane["nodes"]) - 1)
        for n in lane["nodes"]:
            if n.get("id") in ids:
                errs.append(f"duplicate node id '{n.get('id')}'")
            ids.add(n.get("id"))
            if n.get("type") not in NODE_TYPES:
                errs.append(f"node '{n.get('id')}': unknown type '{n.get('type')}'")
            if n.get("type") != "spacer":
                w = usable * n.get("span", 1) / total
                errs += [f"node '{n['id']}': {p}" for p in label_problems(n.get("title", ""), n.get("sub", ""), w)]
    for e in spec.get("edges", []):
        for end in ("from", "to"):
            if e.get(end) not in ids:
                errs.append(f"edge references unknown node '{e.get(end)}'")
    bus = spec.get("bus")
    if bus:
        for t in [bus.get("from")] + list(bus.get("to", [])):
            if t not in ids:
                errs.append(f"bus references unknown node '{t}'")
    return errs


def validate_library() -> list[str]:
    errs = []
    rule_ids = set()
    for r in load_rules():
        rule_ids.add(r["id"])
        for sid in r.get("scenarios", []):
            if not get_scenario(sid):
                errs.append(f"rule {r['id']}: scenario '{sid}' does not exist")
    for a in list_architectures():
        spec = load_architecture(a["id"])
        errs += [f"architecture {a['id']}: {e}" for e in validate_spec(spec)]
        result = review(spec)
        errs += [f"architecture {a['id']} (fixed): {e}" for e in validate_spec(result["fixed_spec"])]
        again = detect(result["fixed_spec"])
        if again:
            errs.append(f"architecture {a['id']}: fixed design still triggers {[f['rule'] for f in again]}")
    return errs


# ------------------------------------------------------------------ detection
def detect(spec: dict) -> list[dict]:
    """Return findings ordered by position in the diagram, then rule order."""
    found = []
    nodes = _nodes(spec)
    for ri, rule in enumerate(load_rules()):
        when = rule["when"]
        if "node" in when:
            for li, ni, n in nodes:
                if _match(n, when["node"]):
                    found.append((li, ni, ri, rule, n["id"]))
        elif "missing" in when:
            if _first(spec, when["missing"]):
                continue
            req = when.get("requires")
            if req and not any(_match(n, req) for _, _, n in nodes):
                continue
            target = None
            if rule["scope"] == "component":
                hit = _first(spec, [rule.get("marker_on", "agent")])
                if not hit:
                    continue
                li, ni, n = hit
                target = n["id"]
                found.append((li, ni, ri, rule, target))
            else:
                found.append((10**6, 0, ri, rule, None))
    found.sort(key=lambda f: (f[0], f[1], f[2]))
    out, comp, plat = [], 0, 0
    for li, ni, ri, rule, node_id in found:
        if rule["scope"] == "component":
            comp += 1
            label = str(comp)
        else:
            plat += 1
            label = f"P{plat}"
        out.append({"label": label, "rule": rule["id"], "node": node_id, "scope": rule["scope"]})
    return out


# ------------------------------------------------------------------ fixing
def _lane_index(spec: dict, name: str) -> int:
    for i, lane in enumerate(spec["lanes"]):
        if lane["name"] == name:
            return i
    order = ["Controls", "Platform controls"]
    spec["lanes"].append({"name": name, "nodes": []})
    if name in order:  # keep Controls above Platform controls
        spec["lanes"].sort(key=lambda l: order.index(l["name"].split(" (")[0]) if l["name"].split(" (")[0] in order else -1)
    return next(i for i, l in enumerate(spec["lanes"]) if l["name"] == name)


def _add_node(spec: dict, lane_name: str, node: dict, after: str | None = None) -> None:
    if any(n["id"] == node["id"] for _, _, n in _nodes(spec)):
        return
    li = _lane_index(spec, lane_name)
    lane = spec["lanes"][li]
    ids = [n["id"] for n in lane["nodes"]]
    for i, n in enumerate(lane["nodes"]):
        if n.get("kind") == "spacer" or n.get("type") == "spacer":
            lane["nodes"].pop(i)
            pos = ids.index(after) + 1 if after in ids else i
            lane["nodes"].insert(min(pos, len(lane["nodes"])), node)
            return
    if after in ids and len(lane["nodes"]) < MAX_PER_LANE:
        lane["nodes"].insert(ids.index(after) + 1, node)
        return
    real = [n for n in lane["nodes"]]
    if len(real) >= MAX_PER_LANE:
        base = lane["name"].split(" (")[0]
        k = 2
        while True:
            name = f"{base} ({k})"
            idx = next((i for i, l in enumerate(spec["lanes"]) if l["name"] == name), None)
            if idx is None:
                spec["lanes"].insert(li + k - 1, {"name": name, "nodes": [node]})
                return
            if len(spec["lanes"][idx]["nodes"]) < MAX_PER_LANE:
                spec["lanes"][idx]["nodes"].append(node)
                return
            k += 1
    lane["nodes"].append(node)


def _lane_of(spec: dict, node_id: str) -> str:
    for lane in spec["lanes"]:
        if any(n["id"] == node_id for n in lane["nodes"]):
            return lane["name"]
    return spec["lanes"][-1]["name"]


def fix(spec: dict, findings: list[dict]) -> dict:
    """Apply each finding's patch to a copy of the spec and return the fixed spec."""
    fixed = copy.deepcopy(spec)
    rules = {r["id"]: r for r in load_rules()}
    agent = _first(fixed, ["agent"])
    agent_id = agent[2]["id"] if agent else None
    by_id = {n["id"]: n for _, _, n in _nodes(fixed)}
    for n in by_id.values():
        n["kind"] = default_kind(n)
    for f in findings:
        patch = rules[f["rule"]].get("patch", {})
        node = by_id.get(f["node"]) if f["node"] else None

        def resolve(v):
            if v == "$agent":
                return agent_id
            if v == "$node":
                return f["node"]
            if v == "$agent_lane":
                return _lane_of(fixed, agent_id) if agent_id else "Controls"
            if v == "$node_lane":
                return _lane_of(fixed, f["node"]) if f["node"] else "Controls"
            return v

        if "set" in patch and node is not None:
            s = patch["set"]
            node.setdefault("attrs", {}).update(s.get("attrs", {}))
            if "title" in s:
                node["title"] = s["title"]
            if "sub" in s:
                if node.get("_patched_sub"):
                    combo = f"{node['sub']} + {s['sub']}"
                    if len(combo) <= 20:
                        node["sub"] = combo
                else:
                    node["sub"] = s["sub"]
                    node["_patched_sub"] = True
            if node.get("type") not in PURPLE_TYPES:
                node["kind"] = "good"
        if "add_node" in patch:
            a = dict(patch["add_node"])
            lane = resolve(a.pop("lane"))
            after = resolve(a.pop("after", None))
            new = {k: v for k, v in a.items()}
            new["kind"] = "good"
            _add_node(fixed, lane, new, after)
            by_id = {n["id"]: n for _, _, n in _nodes(fixed)}
        if "add_edge" in patch:
            e = {k: resolve(v) for k, v in patch["add_edge"].items()}
            if e["from"] and e["to"] and e not in fixed.setdefault("edges", []):
                fixed["edges"].append(e)
        if "add_to_bus" in patch:
            nid = patch["add_to_bus"]
            if fixed.get("bus"):
                if nid not in fixed["bus"]["to"]:
                    fixed["bus"]["to"].append(nid)
            elif agent_id:
                fixed.setdefault("edges", []).append({"from": agent_id, "to": nid})
    for n in by_id.values():
        n.pop("_patched_sub", None)
    fixed.pop("markers", None)
    fixed["legend"] = AFTER_LEGEND
    return fixed


# ------------------------------------------------------------------ review
def _diagram_spec(spec: dict) -> dict:
    d = copy.deepcopy(spec)
    for _, _, n in _nodes(d):
        n["kind"] = default_kind(n)
    return d


def review(spec: dict) -> dict:
    errs = validate_spec(spec)
    if errs:
        raise ValueError("invalid architecture spec: " + "; ".join(errs))
    findings = detect(spec)
    rules = {r["id"]: r for r in load_rules()}
    before = _diagram_spec(spec)
    before["markers"] = [{"node": f["node"], "n": f["label"]} for f in findings if f["scope"] == "component"]
    before["legend"] = BEFORE_LEGEND
    before["title"] = f"{spec['title']}: failure points"
    fixed = fix(spec, findings)
    fixed["title"] = f"{spec['title']}: fixed architecture"
    titles = {n["id"]: n["title"] for _, _, n in _nodes(spec)}
    detailed = []
    for f in findings:
        r = rules[f["rule"]]
        detailed.append({
            **f,
            "node_title": titles.get(f["node"]) if f["node"] else None,
            "title": r["title"], "severity": r["severity"], "why": r["why"].strip(),
            "fix": r["fix"], "detect": r["detect"], "owner": r["owner"],
            "scenarios": [{"id": s, "title": get_scenario(s)["title"]} for s in r["scenarios"] if get_scenario(s)],
        })
    return {
        "title": spec["title"],
        "domain": spec.get("domain", ""),
        "scenario": spec.get("scenario", "").strip(),
        "findings": detailed,
        "before_spec": before,
        "fixed_spec": fixed,
        "before_svg": render_arch(before),
        "after_svg": render_arch(fixed),
    }


def report_markdown(result: dict, before_svg_path: str | None = None, after_svg_path: str | None = None) -> str:
    lines = [f"# Architecture review: {result['title']}", ""]
    if result["scenario"]:
        lines += [f"**Scenario.** {result['scenario']}", ""]
    lines += ["## 1. Architecture as described, with failure points", ""]
    if before_svg_path:
        lines += [f"![As described]({before_svg_path})", ""]
    lines += ["## 2. Failure points and fixes", ""]
    for f in result["findings"]:
        where = f" ({f['node_title']})" if f["node_title"] else ""
        lines += [f"### {f['label']}. {f['title']}{where}", "",
                  f"- **Severity:** {f['severity']}",
                  f"- **Why it breaks:** {f['why']}",
                  "- **Fix:**"]
        lines += [f"    - {x}" for x in f["fix"]]
        lines += [f"- **Detect:** {f['detect']}",
                  f"- **Owner:** {f['owner']}",
                  "- **Deep dives:** " + ", ".join(f"{s['id']} *{s['title']}*" for s in f["scenarios"]), ""]
    lines += ["## 3. Fixed architecture", ""]
    if after_svg_path:
        lines += [f"![Fixed]({after_svg_path})", ""]
    lines += ["## 4. Summary", "", "| # | Failure point | Severity | Fix | Owner |", "| --- | --- | --- | --- | --- |"]
    for f in result["findings"]:
        lines.append(f"| {f['label']} | {f['title']} | {f['severity'].capitalize()} | {f['fix'][0]} | {f['owner']} |")
    lines.append("")
    return "\n".join(lines)
