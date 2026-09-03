"""Adaptive Pedagogy Policy Selector & Socratic Dialogue Engine for BHARATGURU.

Dynamically shifts pedagogical strategy (analogy, counterexample, visual deconstruction,
worked mathematical example, Socratic inquiry) based on student cognitive state.
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from src.llm import generate_json, generate_text


class PedagogyStrategy(str, Enum):
    ANALOGY = "analogy"
    VISUAL_DECONSTRUCTION = "visual_deconstruction"
    WORKED_EXAMPLE = "worked_example"
    SOCRATIC_QUESTIONING = "socratic_questioning"
    COUNTEREXAMPLE = "counterexample"
    SIMPLIFIED_INTUITION = "simplified_intuition"


# Strategy description injected into generation prompts
STRATEGY_INSTRUCTIONS = {
    PedagogyStrategy.ANALOGY: (
        "Strategy: FRESH PHYSICAL ANALOGY. Use an intuitive, tangible physical scenario "
        "completely different from previous attempts (e.g. water pressure, traffic flow, bicycle gears)."
    ),
    PedagogyStrategy.COUNTEREXAMPLE: (
        "Strategy: ILLUMINATING COUNTEREXAMPLE. Present an extreme or revealing scenario that "
        "directly breaks the student's false assumption and exposes the contradiction."
    ),
    PedagogyStrategy.WORKED_EXAMPLE: (
        "Strategy: STEP-BY-STEP WORKED CALCULATION. Walk through a concrete numerical case "
        "with round numbers (e.g., V=10V, R1=2Ω vs R2=5Ω), calculating the exact result."
    ),
    PedagogyStrategy.VISUAL_DECONSTRUCTION: (
        "Strategy: SPATIAL/VISUAL WALKTHROUGH. Describe the physical anatomy of the system "
        "layer by layer as if looking at a diagram or cross-section."
    ),
    PedagogyStrategy.SOCRATIC_QUESTIONING: (
        "Strategy: SOCRATIC GUIDANCE. Do not hand over the answer. Ask a guided leading question "
        "that cues the student to deduce the underlying principle themselves."
    ),
    PedagogyStrategy.SIMPLIFIED_INTUITION: (
        "Strategy: ZERO-JARGON INTUITIVE CORE. Strip away all formulas and formal terminology. "
        "Explain in plain, conversational language what is actually happening physically."
    ),
}


def select_adaptive_strategy(
    attempts_on_concept: int,
    misconception: str | None = None,
    preferred_style: str = "analogy",
    mode: str = "DIRECT",
) -> PedagogyStrategy:
    """Selects the best pedagogical strategy based on learner history and current mode."""
    if mode == "SOCRATIC":
        return PedagogyStrategy.SOCRATIC_QUESTIONING

    if attempts_on_concept == 1:
        # First wrong answer: try a counterexample or fresh analogy
        return PedagogyStrategy.COUNTEREXAMPLE if misconception else PedagogyStrategy.ANALOGY
    elif attempts_on_concept == 2:
        # Second wrong answer: shift to step-by-step worked example or visual breakdown
        return PedagogyStrategy.WORKED_EXAMPLE
    else:
        # Multiple struggles: strip down to absolute simplest intuition
        return PedagogyStrategy.SIMPLIFIED_INTUITION


def socratic_dialogue_turn(
    concept: str,
    dialogue_history: list[dict[str, str]],
    student_latest_input: str,
    language: str = "English",
) -> dict[str, Any]:
    """Generates a Socratic guiding response to lead the student toward discovering the principle."""
    formatted_history = "\n".join(
        f"{msg['role'].upper()}: {msg['text']}" for msg in dialogue_history[-4:]
    )

    prompt = (
        f"Subject Concept: {concept}\n"
        f"Conversation History:\n{formatted_history}\n"
        f"Student Latest Input: \"{student_latest_input}\"\n\n"
        "You are Socrates teaching this student. Never give away the answer directly. "
        "Acknowledge any partial truth in what they said, then pose ONE targeted question "
        "that nudges them to the next logical realization. "
        f"Respond in natural {language}. Keep it to 2-3 sentences max."
    )

    socratic_reply = generate_text(prompt, tag="explain", temperature=0.6)
    return {
        "reply": socratic_reply.strip(),
        "is_socratic": True,
        "concept": concept,
    }
