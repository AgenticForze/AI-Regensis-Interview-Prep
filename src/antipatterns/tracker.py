"""Interview progress tracker (SQLite). Location: $AAP_PROGRESS_DB or ~/.aap/progress.db."""
from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path

SCHEMA = """
create table if not exists attempts (
  id integer primary key autoincrement,
  user_id text not null,
  scenario_id text not null,
  topic text not null,
  score integer not null,          -- 0..5, one point per rubric criterion met
  criteria text not null,          -- json {criterion: bool}
  notes text,
  ts real not null
);
create index if not exists attempts_user on attempts(user_id, ts);
"""


def _db() -> sqlite3.Connection:
    path = Path(os.environ.get("AAP_PROGRESS_DB", Path.home() / ".aap" / "progress.db"))
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    return con


def record(user_id: str, scenario_id: str, topic: str, criteria: dict[str, bool], notes: str = "") -> int:
    score = sum(1 for v in criteria.values() if v)
    with _db() as con:
        con.execute(
            "insert into attempts(user_id, scenario_id, topic, score, criteria, notes, ts) values (?,?,?,?,?,?,?)",
            (user_id, scenario_id, topic, score, json.dumps(criteria), notes, time.time()),
        )
    return score


def history(user_id: str) -> list[dict]:
    with _db() as con:
        rows = con.execute(
            "select scenario_id, topic, score, criteria, ts from attempts where user_id=? order by ts", (user_id,)
        ).fetchall()
    return [{"scenario_id": r[0], "topic": r[1], "score": r[2], "criteria": json.loads(r[3]), "ts": r[4]} for r in rows]


def progress(user_id: str) -> dict:
    h = history(user_id)
    by_topic: dict[str, list[int]] = {}
    misses: dict[str, int] = {}
    for a in h:
        by_topic.setdefault(a["topic"], []).append(a["score"])
        for k, v in a["criteria"].items():
            if not v:
                misses[k] = misses.get(k, 0) + 1
    topics = {t: {"attempts": len(s), "avg_score": round(sum(s) / len(s), 2)} for t, s in by_topic.items()}
    weakest = sorted(topics, key=lambda t: topics[t]["avg_score"])[:3]
    return {
        "attempts": len(h),
        "avg_score": round(sum(a["score"] for a in h) / len(h), 2) if h else None,
        "topics": topics,
        "weakest_topics": weakest,
        "most_missed_criteria": sorted(misses, key=lambda k: -misses[k]),
        "answered": sorted({a["scenario_id"] for a in h}),
    }
