"""Misconception Engine for BHARATGURU.

Identifies cognitive roots of student errors, computes diagnosis confidence,
and prescribes targeted pedagogical interventions and counterexamples.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

from src.llm import generate_json

# Curated Cognitive Misconception Knowledgebase
KNOWN_MISCONCEPTIONS = [
    {
        "pattern": r"(consum|eat|drain|use\s*up|waste).*current",
        "concept": "Electrical Current",
        "misconception": "Current is consumed or depleted by resistors/bulbs",
        "confidence": 0.94,
        "likely_cause": "Conflation of charge flow (current) with energy transfer.",
        "recommended_intervention": "Closed water-pipe loop analogy + bicycle chain analogy + conservation of charge proof",
        "counterexample": "If current was consumed, an ammeter placed after the bulb would read less than before the bulb — in reality, both ammeters read identically!",
    },
    {
        "pattern": r"(current|i)\s*(increase|rise|grow|more).*(resist|r)",
        "concept": "Resistance & Ohm's Law",
        "misconception": "Direct proportionality assumed between current and resistance at constant voltage",
        "confidence": 0.96,
        "likely_cause": "Intuitive bias that increasing any circuit property increases the outcome.",
        "recommended_intervention": "Crowded hallway friction analogy + mathematical ratio counterexample",
        "counterexample": "Imagine squeezing a garden hose (more resistance) while water pressure is fixed — water flow drops immediately, it never increases!",
    },
    {
        "pattern": r"(force|push).*(keep|maintain|continue).*mov",
        "concept": "Newton's First Law & Inertia",
        "misconception": "Aristotelian belief that continuous force is required to sustain steady motion",
        "confidence": 0.92,
        "likely_cause": "Everyday friction makes objects stop unless pushed, obscuring Newton's 1st Law.",
        "recommended_intervention": "Deep space Voyager probe thought experiment + frictionless air-hockey puck",
        "counterexample": "Once a spacecraft turns off its rocket engines in vacuum, it coasts forever at constant speed without burning any fuel!",
    },
    {
        "pattern": r"(heavy|heavier|weight|mass).*fall.*faster",
        "concept": "Gravitational Acceleration",
        "misconception": "Heavier objects fall faster due to larger gravitational force",
        "confidence": 0.95,
        "likely_cause": "Observing feathers vs rocks in air without accounting for air resistance.",
        "recommended_intervention": "Galileo Leaning Tower of Pisa derivation + Apollo 15 feather-hammer moon drop",
        "counterexample": "On the Moon with no air, astronaut David Scott dropped a 1.32 kg hammer and a 0.03 kg falcon feather simultaneously — both struck the lunar surface at the exact same instant.",
    },
]


@dataclass
class MisconceptionFingerprint:
    concept: str
    misconception: str
    confidence: float
    likely_cause: str
    recommended_intervention: str
    counterexample: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_FINGERPRINT_SYS = (
    "You are the Misconception Engine in an advanced pedagogical AI tutor. "
    "Given a concept, question, and student's incorrect answer, diagnose the deep "
    "cognitive reason why they are wrong. Output ONLY JSON with keys: "
    "misconception (str), confidence (0.5 to 0.99), likely_cause (str), "
    "recommended_intervention (str), counterexample (str)."
)


def fingerprint_misconception(
    concept: str,
    question: str,
    student_answer: str,
) -> MisconceptionFingerprint:
    sa = student_answer.strip().lower()

    # 1. Fast Pattern Matching from Curated Misconceptions
    for km in KNOWN_MISCONCEPTIONS:
        if re.search(km["pattern"], sa) or (concept.lower() in km["concept"].lower() and ("increase" in sa or "consum" in sa)):
            return MisconceptionFingerprint(
                concept=concept,
                misconception=km["misconception"],
                confidence=km["confidence"],
                likely_cause=km["likely_cause"],
                recommended_intervention=km["recommended_intervention"],
                counterexample=km["counterexample"],
            )

    # 2. LLM Cognitive Diagnosis Fallback
    prompt = (
        f"Concept: {concept}\n"
        f"Checkpoint Question: {question}\n"
        f'Student Answer: "{student_answer}"\n\n'
        "Fingerprint this error. What fundamental misconception or false mental model produced it?"
    )

    data = generate_json(prompt, tag="evaluate", system=_FINGERPRINT_SYS, temperature=0.2)
    return MisconceptionFingerprint(
        concept=concept,
        misconception=data.get("misconception", "Incomplete mental model of physical relationship"),
        confidence=float(data.get("confidence", 0.88)),
        likely_cause=data.get("likely_cause", "Conflation of dependent and independent variables"),
        recommended_intervention=data.get(
            "recommended_intervention", "Concrete real-world physical analogy with step-by-step ratio comparison"
        ),
        counterexample=data.get(
            "counterexample", "Consider holding voltage constant while varying resistance."
        ),
    )
