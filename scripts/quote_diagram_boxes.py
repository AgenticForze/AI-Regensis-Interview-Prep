"""Authoring helper: quote every box label in `bad:`/`good:` flow lists.

YAML flow sequences break on plain labels containing ? : , # etc. Run this on a
topic file after editing so every label is a double-quoted string.
Usage: python scripts/quote_diagram_boxes.py content/topics/*.yaml
"""
import json
import re
import sys
from pathlib import Path

LINE = re.compile(r"^(\s+(?:bad|good): )(\[\[.*\]\])\s*$")


def split_items(s: str) -> list[str]:
    """Split the inside of [a, "b, c", 'd'] on top-level commas."""
    items, cur, q = [], "", None
    for ch in s:
        if q:
            cur += ch
            if ch == q:
                q = None
        elif ch in "\"'" and not cur.strip():
            q = ch
            cur += ch
        elif ch == ",":
            items.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        items.append(cur.strip())
    return items


def unquote(tok: str) -> str:
    if tok.startswith('"') and tok.endswith('"'):
        return json.loads(tok)
    if tok.startswith("'") and tok.endswith("'"):
        return tok[1:-1].replace("''", "'")
    return tok


def fix_line(body: str) -> str:
    inner = body[1:-1]
    boxes, depth, cur, q = [], 0, "", None
    for ch in inner:
        if q:
            cur += ch
            if ch == q:
                q = None
            continue
        if ch in "\"'" and depth >= 1 and not cur.strip().rsplit(",", 1)[-1].strip():
            q = ch
        if ch == "[":
            depth += 1
            if depth == 1:
                cur = ""
                continue
        if ch == "]":
            depth -= 1
            if depth == 0:
                boxes.append([unquote(t) for t in split_items(cur)])
                continue
        if depth >= 1:
            cur += ch
    return "[" + ", ".join("[" + ", ".join(json.dumps(x) for x in b) + "]" for b in boxes) + "]"


def main(paths):
    for p in map(Path, paths):
        out = []
        for line in p.read_text().splitlines():
            m = LINE.match(line)
            out.append(m.group(1) + fix_line(m.group(2)) if m else line)
        p.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
