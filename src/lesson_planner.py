"""Learner-instruction parser + lesson-planning agent (both Gemini JSON-mode)."""
from __future__ import annotations

from dataclasses import dataclass, field

import config
from src.llm import generate_json
from src.retrieval import Retriever

VALID_LANGS = tuple(config.LANGUAGES)


@dataclass
class LearnerInstruction:
    level: str = "beginner"           # beginner | intermediate | advanced
    time_minutes: int = 20
    language: str = "English"
    style: str = "clear real-world examples"
    focus: str = ""

    def normalised(self) -> "LearnerInstruction":
        self.level = (self.level or "beginner").lower().strip()
        if self.level not in ("beginner", "intermediate", "advanced"):
            self.level = "beginner"
        # snap requested minutes to the nearest duration template
        self.time_minutes = min(
            config.DURATION_TEMPLATES,
            key=lambda t: abs(t - int(self.time_minutes or 20)),
        )
        lang = (self.language or "English").strip().title()
        self.language = lang if lang in VALID_LANGS else "English"
        self.style = self.style or "clear real-world examples"
        return self


@dataclass
class Segment:
    concept: str
    depth: str
    example: str
    checkpoint_question: str
    source_page: int | None = None
    source_label: str | None = None
    source_quote: str = ""


@dataclass
class LessonPlan:
    title: str
    language: str
    level: str
    segments: list[Segment] = field(default_factory=list)
    grounded: bool = False            # True when built from uploaded material

    def __len__(self) -> int:
        return len(self.segments)


# --------------------------------------------------------------------------- #
# 1. Parse a free-text learner instruction
# --------------------------------------------------------------------------- #
_INSTR_SYS = (
    "You convert a student's free-text request into a compact JSON profile. "
    "Infer sensibly; never invent a language the student did not imply."
)


def parse_instruction(text: str) -> LearnerInstruction:
    if not text or not text.strip():
        return LearnerInstruction().normalised()
    prompt = (
        "Student request:\n"
        f'"""{text.strip()}"""\n\n'
        "Return JSON with exactly these keys:\n"
        '  level         : "beginner" | "intermediate" | "advanced"\n'
        "  time_minutes  : integer (5, 20 or 60 — pick the closest)\n"
        f"  language      : one of {list(VALID_LANGS)}\n"
        "  style         : short phrase describing the example/explanation style\n"
        "  focus         : what to concentrate on (chapter, subtopic, or \"\")\n"
    )
    data = generate_json(prompt, tag="instruction", system=_INSTR_SYS)
    return LearnerInstruction(
        level=data.get("level", "beginner"),
        time_minutes=data.get("time_minutes", 20),
        language=data.get("language", "English"),
        style=data.get("style", "clear real-world examples"),
        focus=data.get("focus", ""),
    ).normalised()


# --------------------------------------------------------------------------- #
# 2. Build a structured lesson plan
# --------------------------------------------------------------------------- #
_PLAN_SYS = (
    "You are an expert teacher and instructional designer. You output only a "
    "JSON lesson plan. When source excerpts are provided, every concept must be "
    "supported by them and you must copy the citation tag (e.g. [notes p.41]) "
    "into 'source_label'. When no excerpts are provided, build the plan from "
    "well-established curriculum knowledge."
)


def _template_for(minutes: int) -> dict:
    return config.DURATION_TEMPLATES.get(minutes, config.DURATION_TEMPLATES[20])


def make_lesson_plan(
    topic: str,
    instruction: LearnerInstruction,
    retriever: Retriever | None = None,
) -> LessonPlan:
    tmpl = _template_for(instruction.time_minutes)
    grounded = retriever is not None and len(retriever) > 0

    if grounded:
        context = retriever.context_block(topic or instruction.focus or "overview", k=8)
        source_note = (
            "SOURCE EXCERPTS (cite these — put the bracketed tag in "
            "'source_label', and a short verbatim snippet in 'source_quote'):\n"
            f"{context}\n"
        )
    else:
        source_note = "No uploaded material. Use standard curriculum knowledge.\n"

    prompt = (
        f"{source_note}\n"
        f"TOPIC: {topic or instruction.focus or 'the source material'}\n"
        f"LEARNER: level={instruction.level}, language={instruction.language}, "
        f"style={instruction.style}, focus={instruction.focus or 'whole topic'}\n"
        f"TIME BUDGET: {instruction.time_minutes} minutes -> about "
        f"{tmpl['segments']} segments, depth: {tmpl['depth']}\n\n"
        "Return JSON:\n"
        "{\n"
        '  "title": str,\n'
        f'  "language": "{instruction.language}",\n'
        f'  "level": "{instruction.level}",\n'
        '  "segments": [\n'
        "    {\n"
        '      "concept": str,\n'
        '      "depth": str,\n'
        '      "example": str  (one concrete example fitting the requested style),\n'
        '      "checkpoint_question": str,\n'
        '      "source_label": str | null,\n'
        '      "source_page": int | null,\n'
        '      "source_quote": str\n'
        "    }\n"
        "  ]\n"
        "}\n"
        f"Produce {tmpl['segments']} segments, ordered from foundational to advanced."
    )

    data = generate_json(prompt, tag="lesson_plan", system=_PLAN_SYS, temperature=0.4)

    segments = []
    for s in data.get("segments", []):
        segments.append(
            Segment(
                concept=s.get("concept", "Untitled concept"),
                depth=s.get("depth", tmpl["depth"]),
                example=s.get("example", ""),
                checkpoint_question=s.get(
                    "checkpoint_question", f"Explain {s.get('concept', 'this')} in your own words."
                ),
                source_page=s.get("source_page"),
                source_label=s.get("source_label"),
                source_quote=s.get("source_quote", ""),
            )
        )
    if not segments:
        raise RuntimeError("Lesson planner returned no segments.")

    return LessonPlan(
        title=data.get("title", topic or "Lesson"),
        language=data.get("language", instruction.language),
        level=data.get("level", instruction.level),
        segments=segments,
        grounded=grounded,
    )
