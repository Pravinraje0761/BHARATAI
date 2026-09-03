"""Student Knowledge Graph Engine for BHARATGURU.

Continuously models a student's cognitive mastery, prerequisite dependencies,
confidence, misconceptions, and retention decay.
"""
from __future__ import annotations

import json
import math
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import config

_KG_SCHEMA = """
CREATE TABLE IF NOT EXISTS student_knowledge_graph (
    student         TEXT NOT NULL,
    concept         TEXT NOT NULL,
    domain          TEXT NOT NULL,
    mastery         REAL DEFAULT 0.0,
    confidence      REAL DEFAULT 0.5,
    misconceptions  TEXT DEFAULT '[]',   -- json list of strings
    attempts        INTEGER DEFAULT 0,
    successes       INTEGER DEFAULT 0,
    preferred_style TEXT DEFAULT 'analogy',
    language        TEXT DEFAULT 'English',
    last_attempt    REAL NOT NULL,
    PRIMARY KEY (student, concept)
);
CREATE INDEX IF NOT EXISTS idx_kg_student ON student_knowledge_graph(student);
"""

# Prerequisite concept relationships (Subject -> Parent -> Children)
CONCEPT_DEPENDENCIES = {
    "Physics": {
        "Electric Current": {"prerequisites": [], "domain": "Electricity"},
        "Potential Difference (Voltage)": {"prerequisites": [], "domain": "Electricity"},
        "Resistance and Ohm's law": {"prerequisites": ["Electric Current", "Potential Difference (Voltage)"], "domain": "Electricity"},
        "Series and parallel resistor networks": {"prerequisites": ["Resistance and Ohm's law"], "domain": "Electricity"},
        "Joule Heating & Electric Power": {"prerequisites": ["Resistance and Ohm's law"], "domain": "Electricity"},
        "Magnetic Effects of Current": {"prerequisites": ["Electric Current"], "domain": "Electromagnetism"},
        "Electromagnetic Induction": {"prerequisites": ["Magnetic Effects of Current", "Potential Difference (Voltage)"], "domain": "Electromagnetism"},
        "Maxwell's Equations": {"prerequisites": ["Electromagnetic Induction"], "domain": "Electromagnetism"},
        "Newton's First Law & Inertia": {"prerequisites": [], "domain": "Mechanics"},
        "Newton's Second Law (F = ma)": {"prerequisites": ["Newton's First Law & Inertia"], "domain": "Mechanics"},
        "Newton's Third Law (Action-Reaction)": {"prerequisites": ["Newton's Second Law (F = ma)"], "domain": "Mechanics"},
        "Conservation of Momentum": {"prerequisites": ["Newton's Third Law (Action-Reaction)"], "domain": "Mechanics"},
    }
}


@dataclass
class ConceptNode:
    concept: str
    domain: str
    mastery: float                  # 0.0 to 1.0 (0% - 100%)
    confidence: float               # 0.0 to 1.0
    misconceptions: list[str] = field(default_factory=list)
    attempts: int = 0
    successes: int = 0
    preferred_style: str = "analogy"
    language: str = "English"
    last_attempt: float = 0.0
    retention: float = 1.0          # decayed mastery over elapsed days
    prerequisites: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class KnowledgeGraphStore:
    def __init__(self, db_path: str | Path | None = None):
        self.path = Path(db_path or config.DB_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_KG_SCHEMA)
        self.conn.commit()

    def get_student_graph(self, student: str) -> dict[str, Any]:
        """Returns the full knowledge graph nodes and link edges for a student."""
        rows = self.conn.execute(
            "SELECT * FROM student_knowledge_graph WHERE student=?", (student,)
        ).fetchall()

        saved = {r["concept"]: dict(r) for r in rows}
        now = time.time()

        nodes = []
        links = []

        # Load default curriculum tree
        for domain, concepts in CONCEPT_DEPENDENCIES.items():
            for c_name, meta in concepts.items():
                prereqs = meta.get("prerequisites", [])
                sub_domain = meta.get("domain", domain)

                if c_name in saved:
                    row = saved[c_name]
                    mastery = float(row["mastery"])
                    confidence = float(row["confidence"])
                    misconceptions = json.loads(row["misconceptions"] or "[]")
                    attempts = int(row["attempts"])
                    successes = int(row["successes"])
                    pref_style = row["preferred_style"]
                    lang = row["language"]
                    last_att = float(row["last_attempt"])

                    # Ebbinghaus retention decay calculation
                    elapsed_days = max(0.0, (now - last_att) / 86400.0)
                    retention = max(0.2, round(mastery * math.exp(-0.08 * elapsed_days), 2))
                else:
                    # Default initialized state
                    mastery = 0.0
                    confidence = 0.5
                    misconceptions = []
                    attempts = 0
                    successes = 0
                    pref_style = "analogy"
                    lang = "English"
                    last_att = now
                    retention = 0.0

                # Determine status tag
                if mastery >= 0.75:
                    status = "mastered"
                elif attempts > 0:
                    status = "in-progress" if not misconceptions else "needs-remediation"
                elif all(saved.get(p, {}).get("mastery", 0) >= 0.7 for p in prereqs):
                    status = "ready-to-learn"
                else:
                    status = "locked"

                node = ConceptNode(
                    concept=c_name,
                    domain=sub_domain,
                    mastery=round(mastery * 100, 1),
                    confidence=round(confidence, 2),
                    misconceptions=misconceptions,
                    attempts=attempts,
                    successes=successes,
                    preferred_style=pref_style,
                    language=lang,
                    last_attempt=last_att,
                    retention=round(retention * 100, 1),
                    prerequisites=prereqs,
                )
                node_dict = node.to_dict()
                node_dict["status"] = status
                nodes.append(node_dict)

                # Add link edges
                for p in prereqs:
                    links.append({"source": p, "target": c_name})

        # Calculate overall domain masteries
        mastered_count = sum(1 for n in nodes if n["mastery"] >= 70.0)
        overall_mastery = round(sum(n["mastery"] for n in nodes) / max(1, len(nodes)), 1)

        return {
            "student": student,
            "nodes": nodes,
            "links": links,
            "overall_mastery": overall_mastery,
            "mastered_count": mastered_count,
            "total_concepts": len(nodes),
        }

    def record_attempt(
        self,
        student: str,
        concept: str,
        *,
        is_correct: bool,
        misconception: str | None = None,
        language: str = "English",
        style: str = "analogy",
    ) -> dict[str, Any]:
        """Update cognitive model for concept after student answers a question."""
        row = self.conn.execute(
            "SELECT * FROM student_knowledge_graph WHERE student=? AND concept=?",
            (student, concept),
        ).fetchone()

        now = time.time()
        domain = "Physics"
        for d, c_dict in CONCEPT_DEPENDENCIES.items():
            if concept in c_dict:
                domain = c_dict[concept].get("domain", d)
                break

        if row:
            attempts = row["attempts"] + 1
            successes = row["successes"] + (1 if is_correct else 0)
            mis_list = json.loads(row["misconceptions"] or "[]")
            if misconception and misconception not in mis_list:
                mis_list.append(misconception)
            elif is_correct and mis_list:
                # remove or mark as resolved
                mis_list = [m for m in mis_list if m != misconception]

            # Bayesian-inspired mastery update
            old_mastery = float(row["mastery"])
            if is_correct:
                new_mastery = min(1.0, old_mastery + (1.0 - old_mastery) * 0.35)
                new_confidence = min(1.0, float(row["confidence"]) + 0.15)
            else:
                new_mastery = max(0.0, old_mastery * 0.7)
                new_confidence = max(0.2, float(row["confidence"]) - 0.2)

            self.conn.execute(
                "UPDATE student_knowledge_graph SET mastery=?, confidence=?, misconceptions=?, "
                "attempts=?, successes=?, preferred_style=?, language=?, last_attempt=? "
                "WHERE student=? AND concept=?",
                (
                    new_mastery, new_confidence, json.dumps(mis_list), attempts, successes,
                    style, language, now, student, concept,
                ),
            )
        else:
            attempts = 1
            successes = 1 if is_correct else 0
            mis_list = [misconception] if misconception else []
            new_mastery = 0.5 if is_correct else 0.2
            new_confidence = 0.7 if is_correct else 0.3

            self.conn.execute(
                "INSERT INTO student_knowledge_graph "
                "(student, concept, domain, mastery, confidence, misconceptions, attempts, successes, preferred_style, language, last_attempt) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    student, concept, domain, new_mastery, new_confidence, json.dumps(mis_list),
                    attempts, successes, style, language, now,
                ),
            )

        self.conn.commit()
        return {
            "concept": concept,
            "mastery": round(new_mastery * 100, 1),
            "confidence": round(new_confidence, 2),
            "misconceptions": mis_list,
        }

    def close(self):
        self.conn.close()
