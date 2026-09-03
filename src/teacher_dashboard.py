"""Institutional Teacher Dashboard & Class Intervention Engine for BHARATGURU.

Aggregates cohort-level concept mastery, identifies shared misconceptions across students,
and generates 1-click targeted remediation micro-lessons.
"""
from __future__ import annotations

from typing import Any

from src.knowledge_graph import CONCEPT_DEPENDENCIES


def get_class_overview() -> dict[str, Any]:
    """Provides classroom-level analytics for institutional teachers and school principals."""
    # Simulated cohort metrics for Bharat Academix classrooms
    students_count = 42
    concepts_mastery = [
        {"concept": "Electric Current & Charge", "mastery": 84, "status": "Strong", "students_at_risk": 3},
        {"concept": "Potential Difference (Voltage)", "mastery": 78, "status": "Good", "students_at_risk": 5},
        {"concept": "Resistance and Ohm's Law", "mastery": 52, "status": "High Risk", "students_at_risk": 16},
        {"concept": "Series & Parallel Resistors", "mastery": 41, "status": "Critical Risk", "students_at_risk": 22},
        {"concept": "Newton's Laws & Inertia", "mastery": 68, "status": "Moderate", "students_at_risk": 11},
    ]

    shared_misconceptions = [
        {
            "misconception": "Current gets consumed/depleted by circuit components",
            "concept": "Electrical Current",
            "affected_students": 14,
            "percentage": 33,
            "root_cause": "Conflating electrical charge flow with energy dissipation",
            "recommended_action": "Run bicycle-chain closed-loop demonstration",
        },
        {
            "misconception": "Current increases when resistance increases at constant voltage",
            "concept": "Resistance and Ohm's law",
            "affected_students": 18,
            "percentage": 43,
            "root_cause": "Faulty intuition that increasing any input increases electrical output",
            "recommended_action": "Deploy crowded corridor friction counterexample + 5-min remediation blitz",
        },
        {
            "misconception": "Continuous forward force is required to sustain steady velocity",
            "concept": "Newton's First Law",
            "affected_students": 12,
            "percentage": 28,
            "root_cause": "Earth-bound friction biases masking the principle of inertia",
            "recommended_action": "Demonstrate deep-space probe and puck-on-ice thought experiments",
        },
    ]

    recommended_remediations = [
        {
            "title": "5-Minute Targeted Remediation: Ohm's Law Inverse Proportionality",
            "concept": "Resistance and Ohm's law",
            "target_cohort": "18 struggling students",
            "delivery_language": "Bilingual Hinglish / Hindi",
            "pedagogy": "Water hose constriction visual analogy + 3 rapid worked examples",
            "status": "Ready to Launch",
        },
        {
            "title": "Conceptual Reset: Charge Conservation vs Energy Transfer",
            "concept": "Electric Current",
            "target_cohort": "14 students",
            "delivery_language": "English / Tamil",
            "pedagogy": "Two-ammeter circuit counterexample",
            "status": "Ready to Launch",
        },
    ]

    return {
        "class_name": "Class 10-A (Science & Physics)",
        "total_enrolled": students_count,
        "average_mastery": 64.6,
        "concepts_mastery": concepts_mastery,
        "shared_misconceptions": shared_misconceptions,
        "recommended_remediations": recommended_remediations,
    }
