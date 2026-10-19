"""Bundle the engine and catalog into the skill, and zip it for upload.

  python scripts/build_skill.py          rebuild skill/agentic-ai-coach/scripts/antipatterns + zip
  python scripts/build_skill.py --check  fail if the bundled copy is out of date (used in CI)
"""
from __future__ import annotations

import filecmp
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "agentic-ai-coach"
BUNDLE = SKILL / "scripts" / "antipatterns"
MODULES = ["__init__.py", "catalog.py", "render.py", "review.py", "tools.py", "tracker.py"]

sys.path.insert(0, str(ROOT / "src"))


def build(dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    (dest / "content").mkdir(parents=True)
    for m in MODULES:
        shutil.copy2(ROOT / "src" / "antipatterns" / m, dest / m)
    shutil.copytree(ROOT / "content" / "topics", dest / "content" / "topics")
    shutil.copytree(ROOT / "content" / "architectures", dest / "content" / "architectures")
    shutil.copy2(ROOT / "content" / "rules.yaml", dest / "content" / "rules.yaml")
    shutil.copy2(ROOT / "docs" / "architecture-spec.md", dest / "content" / "architecture-spec.md")


def topic_index() -> str:
    from antipatterns.catalog import load_topics
    lines = ["# Scenario index", "",
             "All 360 scenarios by topic. Use `scripts/aap.py scenario <id>` for the full answer.", ""]
    for t in load_topics():
        lines += [f"## {t['order']}. {t['title']} (`{t['id']}`)", "", t["summary"], ""]
        lines += [f"- `{s['id']}` [{s['domain']}, {s['severity']}] {s['title']}" for s in t["scenarios"]]
        lines.append("")
    return "\n".join(lines)


def same_tree(a: Path, b: Path) -> bool:
    cmp = filecmp.dircmp(a, b, ignore=["__pycache__"])
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False
    return all(same_tree(a / d, b / d) for d in cmp.common_dirs)


def main() -> int:
    index = topic_index()
    if "--check" in sys.argv:
        with tempfile.TemporaryDirectory() as tmp:
            build(Path(tmp) / "antipatterns")
            ok = same_tree(Path(tmp) / "antipatterns", BUNDLE)
        ok = ok and (SKILL / "references" / "scenario-index.md").read_text() == index
        print("skill bundle up to date" if ok else "skill bundle is stale: run python scripts/build_skill.py")
        return 0 if ok else 1
    build(BUNDLE)
    (SKILL / "references" / "scenario-index.md").write_text(index)
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    zpath = dist / "agentic-ai-coach.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(SKILL.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts:
                z.write(f, f.relative_to(SKILL.parent))
    print(f"bundled {len(MODULES)} modules + catalog into {BUNDLE.relative_to(ROOT)}; wrote {zpath.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
