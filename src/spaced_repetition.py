"""Spaced Repetition & Cognitive Retention Engine for BHARATGURU.

Schedules SM-2 review checkpoints (Day 0, Day 1, Day 3, Day 7, Day 14)
to counteract Ebbinghaus forgetting curve.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Any

from src.knowledge_graph import KnowledgeGraphStore

INTERVAL_DAYS = [0, 1, 3, 7, 14, 30]


@dataclass
class ReviewCard:
    concept: str
    due_day_label: str             # "Day 1: Quick Recall", "Day 3: Targeted Question", etc.
    urgency: str                   # "OVERDUE", "DUE_TODAY", "UPCOMING", "RETAINED"
    days_since_learned: float
    recommended_action: str
    checkpoint_question: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def get_spaced_repetition_queue(student: str) -> list[dict[str, Any]]:
    """Generates the prioritized spaced review queue for the student."""
    store = KnowledgeGraphStore()
    graph = store.get_student_graph(student)
    store.close()

    now = time.time()
    queue = []

    for node in graph["nodes"]:
        if node["attempts"] == 0:
            continue

        last_attempt = node["last_attempt"]
        elapsed_days = max(0.0, (now - last_attempt) / 86400.0)
        c_name = node["concept"]
        retention = node["retention"]

        if elapsed_days >= 7.0:
            urgency = "OVERDUE"
            label = "Day 7: Mini Assessment Checkpoint"
            action = "Targeted 3-question recall quiz to restore retention above 90%"
        elif elapsed_days >= 3.0:
            urgency = "DUE_TODAY"
            label = "Day 3: Targeted Numerical Checkpoint"
            action = "1 worked numerical application"
        elif elapsed_days >= 1.0:
            urgency = "DUE_TODAY"
            label = "Day 1: Rapid Recall Checkpoint"
            action = "60-second concept flash question"
        else:
            urgency = "RETAINED"
            label = "Day 0: Initial Mastery Acquired"
            action = "Review scheduled for tomorrow"

        q_card = ReviewCard(
            concept=c_name,
            due_day_label=label,
            urgency=urgency,
            days_since_learned=round(elapsed_days, 1),
            recommended_action=action,
            checkpoint_question=f"Recall: How does changing the parameters in {c_name} affect downstream output?",
        )
        queue.append(q_card.to_dict())

    # Sort so overdue/due items come first
    queue.sort(key=lambda x: (x["urgency"] != "OVERDUE", x["urgency"] != "DUE_TODAY", -x["days_since_learned"]))
    return queue
