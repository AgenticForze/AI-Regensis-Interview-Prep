// Port of src/antipatterns/review.py for the website. tests/test_review_parity.py
// runs every reference architecture through both and compares the results.
(function (root) {
  const NODE_TYPES = new Set([
    "channel", "agent", "router", "retriever", "knowledge", "vector_store", "tool_read",
    "tool_write", "tool_payment", "tool_provision", "tool_identity", "tool_fraud",
    "tool_notify", "tool_code", "system_of_record", "policy", "human_approval",
    "guardrail", "memory", "cache", "gateway", "observability", "eval", "audit",
    "queue", "external_agent", "spacer",
  ]);
  const PURPLE = new Set(["agent", "router"]);
  const NODE_KEYS = new Set(["id", "title", "sub", "type", "attrs", "kind", "span"]);
  const MAX_PER_LANE = 4;
  const INNER_W = 605, GAP_ARCH = 30, TITLE_PX = 7.3, SUB_PX = 6.0;
  const BEFORE_LEGEND = "Red numbered markers = failure points";
  const AFTER_LEGEND = "Teal = new or changed control";

  const clone = (o) => JSON.parse(JSON.stringify(o));
  const nodesOf = (spec) => {
    const out = [];
    spec.lanes.forEach((lane, li) => lane.nodes.forEach((n, ni) => out.push([li, ni, n])));
    return out;
  };
  const attr = (n, k) => {
    const v = (n.attrs || {})[k];
    return v === undefined ? null : v;
  };
  function match(n, cond) {
    if (!(cond.type || []).includes(n.type)) return false;
    for (const [k, v] of Object.entries(cond.attrs || {})) if (attr(n, k) !== v) return false;
    for (const [k, v] of Object.entries(cond.not || {})) if (attr(n, k) === v) return false;
    return true;
  }
  const first = (spec, types) => nodesOf(spec).find(([, , n]) => types.includes(n.type)) || null;

  function defaultKind(n) {
    if (n.type === "spacer") return "spacer";
    if (n.kind) return n.kind;
    return PURPLE.has(n.type) || (n.type || "").startsWith("tool_") ? "agent" : "neutral";
  }

  function labelProblems(title, sub, width) {
    const p = [];
    if (title.length * TITLE_PX + 16 > width) p.push(`title '${title}' too long for ${Math.round(width)}px box`);
    if (sub && sub.length * SUB_PX + 16 > width) p.push(`subtitle '${sub}' too long for ${Math.round(width)}px box`);
    return p;
  }

  function validateSpec(spec) {
    const errs = [];
    if (!spec || !Array.isArray(spec.lanes) || !spec.lanes.length) return ["spec has no lanes"];
    const ids = new Set();
    for (const lane of spec.lanes) {
      if (!lane.nodes || !lane.nodes.length) { errs.push(`lane '${lane.name}' has no nodes`); continue; }
      if (lane.nodes.length > MAX_PER_LANE) errs.push(`lane '${lane.name}' has more than ${MAX_PER_LANE} nodes; split it`);
      const total = lane.nodes.reduce((a, n) => a + (n.span || 1), 0);
      const usable = INNER_W - GAP_ARCH * (lane.nodes.length - 1);
      for (const n of lane.nodes) {
        if (ids.has(n.id)) errs.push(`duplicate node id '${n.id}'`);
        ids.add(n.id);
        const extra = Object.keys(n).filter((k) => !NODE_KEYS.has(k)).sort();
        if (extra.length) errs.push(`node '${n.id}': unexpected keys ${JSON.stringify(extra)} (quote labels that contain commas)`);
        if (!NODE_TYPES.has(n.type)) errs.push(`node '${n.id}': unknown type '${n.type}'`);
        if (n.type !== "spacer") {
          const w = (usable * (n.span || 1)) / total;
          labelProblems(n.title || "", n.sub || "", w).forEach((p) => errs.push(`node '${n.id}': ${p}`));
        }
      }
    }
    for (const e of spec.edges || []) for (const end of ["from", "to"]) if (!ids.has(e[end])) errs.push(`edge references unknown node '${e[end]}'`);
    if (spec.bus) for (const t of [spec.bus.from].concat(spec.bus.to || [])) if (!ids.has(t)) errs.push(`bus references unknown node '${t}'`);
    return errs;
  }

  function detect(spec, rules) {
    const found = [];
    const nodes = nodesOf(spec);
    rules.forEach((rule, ri) => {
      const w = rule.when;
      if (w.node) {
        for (const [li, ni, n] of nodes) if (match(n, w.node)) found.push([li, ni, ri, rule, n.id]);
      } else if (w.missing) {
        if (first(spec, w.missing)) return;
        if (w.requires && !nodes.some(([, , n]) => match(n, w.requires))) return;
        if (rule.scope === "component") {
          const hit = first(spec, [rule.marker_on || "agent"]);
          if (!hit) return;
          found.push([hit[0], hit[1], ri, rule, hit[2].id]);
        } else found.push([1e6, 0, ri, rule, null]);
      }
    });
    found.sort((a, b) => a[0] - b[0] || a[1] - b[1] || a[2] - b[2]);
    let comp = 0, plat = 0;
    return found.map(([, , , rule, nodeId]) => {
      const label = rule.scope === "component" ? String(++comp) : `P${++plat}`;
      return { label, rule: rule.id, node: nodeId, scope: rule.scope };
    });
  }

  const ORDER = ["Controls", "Platform controls"];
  const base = (name) => name.split(" (")[0];
  function laneIndex(spec, name) {
    let i = spec.lanes.findIndex((l) => l.name === name);
    if (i >= 0) return i;
    spec.lanes.push({ name, nodes: [] });
    if (ORDER.includes(name)) {
      const key = (l) => (ORDER.includes(base(l.name)) ? ORDER.indexOf(base(l.name)) : -1);
      spec.lanes.sort((a, b) => key(a) - key(b));
    }
    return spec.lanes.findIndex((l) => l.name === name);
  }

  function addNode(spec, laneName, node, after) {
    if (nodesOf(spec).some(([, , n]) => n.id === node.id)) return;
    const li = laneIndex(spec, laneName);
    const lane = spec.lanes[li];
    const ids = lane.nodes.map((n) => n.id);
    for (let i = 0; i < lane.nodes.length; i++) {
      const n = lane.nodes[i];
      if (n.kind === "spacer" || n.type === "spacer") {
        lane.nodes.splice(i, 1);
        const pos = ids.includes(after) ? ids.indexOf(after) + 1 : i;
        lane.nodes.splice(Math.min(pos, lane.nodes.length), 0, node);
        return;
      }
    }
    if (ids.includes(after) && lane.nodes.length < MAX_PER_LANE) {
      lane.nodes.splice(ids.indexOf(after) + 1, 0, node);
      return;
    }
    if (lane.nodes.length >= MAX_PER_LANE) {
      const b = base(lane.name);
      for (let k = 2; ; k++) {
        const name = `${b} (${k})`;
        const idx = spec.lanes.findIndex((l) => l.name === name);
        if (idx < 0) { spec.lanes.splice(li + k - 1, 0, { name, nodes: [node] }); return; }
        if (spec.lanes[idx].nodes.length < MAX_PER_LANE) { spec.lanes[idx].nodes.push(node); return; }
      }
    }
    lane.nodes.push(node);
  }

  function laneOf(spec, nodeId) {
    for (const lane of spec.lanes) if (lane.nodes.some((n) => n.id === nodeId)) return lane.name;
    return spec.lanes[spec.lanes.length - 1].name;
  }

  function fix(spec, findings, rules) {
    const fixed = clone(spec);
    const byRule = Object.fromEntries(rules.map((r) => [r.id, r]));
    const ag = first(fixed, ["agent"]);
    const agentId = ag ? ag[2].id : null;
    let byId = Object.fromEntries(nodesOf(fixed).map(([, , n]) => [n.id, n]));
    for (const n of Object.values(byId)) n.kind = defaultKind(n);
    for (const f of findings) {
      const patch = byRule[f.rule].patch || {};
      const node = f.node ? byId[f.node] : null;
      const resolve = (v) => {
        if (v === "$agent") return agentId;
        if (v === "$node") return f.node;
        if (v === "$agent_lane") return agentId ? laneOf(fixed, agentId) : "Controls";
        if (v === "$node_lane") return f.node ? laneOf(fixed, f.node) : "Controls";
        return v === undefined ? null : v;
      };
      if (patch.set && node) {
        const s = patch.set;
        node.attrs = Object.assign(node.attrs || {}, s.attrs || {});
        if ("title" in s) node.title = s.title;
        if ("sub" in s) {
          if (node._patched_sub) {
            const combo = `${node.sub} + ${s.sub}`;
            if (combo.length <= 20) node.sub = combo;
          } else {
            node.sub = s.sub;
            node._patched_sub = true;
          }
        }
        if (!PURPLE.has(node.type)) node.kind = "good";
      }
      if (patch.add_node) {
        const a = Object.assign({}, patch.add_node);
        const lane = resolve(a.lane);
        const after = resolve(a.after);
        delete a.lane;
        delete a.after;
        a.kind = "good";
        addNode(fixed, lane, a, after);
        byId = Object.fromEntries(nodesOf(fixed).map(([, , n]) => [n.id, n]));
      }
      if (patch.add_edge) {
        const e = {};
        for (const [k, v] of Object.entries(patch.add_edge)) e[k] = resolve(v);
        fixed.edges = fixed.edges || [];
        const dup = fixed.edges.some((x) => JSON.stringify(Object.entries(x).sort()) === JSON.stringify(Object.entries(e).sort()));
        if (e.from && e.to && !dup) fixed.edges.push(e);
      }
      if (patch.add_to_bus) {
        const nid = patch.add_to_bus;
        if (fixed.bus) { if (!fixed.bus.to.includes(nid)) fixed.bus.to.push(nid); }
        else if (agentId) (fixed.edges = fixed.edges || []).push({ from: agentId, to: nid });
      }
    }
    for (const n of Object.values(byId)) delete n._patched_sub;
    delete fixed.markers;
    fixed.legend = AFTER_LEGEND;
    return fixed;
  }

  function review(spec, rules, getScenario, render) {
    const errs = validateSpec(spec);
    if (errs.length) throw new Error("invalid architecture spec: " + errs.join("; "));
    const findings = detect(spec, rules);
    const byRule = Object.fromEntries(rules.map((r) => [r.id, r]));
    const before = clone(spec);
    for (const [, , n] of nodesOf(before)) n.kind = defaultKind(n);
    before.markers = findings.filter((f) => f.scope === "component").map((f) => ({ node: f.node, n: f.label }));
    before.legend = BEFORE_LEGEND;
    before.title = `${spec.title}: failure points`;
    const fixed = fix(spec, findings, rules);
    fixed.title = `${spec.title}: fixed architecture`;
    const titles = Object.fromEntries(nodesOf(spec).map(([, , n]) => [n.id, n.title]));
    const detailed = findings.map((f) => {
      const r = byRule[f.rule];
      return Object.assign({}, f, {
        node_title: f.node ? titles[f.node] : null,
        title: r.title, severity: r.severity, why: r.why.trim(), fix: r.fix,
        detect: r.detect, owner: r.owner,
        scenarios: r.scenarios.filter((s) => getScenario(s)).map((s) => ({ id: s, title: getScenario(s).title })),
      });
    });
    return {
      title: spec.title, domain: spec.domain || "", scenario: (spec.scenario || "").trim(),
      findings: detailed, before_spec: before, fixed_spec: fixed,
      before_svg: render.renderArch(before), after_svg: render.renderArch(fixed),
    };
  }

  const api = { review, detect, fix, validateSpec, NODE_TYPES: [...NODE_TYPES] };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.AAPReview = api;
})(typeof window !== "undefined" ? window : globalThis);
