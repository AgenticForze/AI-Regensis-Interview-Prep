"""SVG renderers shared by the site build, MCP server, agent and skill.

Two diagram kinds:

* ``render_fix(spec)``  - the per-scenario "anti-pattern vs fix" diagram: two
  dashed lanes, each a left-to-right flow of up to four boxes.
* ``render_arch(spec)`` - the swimlane architecture diagram used by
  Architecture Review: stacked lanes (channel, orchestration, tools, ...),
  straight arrows, an optional tool bus, and numbered failure markers.

Output is self-contained SVG: colours live in an embedded <style> with a
prefers-color-scheme dark variant, so files render correctly on GitHub, in the
website, and in chat. ``site/src/render.js`` is a line-for-line port; the
parity test in ``tests/test_render_parity.py`` keeps them identical.
"""
from __future__ import annotations

import math
from html import escape

W = 680
LANE_X = 20
LANE_W = 640
INNER_X = 35
INNER_W = 605
GAP_FIX = 24
GAP_ARCH = 30
FIX_LANE_H = 118
BOX_H = 56
LANE_H = 104
LANE_GAP = 40
TOP = 20

STYLE = (
    "<style>"
    ".ln{fill:none;stroke:#B4B2A9;stroke-width:.5;stroke-dasharray:4 4}"
    ".lt{font:500 14px system-ui,-apple-system,Segoe UI,sans-serif;fill:#2C2C2A}"
    ".bt{font:500 14px system-ui,-apple-system,Segoe UI,sans-serif}"
    ".bs{font:400 12px system-ui,-apple-system,Segoe UI,sans-serif}"
    ".cap{font:400 12px system-ui,-apple-system,Segoe UI,sans-serif;fill:#5F5E5A}"
    ".ar{stroke:#888780;stroke-width:1.5;fill:none}"
    ".k-bad rect{fill:#FCEBEB;stroke:#A32D2D}.k-bad .bt{fill:#791F1F}.k-bad .bs{fill:#A32D2D}"
    ".k-good rect{fill:#E1F5EE;stroke:#0F6E56}.k-good .bt{fill:#085041}.k-good .bs{fill:#0F6E56}"
    ".k-agent rect{fill:#EEEDFE;stroke:#534AB7}.k-agent .bt{fill:#3C3489}.k-agent .bs{fill:#534AB7}"
    ".k-neutral rect{fill:#F1EFE8;stroke:#5F5E5A}.k-neutral .bt{fill:#444441}.k-neutral .bs{fill:#5F5E5A}"
    ".mk circle{fill:#E24B4A;stroke:#A32D2D}.mk text{font:500 12px system-ui,sans-serif;fill:#FFFFFF}"
    "@media (prefers-color-scheme:dark){"
    ".ln{stroke:#5F5E5A}.lt{fill:#F1EFE8}.cap{fill:#B4B2A9}.ar{stroke:#B4B2A9}"
    ".k-bad rect{fill:#791F1F;stroke:#F09595}.k-bad .bt{fill:#FCEBEB}.k-bad .bs{fill:#F7C1C1}"
    ".k-good rect{fill:#085041;stroke:#5DCAA5}.k-good .bt{fill:#E1F5EE}.k-good .bs{fill:#9FE1CB}"
    ".k-agent rect{fill:#3C3489;stroke:#AFA9EC}.k-agent .bt{fill:#EEEDFE}.k-agent .bs{fill:#CECBF6}"
    ".k-neutral rect{fill:#444441;stroke:#B4B2A9}.k-neutral .bt{fill:#F1EFE8}.k-neutral .bs{fill:#D3D1C7}"
    "}"
    "</style>"
)

DEFS = (
    '<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" '
    'markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" '
    'stroke="#888780" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
    "</marker></defs>"
)

KINDS = {"bad", "good", "agent", "neutral"}

# Approximate rendered widths (px per char) used by the validator.
TITLE_PX = 7.3
SUB_PX = 6.0


def _e(s: str) -> str:
    return escape(str(s), quote=True)


def _f(v: float) -> str:
    """Format a coordinate identically in Python and JS (max 1 decimal)."""
    r = math.floor(v * 10 + 0.5) / 10
    return str(int(r)) if r == int(r) else f"{r:.1f}"


def _box(x: float, y: float, w: float, title: str, sub: str, kind: str) -> str:
    kind = kind if kind in KINDS else "neutral"
    cx = x + w / 2
    out = [f'<g class="k-{kind}">']
    out.append(f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{BOX_H}" rx="8" stroke-width=".5"/>')
    if sub:
        out.append(f'<text class="bt" x="{_f(cx)}" y="{_f(y + 18)}" text-anchor="middle" dominant-baseline="central">{_e(title)}</text>')
        out.append(f'<text class="bs" x="{_f(cx)}" y="{_f(y + 38)}" text-anchor="middle" dominant-baseline="central">{_e(sub)}</text>')
    else:
        out.append(f'<text class="bt" x="{_f(cx)}" y="{_f(y + 28)}" text-anchor="middle" dominant-baseline="central">{_e(title)}</text>')
    out.append("</g>")
    return "".join(out)


def _head(h: int, title: str, desc: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 {W} {h}" role="img">'
        f"<title>{_e(title)}</title><desc>{_e(desc)}</desc>{STYLE}{DEFS}"
    )


def _row_layout(n: int, spans: list[float] | None = None, gap: int = GAP_ARCH) -> list[tuple[float, float]]:
    spans = spans or [1.0] * n
    total = sum(spans)
    usable = INNER_W - gap * (n - 1)
    xs, x = [], float(INNER_X)
    for s in spans:
        w = usable * s / total
        xs.append((x, w))
        x += w + gap
    return xs


# ---------------------------------------------------------------- fix diagram
def render_fix(spec: dict) -> str:
    """spec = {title, bad_label, good_label, bad: [[t, s], ...], good: [[t, s], ...]}"""
    lanes = [
        (spec.get("bad_label") or "Anti-pattern", spec["bad"], "bad"),
        (spec.get("good_label") or "Fix", spec["good"], "good"),
    ]
    h = TOP + 2 * FIX_LANE_H + 20 + 20
    desc = "; ".join(
        f"{lbl}: " + " then ".join(f"{b[0]} ({b[1]})" if len(b) > 1 and b[1] else b[0] for b in boxes)
        for lbl, boxes, _ in lanes
    )
    out = [_head(h, spec.get("title", "Anti-pattern and fix"), desc)]
    for i, (label, boxes, kind) in enumerate(lanes):
        ly = TOP + i * (FIX_LANE_H + 20)
        lh = FIX_LANE_H
        out.append(f'<rect class="ln" x="{LANE_X}" y="{ly}" width="{LANE_W}" height="{lh}" rx="12"/>')
        out.append(f'<text class="lt" x="40" y="{ly + 24}">{_e(label)}</text>')
        by = ly + 42
        cols = _row_layout(len(boxes), gap=GAP_FIX)
        for j, (b, (x, w)) in enumerate(zip(boxes, cols)):
            out.append(_box(x, by, w, b[0], b[1] if len(b) > 1 else "", kind))
            if j < len(boxes) - 1:
                x2 = cols[j + 1][0]
                out.append(
                    f'<line class="ar" x1="{_f(x + w + 1)}" y1="{by + 28}" x2="{_f(x2 - 2)}" y2="{by + 28}" marker-end="url(#ah)"/>'
                )
    out.append("</svg>")
    return "".join(out)


# ---------------------------------------------------------- architecture diagram
def _lane_y(i: int) -> int:
    return TOP + i * (LANE_H + LANE_GAP)


def layout_arch(spec: dict) -> dict:
    """Return {node_id: (x, y, w, lane_index)} for an architecture spec."""
    pos = {}
    for li, lane in enumerate(spec["lanes"]):
        nodes = lane["nodes"]
        cols = _row_layout(len(nodes), [n.get("span", 1) for n in nodes])
        y = _lane_y(li) + 34
        for n, (x, w) in zip(nodes, cols):
            pos[n["id"]] = (x, y, w, li)
    return pos


def render_arch(spec: dict) -> str:
    """spec = {title, lanes: [{name, nodes: [{id, title, sub, kind, span}]}],
    edges: [{from, to, two_way}], bus: {from, to: [...]},
    markers: [{node, n}], legend}"""
    lanes = spec["lanes"]
    pos = layout_arch(spec)
    nodes = {n["id"]: n for lane in lanes for n in lane["nodes"]}
    h = _lane_y(len(lanes) - 1) + LANE_H + (48 if spec.get("legend") else 20)
    desc_parts = [f"{lane['name']}: " + ", ".join(n["title"] for n in lane["nodes"] if n.get("kind") != "spacer") for lane in lanes]
    if spec.get("markers"):
        desc_parts.append(
            "failure markers on " + ", ".join(f"{m['n']} {nodes[m['node']]['title']}" for m in spec["markers"] if m["node"] in nodes)
        )
    out = [_head(h, spec.get("title", "Architecture"), "; ".join(desc_parts))]

    for li, lane in enumerate(lanes):
        y = _lane_y(li)
        out.append(f'<rect class="ln" x="{LANE_X}" y="{y}" width="{LANE_W}" height="{LANE_H}" rx="12"/>')
        out.append(f'<text class="lt" x="40" y="{y + 22}">{_e(lane["name"])}</text>')

    bus = spec.get("bus")
    for e in spec.get("edges", []):
        if e["from"] in pos and e["to"] in pos:
            out.append(_edge(pos[e["from"]], pos[e["to"]], e.get("two_way", False)))
    if bus and bus["from"] in pos:
        out.append(_bus(pos[bus["from"]], [pos[t] for t in bus["to"] if t in pos]))

    for lane in lanes:
        for n in lane["nodes"]:
            if n.get("kind") == "spacer":
                continue
            x, y, w, _ = pos[n["id"]]
            out.append(_box(x, y, w, n["title"], n.get("sub", ""), n.get("kind", "neutral")))

    for m in spec.get("markers", []):
        if m["node"] not in pos:
            continue
        x, y, w, _ = pos[m["node"]]
        cx, cy = x + w - 4, y + 2
        out.append(
            f'<g class="mk"><circle cx="{_f(cx)}" cy="{_f(cy)}" r="11" stroke-width=".5"/>'
            f'<text x="{_f(cx)}" y="{_f(cy)}" text-anchor="middle" dominant-baseline="central">{_e(m["n"])}</text></g>'
        )
    if spec.get("legend"):
        out.append(f'<text class="cap" x="340" y="{h - 18}" text-anchor="middle">{_e(spec["legend"])}</text>')
    out.append("</svg>")
    return "".join(out)


def _edge(a, b, two_way: bool) -> str:
    ax, ay, aw, al = a
    bx, by, bw, bl = b
    start = ' marker-start="url(#ah)"' if two_way else ""
    end = ' marker-end="url(#ah)"'
    if al == bl:  # same lane: horizontal between facing edges
        if ax < bx:
            x1, x2 = ax + aw + 2, bx - 3
        else:
            x1, x2 = ax - 2, bx + bw + 3
        y = ay + BOX_H / 2
        return f'<line class="ar" x1="{_f(x1)}" y1="{_f(y)}" x2="{_f(x2)}" y2="{_f(y)}"{start}{end}/>'
    down = bl > al
    acx, bcx = ax + aw / 2, bx + bw / 2
    y1 = ay + BOX_H if down else ay
    y2 = by - 4 if down else by + BOX_H + 4
    lo, hi = max(ax, bx), min(ax + aw, bx + bw)
    if hi - lo >= 30:  # columns overlap: one straight vertical arrow
        x = (lo + hi) / 2
        return f'<line class="ar" x1="{_f(x)}" y1="{_f(y1)}" x2="{_f(x)}" y2="{_f(y2)}"{start}{end}/>'
    # L-route through the gap just below (or above) the source lane
    src_lane_y = _lane_y(al)
    mid = src_lane_y + LANE_H + LANE_GAP / 2 if down else src_lane_y - LANE_GAP / 2
    d = f"M{_f(acx)} {_f(y1)} L{_f(acx)} {_f(mid)} L{_f(bcx)} {_f(mid)} L{_f(bcx)} {_f(y2)}"
    return f'<path class="ar" d="{d}"{start}{end}/>'


def _bus(src, targets) -> str:
    sx, sy, sw, sl = src
    scx = sx + sw / 2
    if not targets:
        return ""
    tl = targets[0][3]
    bus_y = _lane_y(tl) - LANE_GAP / 2 + 4 if tl > sl else _lane_y(sl) - LANE_GAP / 2
    xs = [t[0] + t[2] / 2 for t in targets] + [scx]
    out = [f'<path class="ar" d="M{_f(scx)} {_f(sy + BOX_H)} L{_f(scx)} {_f(bus_y)}"/>']
    out.append(f'<path class="ar" d="M{_f(min(xs))} {_f(bus_y)} L{_f(max(xs))} {_f(bus_y)}"/>')
    for t in targets:
        tx = t[0] + t[2] / 2
        out.append(f'<line class="ar" x1="{_f(tx)}" y1="{_f(bus_y)}" x2="{_f(tx)}" y2="{_f(t[1] - 4)}" marker-end="url(#ah)"/>')
    return "".join(out)


def label_problems(title: str, sub: str, width: float) -> list[str]:
    """Return human-readable problems if a box label will overflow its box."""
    probs = []
    if len(title) * TITLE_PX + 16 > width:
        probs.append(f"title '{title}' too long for {width:.0f}px box")
    if sub and len(sub) * SUB_PX + 16 > width:
        probs.append(f"subtitle '{sub}' too long for {width:.0f}px box")
    return probs
