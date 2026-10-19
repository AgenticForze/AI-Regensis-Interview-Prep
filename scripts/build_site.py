"""Build the static website from the catalog.

Writes site/dist/index.html (a full document, deployed to GitHub Pages) and
site/dist/artifact.html (the same page without the document wrapper, for a Claude artifact).
Everything is inlined except Google Fonts and the js-yaml parser from cdnjs.
"""
from __future__ import annotations

import json
import sys

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from antipatterns.catalog import load_topics, validate  # noqa: E402
from antipatterns.review import list_architectures, load_rules  # noqa: E402

SRC = ROOT / "site" / "src"
DIST = ROOT / "site" / "dist"
KEEP = ["id", "title", "domain", "severity", "tags", "scenario", "analogy", "breaks", "root_cause", "where",
        "fix", "code", "detect", "tradeoff", "variant", "line", "related", "diagram"]


def data() -> dict:
    topics = [{"id": t["id"], "order": t["order"], "title": t["title"], "summary": t["summary"],
               "scenarios": [{k: s[k] for k in KEEP if k in s} for s in t["scenarios"]]} for t in load_topics()]
    archs = []
    for a in list_architectures():
        text = (ROOT / "content" / "architectures" / f"{a['id']}.yaml").read_text()
        archs.append({**a, "yaml": text, "spec": yaml.safe_load(text)})
    return {"topics": topics, "rules": load_rules(), "architectures": archs}


def main() -> int:
    errs = validate()
    if errs:
        print("catalog invalid; run scripts/validate.py")
        return 1
    page = (SRC / "page.html").read_text()
    blob = json.dumps(data(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    for key, val in [("STYLES", (SRC / "styles.css").read_text()), ("DATA", blob),
                     ("RENDER", (SRC / "render.js").read_text()), ("REVIEW", (SRC / "review.js").read_text()),
                     ("APP", (SRC / "app.js").read_text())]:
        page = page.replace(f"/*{key}*/", val, 1)
    DIST.mkdir(parents=True, exist_ok=True)
    (DIST / "artifact.html").write_text(page)
    doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
           'body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n')
    head_end = page.index("<header")
    doc += page[:head_end] + "</head>\n<body>\n" + page[head_end:] + "\n</body>\n</html>\n"
    (DIST / "index.html").write_text(doc)
    (DIST / ".nojekyll").write_text("")
    print(f"wrote site/dist/index.html ({len(doc) / 1e6:.2f} MB) and site/dist/artifact.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
