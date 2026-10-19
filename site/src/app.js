(function () {
  const D = window.AAP_DATA;
  const R = window.AAPRender;
  const RV = window.AAPReview;
  const $ = (s, el = document) => el.querySelector(s);
  const main = $("#main");
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const all = [];
  const byId = {};
  D.topics.forEach((t) => t.scenarios.forEach((s) => { s.topic = t.id; s.topic_title = t.title; all.push(s); byId[s.id] = s; }));
  const topicById = Object.fromEntries(D.topics.map((t) => [t.id, t]));
  const RUBRIC = [
    ["names_antipattern", "Named the anti-pattern or root cause, not just the symptom"],
    ["explains_mechanism", "Explained the mechanism: why it breaks"],
    ["concrete_fix", "Gave a concrete fix in the right layer"],
    ["detection", "Said how to detect or measure it"],
    ["tradeoff", "Named a trade-off or cost of the fix"],
  ];

  // ---------- per-viewer conveniences (safe if storage is unavailable)
  const store = {
    get(k, d) { try { const v = localStorage.getItem("aap." + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem("aap." + k, JSON.stringify(v)); } catch (e) { /* storage blocked */ } },
  };
  let domain = store.get("domain", "all");
  let practice = store.get("practice", false);
  let progress = store.get("progress", {});
  let query = "";

  const svg = (s) => s.replace(/<style>[\s\S]*?<\/style>/, "");
  const chip = (d) => `<span class="chip ${d}">${d === "telco" ? "Telco BSS" : "FinTech"}</span>`;
  const sev = (v) => `<span class="sev ${v}">${esc(v)}</span>`;
  const inDomain = (s) => domain === "all" || s.domain === domain;

  // ---------- rail
  function renderRail(current) {
    const links = D.topics.map((t) => {
      const done = t.scenarios.filter((s) => progress[s.id] != null).length;
      return `<a href="#t-${t.id}" ${current === t.id ? 'aria-current="page"' : ""}><span class="n">${String(t.order).padStart(2, "0")}</span><span>${esc(t.title)}</span><span class="done">${done ? done + "/20" : ""}</span></a>`;
    }).join("");
    $("#rail").innerHTML = `<h4>Start</h4><a href="#home" ${current === "home" ? 'aria-current="page"' : ""}><span class="n">00</span><span>Overview</span><span></span></a>
      <a href="#review" ${current === "review" ? 'aria-current="page"' : ""}><span class="n">AR</span><span>Architecture Review</span><span></span></a>
      <h4>Topics</h4>${links}`;
    const sel = $("#topic-select");
    sel.innerHTML = `<option value="home">Overview</option><option value="review">Architecture Review</option>` +
      D.topics.map((t) => `<option value="t-${t.id}">${t.order}. ${esc(t.title)}</option>`).join("");
    sel.value = current === "home" || current === "review" ? current : current ? `t-${current}` : "home";
  }

  // ---------- views
  function home() {
    renderRail("home");
    const telco = all.filter((s) => s.domain === "telco").length;
    const answered = Object.keys(progress).length;
    const avg = answered ? (Object.values(progress).reduce((a, b) => a + b, 0) / answered).toFixed(1) : null;
    main.innerHTML = `
      <h1>Agentic AI failures in production, from Telco BSS and FinTech</h1>
      <p class="lead">Each scenario is a real-world failure an interviewer can describe to you: a roaming tariff misquoted, a SIM swap gone wrong, a wire sent twice. You get the mechanism, an analogy, where and how to fix it, how to detect it, the trade-off, and a one-line answer that signals seniority.</p>
      <div class="facts"><span><b>${D.topics.length}</b> topics</span><span><b>${all.length}</b> scenarios</span><span><b>${telco}</b> Telco BSS</span><span><b>${all.length - telco}</b> FinTech</span><span><b>${D.rules.length}</b> review rules</span><span><b>${D.architectures.length}</b> reference architectures</span>${avg ? `<span>practised <b>${answered}</b>, avg <b>${avg}</b>/5</span>` : ""}</div>
      <section><h2>How to answer any scenario</h2>
        <div class="tbl-wrap"><table><thead><tr><th>Beat</th><th>What you say</th><th>Example (rag-01)</th></tr></thead><tbody>
          <tr><td>Symptom</td><td>What the team sees in production</td><td>Roaming answers wrong, bill disputes rising</td></tr>
          <tr><td>Anti-pattern</td><td>The design mistake behind it</td><td>Fixed-size chunking splits the tariff table</td></tr>
          <tr><td>Why it breaks</td><td>The mechanism, in the scenario's terms</td><td>The chunk has rates but no plan names, so the model borrows a neighbouring column</td></tr>
          <tr><td>Fix</td><td>A concrete change in the right layer</td><td>Prices from the TMF620 catalog as a tool; row-level chunks with context headers</td></tr>
          <tr><td>Interview line</td><td>One sentence that signals seniority</td><td>If the BSS holds the fact, don't retrieve it from a PDF.</td></tr>
        </tbody></table></div>
        <p class="tip">Turn on <b>Practice</b> on any scenario to hide the answer, try it yourself, then grade yourself on the same five criteria the coach agent uses.</p>
      </section>
      <section><h2>Topics</h2><div class="topics">${D.topics.map((t) => {
        const tc = t.scenarios.filter((s) => s.domain === "telco").length;
        return `<a class="tcard" href="#t-${t.id}"><div class="row"><h3>${esc(t.title)}</h3><span class="mono muted">${String(t.order).padStart(2, "0")}</span></div><p>${esc(t.summary)}</p><div class="row"><span class="mono muted" style="font-size:.76rem">${tc} telco · ${20 - tc} fintech</span></div></a>`;
      }).join("")}</div></section>
      <section><h2>Architecture Review</h2><p class="tip">Describe or pick an agentic system and get numbered failure points, fixes linked to the scenarios, and before/after swimlane diagrams. <a href="#review">Open Architecture Review</a>.</p></section>`;
  }

  function listRows(items) {
    if (!items.length) return `<p class="muted">No scenarios match this filter.</p>`;
    return `<div class="list">${items.map((s) => `<a class="item" href="#s-${s.id}"><span class="id">${s.id}</span><span>${esc(s.title)}</span><span class="meta">${chip(s.domain)}${sev(s.severity)}<span class="tick">${progress[s.id] != null ? progress[s.id] + "/5" : ""}</span></span></a>`).join("")}</div>`;
  }

  function topic(id) {
    const t = topicById[id];
    if (!t) return home();
    renderRail(id);
    main.innerHTML = `<div class="crumbs"><a href="#home">Overview</a><span>/</span><span>${String(t.order).padStart(2, "0")}</span></div>
      <div class="shead"><h1>${esc(t.title)}</h1><p class="lead">${esc(t.summary)}</p></div>
      <section>${listRows(t.scenarios.filter(inDomain))}</section>`;
  }

  function searchView() {
    renderRail(null);
    const q = query.toLowerCase().split(/\s+/).filter(Boolean);
    const scored = all.filter(inDomain).map((s) => {
      const title = s.title.toLowerCase();
      const body = [s.scenario, s.root_cause, s.fix.join(" "), (s.tags || []).join(" "), s.id].join(" ").toLowerCase();
      const score = q.reduce((a, w) => a + (title.includes(w) ? 3 : 0) + (body.includes(w) ? 1 : 0), 0);
      const allHit = q.every((w) => title.includes(w) || body.includes(w));
      return [allHit ? score : 0, s];
    }).filter(([sc]) => sc > 0).sort((a, b) => b[0] - a[0]).map(([, s]) => s);
    main.innerHTML = `<h1>Search: ${esc(query)}</h1><p class="lead">${scored.length} scenario${scored.length === 1 ? "" : "s"}</p><section>${listRows(scored.slice(0, 60))}</section>`;
  }

  function scenario(id) {
    const s = byId[id];
    if (!s) return home();
    const t = topicById[s.topic];
    renderRail(s.topic);
    const i = t.scenarios.indexOf(s);
    const prev = t.scenarios[i - 1], next = t.scenarios[i + 1];
    const answerHidden = practice && !s._revealed;
    const answer = `
      <div class="block"><h3>Analogy</h3><p class="analogy">${esc(s.analogy)}</p></div>
      <div class="dg" role="figure" aria-label="Anti-pattern and fix diagram">${svg(R.renderFix(Object.assign({}, s.diagram, { title: s.title })))}</div>
      <div class="block"><h3>What goes wrong technically</h3><ol>${s.breaks.map((b) => `<li>${esc(b)}</li>`).join("")}</ol></div>
      <div class="block"><h3>Root cause</h3><p>${esc(s.root_cause)}</p></div>
      <div class="block"><h3>Where to fix it</h3><p>${esc(s.where)}</p></div>
      <div class="block"><h3>How to fix it</h3><ul>${s.fix.map((f) => `<li>${esc(f)}</li>`).join("")}</ul>${s.code ? `<pre><code>${esc(s.code.src)}</code></pre>` : ""}</div>
      <div class="block"><h3>How to detect it</h3><ul>${s.detect.map((f) => `<li>${esc(f)}</li>`).join("")}</ul></div>
      <div class="block"><h3>Trade-off</h3><p>${esc(s.tradeoff)}</p></div>
      <div class="block"><h3>${s.domain === "telco" ? "FinTech" : "Telco"} version</h3><p>${esc(s.variant)}</p></div>
      <div class="line"><span>Interview line</span>${esc(s.line)}</div>
      ${practice ? rubricBox(s) : ""}
      ${s.related && s.related.length ? `<div class="block"><h3>Related</h3><div class="related">${s.related.filter((r) => byId[r]).map((r) => `<a href="#s-${r}" title="${esc(byId[r].title)}">${r}</a>`).join("")}</div></div>` : ""}`;
    main.innerHTML = `<div class="crumbs"><a href="#home">Overview</a><span>/</span><a href="#t-${t.id}">${esc(t.title)}</a><span>/</span><span>${s.id}</span></div>
      <div class="shead"><h1>${esc(s.title)}</h1>
        <div class="meta">${chip(s.domain)}${sev(s.severity)}<span class="mono muted" style="font-size:.8rem">${(s.tags || []).map(esc).join(" · ")}</span>
          <label class="practice"><input type="checkbox" id="practice-toggle" ${practice ? "checked" : ""}> Practice: hide the answer</label></div></div>
      <div class="block"><h3>Scenario</h3><p>${esc(s.scenario)}</p></div>
      ${answerHidden ? `<div class="reveal"><b>Your turn.</b><span class="muted">What is going wrong here, why, and how would you fix and detect it in production? Answer out loud or in notes, then reveal.</span><button class="btn" id="reveal">Reveal answer</button></div>` : answer}
      <div class="pager">${prev ? `<a href="#s-${prev.id}">← ${prev.id} ${esc(prev.title)}</a>` : "<span></span>"}${next ? `<a href="#s-${next.id}" style="text-align:right">${next.id} ${esc(next.title)} →</a>` : ""}</div>`;
    $("#practice-toggle").addEventListener("change", (e) => { practice = e.target.checked; store.set("practice", practice); s._revealed = false; scenario(id); });
    const rv = $("#reveal");
    if (rv) rv.addEventListener("click", () => { s._revealed = true; scenario(id); });
    const form = $("#rubric");
    if (form) form.addEventListener("change", () => {
      const score = [...form.querySelectorAll("input:checked")].length;
      progress[s.id] = score; store.set("progress", progress);
      $("#rubric-score").textContent = `${score}/5 saved`;
      renderRail(s.topic);
    });
    window.scrollTo(0, 0);
  }

  function rubricBox(s) {
    return `<form class="rubric" id="rubric" onsubmit="return false"><b>Grade yourself</b>
      ${RUBRIC.map(([k, label], i) => `<label for="rb-${k}"><input type="checkbox" id="rb-${k}" name="${k}"> ${label}</label>`).join("")}
      <span class="score" id="rubric-score">${progress[s.id] != null ? progress[s.id] + "/5 saved" : "Tick what your answer covered"}</span></form>`;
  }

  // ---------- architecture review
  let currentArch = null;
  function reviewView(archId) {
    renderRail("review");
    const arch = D.architectures.find((a) => a.id === archId) || D.architectures.find((a) => a.id === "telco-sim-swap-agent");
    currentArch = arch;
    const groups = ["telco", "fintech"].map((d) => `<h4 class="mono muted" style="margin:8px 0 2px;font-size:.72rem">${d === "telco" ? "TELCO BSS" : "FINTECH"}</h4>` +
      D.architectures.filter((a) => a.domain === d).map((a) => `<button type="button" data-arch="${a.id}" aria-pressed="${a.id === arch.id}"><span>${esc(a.title)}</span><small>${esc(a.summary)}</small></button>`).join("")).join("");
    main.innerHTML = `<div class="crumbs"><a href="#home">Overview</a><span>/</span><span>Architecture Review</span></div>
      <div class="shead"><h1>Architecture Review</h1><p class="lead">Pick a reference design or edit the spec, then run the review. The same rule engine runs here, in the skill and in the agent: numbered failure points, fixes linked to scenarios, and a fixed design.</p></div>
      <div class="review-grid">
        <div class="refs">${groups}</div>
        <div style="display:grid;gap:10px;min-width:0;align-content:start">
          <label for="spec" class="mono muted" style="font-size:.78rem">Architecture spec (YAML or JSON). <a href="https://github.com/AgenticForze/AI-Regensis-Interview-Prep/blob/main/docs/architecture-spec.md">Spec format</a></label>
          <textarea id="spec" spellcheck="false">${esc(arch.yaml)}</textarea>
          <div class="copyrow"><button class="btn" id="run">Run review</button><button class="btn ghost" id="copy-prompt" type="button">Copy a prompt to turn your own scenario into a spec</button><span id="copy-note" class="muted" style="font-size:.82rem"></span></div>
          <div id="spec-err" hidden></div>
        </div>
      </div>
      <div id="result"></div>`;
    main.querySelectorAll("[data-arch]").forEach((b) => b.addEventListener("click", () => { location.hash = "review-" + b.dataset.arch; }));
    $("#run").addEventListener("click", runReview);
    $("#copy-prompt").addEventListener("click", copyPrompt);
    runReview();
  }

  function parseSpec(text) {
    const t = text.trim();
    if (t.startsWith("{")) return JSON.parse(t);
    if (!window.jsyaml) throw new Error("The YAML parser didn't load. Paste the spec as JSON instead.");
    return window.jsyaml.load(t);
  }

  function runReview() {
    const err = $("#spec-err");
    err.hidden = true;
    let res;
    try {
      res = RV.review(parseSpec($("#spec").value), D.rules, (id) => byId[id] || null, R);
    } catch (e) {
      err.className = "err";
      err.textContent = "Couldn't review this spec. " + e.message;
      err.hidden = false;
      $("#result").innerHTML = "";
      return;
    }
    const comp = res.findings.filter((f) => f.scope === "component");
    const plat = res.findings.filter((f) => f.scope === "platform");
    const card = (f) => `<div class="fcard"><div class="top"><span class="badge ${f.scope === "platform" ? "p" : ""}">${f.label}</span><h3 style="flex:1;min-width:0">${esc(f.title)}${f.node_title ? ` <span class="muted" style="font-weight:400">(${esc(f.node_title)})</span>` : ""}</h3>${sev(f.severity)}</div>
      <p><span class="k">Why it breaks</span><br>${esc(f.why)}</p>
      <div><span class="k">Fix</span><ul>${f.fix.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>
      <p><span class="k">Detect</span><br>${esc(f.detect)}</p>
      <p><span class="k">Owner</span> ${esc(f.owner)} &nbsp; <span class="k">Deep dives</span> ${f.scenarios.map((s) => `<a class="mono" href="#s-${s.id}" title="${esc(s.title)}">${s.id}</a>`).join(", ")}</p></div>`;
    $("#result").innerHTML = `
      ${res.scenario ? `<section><h2>Scenario</h2><p class="tip" style="color:var(--ink)">${esc(res.scenario)}</p></section>` : ""}
      <section><h2>1. As described, with failure points</h2><div class="dg">${svg(res.before_svg)}</div></section>
      <section><h2>2. Failure points and fixes</h2><div class="findings">${comp.map(card).join("") || '<p class="muted">No component failure points found.</p>'}</div></section>
      ${plat.length ? `<section><h2>Platform gaps</h2><div class="findings">${plat.map(card).join("")}</div></section>` : ""}
      <section><h2>3. Fixed architecture</h2><div class="dg">${svg(res.after_svg)}</div></section>
      <section><h2>4. Summary</h2><div class="tbl-wrap"><table><thead><tr><th>#</th><th>Failure point</th><th>Severity</th><th>Fix</th><th>Owner</th></tr></thead><tbody>
        ${res.findings.map((f) => `<tr><td class="mono">${f.label}</td><td>${esc(f.title)}</td><td>${sev(f.severity)}</td><td>${esc(f.fix[0])}</td><td>${esc(f.owner)}</td></tr>`).join("")}</tbody></table></div></section>`;
  }

  function copyPrompt() {
    const text = "Using the agentic-ai-coach skill, run /review-architecture on this system:\n\n<describe your agent: channels, what it decides, which tools it calls, which systems it changes, and the controls you already have>";
    const note = $("#copy-note");
    const done = () => { note.textContent = "Copied. Paste it into Claude with the skill installed."; };
    try {
      navigator.clipboard.writeText(text).then(done, () => { note.textContent = text; });
    } catch (e) { note.textContent = text; }
  }

  // ---------- quiz
  function quiz() {
    const pool = all.filter(inDomain);
    const fresh = pool.filter((s) => progress[s.id] == null);
    const pick = (fresh.length ? fresh : pool)[Math.floor(Math.random() * (fresh.length || pool.length))];
    practice = true; store.set("practice", true);
    pick._revealed = false;
    if (location.hash === "#s-" + pick.id) scenario(pick.id); else location.hash = "s-" + pick.id;
  }

  // ---------- router
  function route() {
    const h = location.hash.replace(/^#/, "");
    if (query) return searchView();
    if (h.startsWith("t-")) return topic(h.slice(2));
    if (h.startsWith("s-")) return scenario(h.slice(2));
    if (h === "review") return reviewView(null);
    if (h.startsWith("review-")) return reviewView(h.slice(7));
    return home();
  }

  function initBar() {
    document.querySelectorAll("#domain button").forEach((b) => {
      b.setAttribute("aria-pressed", String(b.dataset.d === domain));
      b.addEventListener("click", () => {
        domain = b.dataset.d; store.set("domain", domain);
        document.querySelectorAll("#domain button").forEach((x) => x.setAttribute("aria-pressed", String(x.dataset.d === domain)));
        route();
      });
    });
    const q = $("#q");
    q.addEventListener("input", () => { query = q.value.trim(); route(); });
    $("#quiz").addEventListener("click", () => { query = ""; q.value = ""; quiz(); });
    $("#topic-select").addEventListener("change", (e) => { query = ""; q.value = ""; location.hash = e.target.value; });
  }

  initBar();
  window.addEventListener("hashchange", () => { query = ""; $("#q").value = ""; route(); });
  route();
})();
