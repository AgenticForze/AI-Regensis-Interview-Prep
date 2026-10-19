// Line-for-line port of src/antipatterns/render.py. Keep the two in sync:
// tests/test_render_parity.py renders the same specs with both and diffs them.
(function (root) {
  const W = 680, LANE_X = 20, LANE_W = 640, INNER_X = 35, INNER_W = 605;
  const GAP_FIX = 24, GAP_ARCH = 30, FIX_LANE_H = 118;
  const BOX_H = 56, LANE_H = 104, LANE_GAP = 40, TOP = 20;

  const STYLE =
    "<style>" +
    ".ln{fill:#FAF9F5;stroke:#B4B2A9;stroke-width:.5;stroke-dasharray:4 4}" +
    ".lt{font:500 14px system-ui,-apple-system,Segoe UI,sans-serif;fill:#2C2C2A}" +
    ".bt{font:500 14px system-ui,-apple-system,Segoe UI,sans-serif}" +
    ".bs{font:400 12px system-ui,-apple-system,Segoe UI,sans-serif}" +
    ".lb{fill:#FAF9F5}" +
    ".cap{font:400 12px system-ui,-apple-system,Segoe UI,sans-serif;fill:#5F5E5A}" +
    ".ar{stroke:#888780;stroke-width:1.5;fill:none}" +
    ".k-bad rect{fill:#FCEBEB;stroke:#A32D2D}.k-bad .bt{fill:#791F1F}.k-bad .bs{fill:#A32D2D}" +
    ".k-good rect{fill:#E1F5EE;stroke:#0F6E56}.k-good .bt{fill:#085041}.k-good .bs{fill:#0F6E56}" +
    ".k-agent rect{fill:#EEEDFE;stroke:#534AB7}.k-agent .bt{fill:#3C3489}.k-agent .bs{fill:#534AB7}" +
    ".k-neutral rect{fill:#F1EFE8;stroke:#5F5E5A}.k-neutral .bt{fill:#444441}.k-neutral .bs{fill:#5F5E5A}" +
    ".mk circle{fill:#E24B4A;stroke:#A32D2D}.mk text{font:500 12px system-ui,sans-serif;fill:#FFFFFF}" +
    "@media (prefers-color-scheme:dark){" +
    ".ln{fill:#262624;stroke:#5F5E5A}.lt{fill:#F1EFE8}.lb{fill:#262624}.cap{fill:#B4B2A9}.ar{stroke:#B4B2A9}" +
    ".k-bad rect{fill:#791F1F;stroke:#F09595}.k-bad .bt{fill:#FCEBEB}.k-bad .bs{fill:#F7C1C1}" +
    ".k-good rect{fill:#085041;stroke:#5DCAA5}.k-good .bt{fill:#E1F5EE}.k-good .bs{fill:#9FE1CB}" +
    ".k-agent rect{fill:#3C3489;stroke:#AFA9EC}.k-agent .bt{fill:#EEEDFE}.k-agent .bs{fill:#CECBF6}" +
    ".k-neutral rect{fill:#444441;stroke:#B4B2A9}.k-neutral .bt{fill:#F1EFE8}.k-neutral .bs{fill:#D3D1C7}" +
    "}" +
    "</style>";

  const DEFS =
    '<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" ' +
    'markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" ' +
    'stroke="#888780" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>' +
    "</marker></defs>";

  const KINDS = new Set(["bad", "good", "agent", "neutral"]);

  function e(s) {
    return String(s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#x27;");
  }

  function f(v) {
    const r = Math.floor(v * 10 + 0.5) / 10;
    return Number.isInteger(r) ? String(r) : r.toFixed(1);
  }

  function box(x, y, w, title, sub, kind) {
    kind = KINDS.has(kind) ? kind : "neutral";
    const cx = x + w / 2;
    let out = `<g class="k-${kind}">`;
    out += `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${BOX_H}" rx="8" stroke-width=".5"/>`;
    if (sub) {
      out += `<text class="bt" x="${f(cx)}" y="${f(y + 18)}" text-anchor="middle" dominant-baseline="central">${e(title)}</text>`;
      out += `<text class="bs" x="${f(cx)}" y="${f(y + 38)}" text-anchor="middle" dominant-baseline="central">${e(sub)}</text>`;
    } else {
      out += `<text class="bt" x="${f(cx)}" y="${f(y + 28)}" text-anchor="middle" dominant-baseline="central">${e(title)}</text>`;
    }
    return out + "</g>";
  }

  function head(h, title, desc) {
    return (
      `<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 ${W} ${h}" role="img">` +
      `<title>${e(title)}</title><desc>${e(desc)}</desc>${STYLE}${DEFS}`
    );
  }

  function rowLayout(n, spans, gap) {
    spans = spans || Array(n).fill(1);
    gap = gap === undefined ? GAP_ARCH : gap;
    const total = spans.reduce((a, b) => a + b, 0);
    const usable = INNER_W - gap * (n - 1);
    const xs = [];
    let x = INNER_X;
    for (const s of spans) {
      const w = (usable * s) / total;
      xs.push([x, w]);
      x += w + gap;
    }
    return xs;
  }

  function renderFix(spec) {
    const lanes = [
      [spec.bad_label || "Anti-pattern", spec.bad, "bad"],
      [spec.good_label || "Fix", spec.good, "good"],
    ];
    const h = TOP + 2 * FIX_LANE_H + 20 + 20;
    const desc = lanes
      .map(([lbl, boxes]) => `${lbl}: ` + boxes.map((b) => (b.length > 1 && b[1] ? `${b[0]} (${b[1]})` : b[0])).join(" then "))
      .join("; ");
    let out = head(h, spec.title || "Anti-pattern and fix", desc);
    lanes.forEach(([label, boxes, kind], i) => {
      const ly = TOP + i * (FIX_LANE_H + 20);
      out += `<rect class="ln" x="${LANE_X}" y="${ly}" width="${LANE_W}" height="${FIX_LANE_H}" rx="12"/>`;
      out += `<text class="lt" x="40" y="${ly + 24}">${e(label)}</text>`;
      const by = ly + 42;
      const cols = rowLayout(boxes.length, null, GAP_FIX);
      boxes.forEach((b, j) => {
        const [x, w] = cols[j];
        out += box(x, by, w, b[0], b.length > 1 ? b[1] : "", kind);
        if (j < boxes.length - 1) {
          const x2 = cols[j + 1][0];
          out += `<line class="ar" x1="${f(x + w + 1)}" y1="${by + 28}" x2="${f(x2 - 2)}" y2="${by + 28}" marker-end="url(#ah)"/>`;
        }
      });
    });
    return out + "</svg>";
  }

  function laneY(i) {
    return TOP + i * (LANE_H + LANE_GAP);
  }

  function layoutArch(spec) {
    const pos = {};
    spec.lanes.forEach((lane, li) => {
      const cols = rowLayout(lane.nodes.length, lane.nodes.map((n) => n.span || 1));
      const y = laneY(li) + 34;
      lane.nodes.forEach((n, k) => {
        pos[n.id] = [cols[k][0], y, cols[k][1], li];
      });
    });
    return pos;
  }

  function renderArch(spec) {
    const lanes = spec.lanes;
    const pos = layoutArch(spec);
    const nodes = {};
    lanes.forEach((l) => l.nodes.forEach((n) => (nodes[n.id] = n)));
    const h = laneY(lanes.length - 1) + LANE_H + (spec.legend ? 48 : 20);
    const descParts = lanes.map(
      (l) => `${l.name}: ` + l.nodes.filter((n) => !isSpacer(n)).map((n) => n.title).join(", ")
    );
    if (spec.markers && spec.markers.length) {
      descParts.push(
        "failure markers on " +
          spec.markers.filter((m) => m.node in nodes).map((m) => `${m.n} ${nodes[m.node].title}`).join(", ")
      );
    }
    let out = head(h, spec.title || "Architecture", descParts.join("; "));
    lanes.forEach((lane, li) => {
      out += `<rect class="ln" x="${LANE_X}" y="${laneY(li)}" width="${LANE_W}" height="${LANE_H}" rx="12"/>`;
    });
    const bus = spec.bus;
    for (const ed of spec.edges || []) {
      if (!(ed.from in pos && ed.to in pos)) continue;
      const a = pos[ed.from], b = pos[ed.to];
      const blocked = a[3] === b[3] && Object.keys(pos).some((nid) => {
        if (nid === ed.from || nid === ed.to || isSpacer(nodes[nid])) return false;
        const o = pos[nid];
        return o[3] === a[3] && Math.min(a[0], b[0]) < o[0] && o[0] < Math.max(a[0], b[0]);
      });
      out += edge(a, b, !!ed.two_way, blocked);
    }
    if (bus && bus.from in pos) out += busPath(pos[bus.from], bus.to.filter((t) => t in pos).map((t) => pos[t]));
    lanes.forEach((lane, li) => {
      const tw = lane.name.length * 7.6 + 12;
      out += `<rect class="lb" x="34" y="${laneY(li) + 10}" width="${f(tw)}" height="16" rx="3"/>`;
      out += `<text class="lt" x="40" y="${laneY(li) + 22}">${e(lane.name)}</text>`;
    });
    lanes.forEach((lane) =>
      lane.nodes.forEach((n) => {
        if (isSpacer(n)) return;
        const [x, y, w] = pos[n.id];
        out += box(x, y, w, n.title, n.sub || "", n.kind || "neutral");
      })
    );
    const total = {};
    for (const m of spec.markers || []) total[m.node] = (total[m.node] || 0) + 1;
    const seen = {};
    for (const m of spec.markers || []) {
      if (!(m.node in pos)) continue;
      const [x, y, w] = pos[m.node];
      const k = seen[m.node] || 0;
      seen[m.node] = k + 1;
      const cx = x + w - 4 - 26 * (total[m.node] - 1 - k), cy = y - 3;
      out +=
        `<g class="mk"><circle cx="${f(cx)}" cy="${f(cy)}" r="11" stroke-width=".5"/>` +
        `<text x="${f(cx)}" y="${f(cy)}" text-anchor="middle" dominant-baseline="central">${e(m.n)}</text></g>`;
    }
    if (spec.legend) out += `<text class="cap" x="340" y="${h - 18}" text-anchor="middle">${e(spec.legend)}</text>`;
    return out + "</svg>";
  }

  function isSpacer(n) {
    return n.kind === "spacer" || n.type === "spacer";
  }

  function edge(a, b, twoWay, blocked) {
    const [ax, ay, aw, al] = a;
    const [bx, by, bw, bl] = b;
    const start = twoWay ? ' marker-start="url(#ah)"' : "";
    const end = ' marker-end="url(#ah)"';
    if (al === bl && blocked) {
      const low = ay + BOX_H + 7;
      const x1 = ax + aw * 0.75, x2 = bx > ax ? bx + bw * 0.25 : bx + bw * 0.75;
      const d = `M${f(x1)} ${f(ay + BOX_H)} L${f(x1)} ${f(low)} L${f(x2)} ${f(low)} L${f(x2)} ${f(ay + BOX_H + 3)}`;
      return `<path class="ar" d="${d}"${start}${end}/>`;
    }
    if (al === bl) {
      let x1, x2;
      if (ax < bx) { x1 = ax + aw + 2; x2 = bx - 3; } else { x1 = ax - 2; x2 = bx + bw + 3; }
      const y = ay + BOX_H / 2;
      return `<line class="ar" x1="${f(x1)}" y1="${f(y)}" x2="${f(x2)}" y2="${f(y)}"${start}${end}/>`;
    }
    const down = bl > al;
    const acx = ax + aw / 2, bcx = bx + bw / 2;
    const y1 = down ? ay + BOX_H : ay;
    const y2 = down ? by - 4 : by + BOX_H + 4;
    const lo = Math.max(ax, bx), hi = Math.min(ax + aw, bx + bw);
    if (hi - lo >= 30) {
      const x = (lo + hi) / 2;
      return `<line class="ar" x1="${f(x)}" y1="${f(y1)}" x2="${f(x)}" y2="${f(y2)}"${start}${end}/>`;
    }
    const srcLaneY = laneY(al);
    const mid = down ? srcLaneY + LANE_H + LANE_GAP / 2 : srcLaneY - LANE_GAP / 2;
    const d = `M${f(acx)} ${f(y1)} L${f(acx)} ${f(mid)} L${f(bcx)} ${f(mid)} L${f(bcx)} ${f(y2)}`;
    return `<path class="ar" d="${d}"${start}${end}/>`;
  }

  function busPath(src, targets) {
    const [sx, sy, sw, sl] = src;
    const scx = sx + sw / 2;
    if (!targets.length) return "";
    const tl = targets[0][3];
    const busY = tl > sl ? laneY(tl) - LANE_GAP / 2 + 4 : laneY(sl) - LANE_GAP / 2;
    const xs = targets.map((t) => t[0] + t[2] / 2).concat([scx]);
    let out = `<path class="ar" d="M${f(scx)} ${f(sy + BOX_H)} L${f(scx)} ${f(busY)}"/>`;
    out += `<path class="ar" d="M${f(Math.min(...xs))} ${f(busY)} L${f(Math.max(...xs))} ${f(busY)}"/>`;
    for (const t of targets) {
      const tx = t[0] + t[2] / 2;
      out += `<line class="ar" x1="${f(tx)}" y1="${f(busY)}" x2="${f(tx)}" y2="${f(t[1] - 4)}" marker-end="url(#ah)"/>`;
    }
    return out;
  }

  const api = { renderFix, renderArch, layoutArch };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.AAPRender = api;
})(typeof window !== "undefined" ? window : globalThis);
