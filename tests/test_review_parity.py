"""The Python and JavaScript review engines must agree on every reference architecture."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from antipatterns.catalog import all_scenarios
from antipatterns.review import list_architectures, load_architecture, load_rules, review

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_review_parity(tmp_path):
    specs = {a["id"]: load_architecture(a["id"]) for a in list_architectures()}
    payload = {
        "rules": load_rules(),
        "titles": {s["id"]: s["title"] for s in all_scenarios()},
        "specs": specs,
    }
    script = f"""
const render = require({json.dumps(str(ROOT / 'site/src/render.js'))});
const rv = require({json.dumps(str(ROOT / 'site/src/review.js'))});
const p = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const get = (id) => (p.titles[id] ? {{ title: p.titles[id] }} : null);
const out = {{}};
for (const [id, spec] of Object.entries(p.specs)) out[id] = rv.review(spec, p.rules, get, render);
process.stdout.write(JSON.stringify(out));
"""
    res = subprocess.run(["node", "-e", script], input=json.dumps(payload), capture_output=True, text=True, check=True)
    js = json.loads(res.stdout)
    for arch_id, spec in specs.items():
        py = json.loads(json.dumps(review(spec)))
        assert js[arch_id]["findings"] == py["findings"], arch_id
        assert js[arch_id]["fixed_spec"] == py["fixed_spec"], arch_id
        assert js[arch_id]["before_svg"] == py["before_svg"], arch_id
        assert js[arch_id]["after_svg"] == py["after_svg"], arch_id


def test_fixed_designs_pass_review():
    from antipatterns.review import detect
    for a in list_architectures():
        fixed = review(load_architecture(a["id"]))["fixed_spec"]
        assert detect(fixed) == [], a["id"]


def test_sim_swap_matches_reference_numbering():
    r = review(load_architecture("telco-sim-swap-agent"))
    comp = [(f["label"], f["node"]) for f in r["findings"] if f["scope"] == "component"]
    assert comp == [("1", "agent"), ("2", "verify"), ("3", "fraud"), ("4", "swap"), ("5", "swap"), ("6", "notify")]
