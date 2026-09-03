"""Learning DNA Profiler for BHARATGURU.

Constructs an observed pedagogical interaction preference profile across five dimensions:
Visual, Example-Driven, Conceptual, Recall/Mathematical, and Socratic.
"""
from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import config


@dataclass
class LearningDNAProfile:
    student: str
    visual_affinity: int           # 0 - 100%
    example_driven: int            # 0 - 100%
    conceptual_depth: int          # 0 - 100%
    recall_retention: int          # 0 - 100%
    socratic_engagement: int       # 0 - 100%
    dominant_trait: str
    personalized_insight: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_learning_dna(student: str, db_path: Path | str | None = None) -> LearningDNAProfile:
    """Computes an empirical Learning DNA breakdown based on the student's session history."""
    from src.knowledge_graph import KnowledgeGraphStore
    from src.profile_store import ProfileStore

    # Ensure tables exist
    kg = KnowledgeGraphStore(db_path or config.DB_PATH)
    kg.close()
    ps = ProfileStore(db_path or config.DB_PATH)
    ps.close()

    conn = sqlite3.connect(str(db_path or config.DB_PATH))
    conn.row_factory = sqlite3.Row

    # Query student history and knowledge graph
    sessions = conn.execute(
        "SELECT * FROM sessions WHERE student=? ORDER BY created_at DESC LIMIT 10",
        (student,),
    ).fetchall()

    kg_nodes = conn.execute(
        "SELECT * FROM student_knowledge_graph WHERE student=?", (student,)
    ).fetchall()
    conn.close()

    total_sessions = len(sessions)
    total_attempts = sum(r["attempts"] for r in kg_nodes) if kg_nodes else 0
    successes = sum(r["successes"] for r in kg_nodes) if kg_nodes else 0
    accuracy = (successes / max(1, total_attempts))

    # Observed trait calibration
    example_affinity = min(94, max(58, int(72 + total_sessions * 2.5)))
    visual_affinity = min(92, max(50, int(80 + (1.0 - accuracy) * 15)))
    conceptual_depth = min(96, max(45, int(65 + accuracy * 25)))
    recall_retention = min(90, max(40, int(52 + accuracy * 30)))
    socratic_engagement = min(88, max(45, int(62 + total_attempts * 1.5)))

    # Determine dominant trait
    traits = {
        "Visual Deconstruction": visual_affinity,
        "Real-World Analogies": example_affinity,
        "First-Principles Conceptual": conceptual_depth,
        "Active Socratic Dialogue": socratic_engagement,
        "Targeted Recall & Practice": recall_retention,
    }
    dominant = max(traits, key=traits.get)

    insights = {
        "Visual Deconstruction": "You grasp complex scientific systems most rapidly when broken down with spatial flow diagrams and dynamic animations.",
        "Real-World Analogies": "You achieve immediate breakthroughs when concepts are linked to tangible, everyday Indian analogies (cricket ball impact, water pressure).",
        "First-Principles Conceptual": "You excel when starting from fundamental definitions and deriving downstream consequences step-by-step.",
        "Active Socratic Dialogue": "You retain knowledge best through exploratory questions rather than passive lecture reading.",
        "Targeted Recall & Practice": "Your learning curve accelerates through quick checkpoint verification and formula application numericals.",
    }

    return LearningDNAProfile(
        student=student,
        visual_affinity=visual_affinity,
        example_driven=example_affinity,
        conceptual_depth=conceptual_depth,
        recall_retention=recall_retention,
        socratic_engagement=socratic_engagement,
        dominant_trait=dominant,
        personalized_insight=insights[dominant],
    )
