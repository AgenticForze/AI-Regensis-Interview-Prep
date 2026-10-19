"""The Python and JavaScript renderers must emit byte-identical SVG."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from antipatterns.render import render_arch, render_fix

ROOT = Path(__file__).resolve().parents[1]

FIX = {
    "title": "Roaming tariff chunking",
    "bad_label": "Anti-pattern: tariff PDF cut every 512 tokens",
    "good_label": "Fix: row-level chunks, prices from the catalog",
    "bad": [["Roaming PDF", "Zones x plans"], ["Split at 512", "Ignores layout"], ["Chunk 14", "Rates, no plans"], ["Wrong quote", "Bill shock"]],
    "good": [["Layout parser", "Table detected"], ["Row chunks", "Plan+zone+rate"], ["Price tool"], ["Grounded", "Cites <offer> & ID"]],
}

ARCH = {
    "title": "SIM swap 'fixed'",
    "legend": "Teal = new or changed control",
    "lanes": [
        {"name": "Channel", "nodes": [{"id": "ch", "title": "Customer channel", "sub": "App, IVR, chat"}, {"id": "x", "title": "", "kind": "spacer"}]},
        {"name": "Orchestration", "nodes": [
            {"id": "ag", "title": "SIM-swap agent", "sub": "Plans, explains", "kind": "agent"},
            {"id": "pe", "title": "Policy engine", "sub": "Authorizes every swap", "kind": "good", "span": 1.5}]},
        {"name": "Tools", "nodes": [
            {"id": "a", "title": "Step-up auth", "kind": "good"}, {"id": "f", "title": "Fraud score", "kind": "bad"},
            {"id": "s", "title": "Swap SIM", "kind": "good"}]},
        {"name": "Records", "nodes": [{"id": "r", "title": "HSS", "sub": "Subscriber data"}]},
    ],
    "edges": [{"from": "ch", "to": "ag"}, {"from": "ag", "to": "pe", "two_way": True}, {"from": "s", "to": "r"}, {"from": "pe", "to": "a"}],
    "bus": {"from": "ag", "to": ["a", "f", "s"]},
    "markers": [{"node": "f", "n": 3}, {"node": "ag", "n": 1}],
}


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
@pytest.mark.parametrize("kind,spec", [("fix", FIX), ("arch", ARCH)])
def test_parity(kind, spec, tmp_path):
    script = (
        f"const r=require({json.dumps(str(ROOT / 'site/src/render.js'))});"
        f"const s=JSON.parse(require('fs').readFileSync(0,'utf8'));"
        f"process.stdout.write(r.{'renderFix' if kind == 'fix' else 'renderArch'}(s));"
    )
    js = subprocess.run(["node", "-e", script], input=json.dumps(spec), capture_output=True, text=True, check=True).stdout
    py = render_fix(spec) if kind == "fix" else render_arch(spec)
    assert js == py
