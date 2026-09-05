"""Institutional Teacher Dashboard & Class Intervention Engine for BHARATGURU.

Aggregates cohort-level concept mastery and shared misconceptions strictly from
what students have actually done (the knowledge-graph SQLite store). When no
student has attempted anything yet, it reports an empty cohort rather than
fabricating a class.
"""
from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from typing import Any

import config


def _empty_overview() -> dict[str, Any]:
    return {
        "class_name": "All students",
        "data_available": False,
        "total_enrolled": 0,
        "average_mastery": 0.0,
        "concepts_mastery": [],
        "shared_misconceptions": [],
        "recommended_remediations": [],
    }


def get_class_overview() -> dict[str, Any]:
    """Cohort analytics computed from real per-student knowledge-graph rows."""
    try:
        conn = sqlite3.connect(str(config.DB_PATH))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT student, concept, domain, mastery, misconceptions, attempts, successes "
            "FROM student_knowledge_graph WHERE attempts > 0"
        ).fetchall()
        conn.close()
    except sqlite3.OperationalError:
        # Table not created yet -> nobody has learned anything.
        return _empty_overview()

    if not rows:
        return _empty_overview()

    students = {r["student"] for r in rows}

    # --- per-concept aggregation ---
    by_concept: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for r in rows:
        by_concept[r["concept"]].append(r)

    concepts_mastery = []
    for concept, crows in sorted(by_concept.items()):
        masteries = [float(cr["mastery"]) * 100 for cr in crows]
        avg_mastery = round(sum(masteries) / len(masteries), 1)
        at_risk = sum(1 for m in masteries if m < 50.0)
        if avg_mastery >= 75:
            status = "Strong"
        elif avg_mastery >= 55:
            status = "Moderate"
        elif avg_mastery >= 40:
            status = "High Risk"
        else:
            status = "Critical Risk"
        concepts_mastery.append({
            "concept": concept,
            "mastery": round(avg_mastery),
            "status": status,
            "students_at_risk": at_risk,
        })

    # --- shared misconceptions ---
    mis_counter: dict[str, int] = defaultdict(int)
    mis_concept: dict[str, str] = {}
    for r in rows:
        for m in json.loads(r["misconceptions"] or "[]"):
            mis_counter[m] += 1
            mis_concept.setdefault(m, r["concept"])

    total_students = len(students)
    shared_misconceptions = [
        {
            "misconception": m,
            "concept": mis_concept.get(m, ""),
            "affected_students": n,
            "percentage": round(100 * n / max(1, total_students)),
            "root_cause": "Recurring across the cohort — inspect individual answer logs.",
            "recommended_action": "Run a targeted 5-minute remediation on this concept.",
        }
        for m, n in sorted(mis_counter.items(), key=lambda kv: -kv[1])
    ]

    recommended_remediations = [
        {
            "title": f"5-Minute Targeted Remediation: {c['concept']}",
            "concept": c["concept"],
            "target_cohort": f"{c['students_at_risk']} students below 50% mastery",
            "delivery_language": "Cohort default",
            "pedagogy": "Re-teach with a fresh analogy + 3 rapid worked examples",
            "status": "Ready to Launch",
        }
        for c in concepts_mastery
        if c["students_at_risk"] > 0
    ]

    all_mast = [float(r["mastery"]) * 100 for r in rows]
    return {
        "class_name": "All students",
        "data_available": True,
        "total_enrolled": total_students,
        "average_mastery": round(sum(all_mast) / len(all_mast), 1),
        "concepts_mastery": concepts_mastery,
        "shared_misconceptions": shared_misconceptions,
        "recommended_remediations": recommended_remediations,
    }


def get_students_roster() -> list[dict[str, Any]]:
    """Return all students with their overall mastery and risk status for teacher inspection."""
    try:
        conn = sqlite3.connect(str(config.DB_PATH))
        conn.row_factory = sqlite3.Row

        users = conn.execute(
            "SELECT id, username, full_name, grade_or_board, preferred_language, avatar_url, last_login FROM users WHERE role = 'student'"
        ).fetchall()

        roster = []
        for u in users:
            s_name = u["username"]
            kg_rows = conn.execute(
                "SELECT mastery, attempts, successes FROM student_knowledge_graph WHERE student = ?",
                (s_name,),
            ).fetchall()
            if kg_rows:
                avg_m = round(100 * sum(r["mastery"] for r in kg_rows) / len(kg_rows), 1)
                at_risk_count = sum(1 for r in kg_rows if r["mastery"] < 0.6)
            else:
                avg_m = 0.0
                at_risk_count = 0

            status = (
                "High Risk"
                if at_risk_count >= 2
                else ("Moderate Risk" if at_risk_count == 1 else "Strong Progress")
            )
            roster.append({
                "student_id": s_name,
                "full_name": u["full_name"],
                "grade": u["grade_or_board"],
                "language": u["preferred_language"],
                "avatar": u["avatar_url"] or "👨‍🎓",
                "average_mastery": avg_m,
                "concepts_studied": len(kg_rows),
                "at_risk_concepts": at_risk_count,
                "status": status,
                "last_active": u["last_login"],
            })
        conn.close()
        return sorted(
            roster,
            key=lambda x: (x["status"] == "High Risk", x["at_risk_concepts"]),
            reverse=True,
        )
    except Exception as e:
        print(f"[TEACHER ROSTER ERROR] {e}")
        return []


def get_student_pedagogical_guidance(student: str) -> dict[str, Any]:
    """Provide a tailored 'How to Teach This Student' pedagogical blueprint."""
    try:
        conn = sqlite3.connect(str(config.DB_PATH))
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE username = ?", (student,)).fetchone()
        kg_rows = conn.execute("SELECT * FROM student_knowledge_graph WHERE student = ?", (student,)).fetchall()
        conn.close()
    except Exception:
        user = None
        kg_rows = []

    weak_concepts = []
    strong_concepts = []
    all_misconceptions = []

    for r in kg_rows:
        m_pct = round(float(r["mastery"]) * 100, 1)
        mis = json.loads(r["misconceptions"] or "[]")
        all_misconceptions.extend(mis)
        item = {
            "concept": r["concept"],
            "domain": r["domain"],
            "mastery": m_pct,
            "misconceptions": mis,
            "preferred_style": r["preferred_style"] or "analogy",
        }
        if m_pct < 65:
            weak_concepts.append(item)
        elif m_pct >= 80:
            strong_concepts.append(item)

    pedagogical_tips = []
    if all_misconceptions:
        for mis in set(all_misconceptions):
            pedagogical_tips.append({
                "type": "Misconception Deconstruction",
                "insight": f"Student holds mental error: \"{mis}\"",
                "instructional_strategy": "Do not give the definition directly. Ask a Socratic disproving question that forces the student to recognize the contradiction.",
            })

    if any("resist" in w["concept"].lower() or "current" in w["concept"].lower() for w in weak_concepts):
        pedagogical_tips.append({
            "type": "Physics / Electricity Guidance",
            "insight": "Student confuses Resistance (property of material) with Resistivity (geometry-independent constant).",
            "instructional_strategy": "Use the Water Pipe Analogy: Voltage is water pressure at the tap, Current is flow rate, Resistance is the narrow pipe constriction.",
        })

    if any("heat" in w["concept"].lower() or "power" in w["concept"].lower() for w in weak_concepts):
        pedagogical_tips.append({
            "type": "Joule Heating Pedagogy",
            "insight": "Student assumes higher resistance always draws more current.",
            "instructional_strategy": "Anchor with Cricket scenario or electric iron: current encounters friction inside wire particles, turning kinetic energy into thermal heat (H = I²Rt).",
        })

    if not pedagogical_tips:
        pedagogical_tips.append({
            "type": "Growth & Mastery Reinforcement",
            "insight": "Student shows solid foundation across evaluated concepts.",
            "instructional_strategy": "Apply the Feynman technique: ask the student to explain the law as if teaching a 10-year-old child.",
        })

    return {
        "student": student,
        "full_name": user["full_name"] if user else student.capitalize(),
        "grade_or_board": user["grade_or_board"] if user else "CBSE Class 10",
        "preferred_language": user["preferred_language"] if user else "English",
        "weak_concepts": weak_concepts,
        "strong_concepts": strong_concepts,
        "misconceptions": list(set(all_misconceptions)),
        "how_to_teach_guidance": pedagogical_tips,
        "recommended_action": f"Launch 5-min Socratic intervention on {weak_concepts[0]['concept']}" if weak_concepts else "Assign multi-concept challenge problem",
        "optimal_teaching_mode": "SOCRATIC" if len(weak_concepts) <= 1 else "ANALOGY_FIRST",
    }

