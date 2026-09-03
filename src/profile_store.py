"""SQLite per-session progress store + "recommended next topic".

Lightweight on purpose (Section 14/15): topics studied, score, weak/strong
concepts, timestamp. History drives one next-topic suggestion per session.
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

import config
from src.llm import generate_json

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    student       TEXT NOT NULL,
    topic         TEXT NOT NULL,
    language      TEXT,
    level         TEXT,
    score         REAL,
    out_of        REAL,
    strong        TEXT,          -- json list
    weak          TEXT,          -- json list
    created_at    REAL NOT NULL
);
"""


class ProfileStore:
    def __init__(self, db_path: str | Path | None = None):
        self.path = Path(db_path or config.DB_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    # ------------------------------------------------------------------ #
    def record_session(
        self,
        student: str,
        topic: str,
        *,
        language: str,
        level: str,
        score: float,
        out_of: float,
        strong: list[str],
        weak: list[str],
    ) -> int:
        cur = self.conn.execute(
            "INSERT INTO sessions "
            "(student, topic, language, level, score, out_of, strong, weak, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (
                student, topic, language, level, float(score), float(out_of),
                json.dumps(strong), json.dumps(weak), time.time(),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def history(self, student: str, limit: int = 20) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM sessions WHERE student=? ORDER BY created_at DESC LIMIT ?",
            (student, limit),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["strong"] = json.loads(d.get("strong") or "[]")
            d["weak"] = json.loads(d.get("weak") or "[]")
            out.append(d)
        return out

    def profile(self, student: str) -> dict:
        h = self.history(student)
        weak, strong, topics = [], [], []
        for s in h:
            topics.append(s["topic"])
            weak += s["weak"]
            strong += s["strong"]
        return {
            "student": student,
            "sessions": len(h),
            "topics_studied": topics,
            "recurring_weak": sorted({w for w in weak if weak.count(w) >= 1}),
            "recurring_strong": sorted(set(strong) - set(weak)),
            "last_session": h[0] if h else None,
        }

    # ------------------------------------------------------------------ #
    def recommend_next_topic(self, student: str, current_topic: str) -> dict:
        prof = self.profile(student)
        if prof["sessions"] == 0:
            return {
                "next_topic": f"A follow-on subtopic of {current_topic}",
                "reason": "No prior history yet; continue along the same strand.",
            }
        prompt = (
            f"Student history:\n"
            f"  topics studied: {prof['topics_studied']}\n"
            f"  weak concepts:  {prof['recurring_weak']}\n"
            f"  strong concepts:{prof['recurring_strong']}\n"
            f"  just finished:  {current_topic}\n\n"
            "Recommend the single best next topic. JSON: "
            '{"next_topic": str, "reason": str}. The reason must refer to a '
            "specific weak area if one exists."
        )
        data = generate_json(prompt, tag="next_topic", temperature=0.4)
        return {
            "next_topic": data.get("next_topic", f"Next steps in {current_topic}"),
            "reason": data.get("reason", "Builds on the most recent session."),
        }

    def close(self):
        self.conn.close()
