"""The teaching loop as an explicit state machine for BHARATGURU.

    EXPLAIN -> QUESTION -> EVALUATE -> (ADAPT: reinforce | simplify | advance) -> next

Every transition is logged: that log is both the debugging tool and the demo
evidence that adaptation, misconception fingerprinting, and pedagogy shifting are real.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

import config
from src.bharat_context import get_bharat_context_prompt_directive, indianize_text
from src.hallucination_shield import verify_grounding
from src.lesson_planner import LessonPlan, Segment
from src.llm import generate_json, generate_text
from src.misconception_engine import fingerprint_misconception
from src.pedagogy import STRATEGY_INSTRUCTIONS, PedagogyStrategy, select_adaptive_strategy
from src.ingestion import Chunk
from src.retrieval import Retriever


class State(str, Enum):
    EXPLAIN = "EXPLAIN"
    QUESTION = "QUESTION"
    EVALUATE = "EVALUATE"
    ADAPT = "ADAPT"
    DONE = "DONE"


@dataclass
class Transition:
    t: float
    segment_index: int
    concept: str
    state: str
    detail: dict = field(default_factory=dict)


@dataclass
class SegmentRun:
    index: int
    concept: str
    explanation: str = ""
    reexplanation: str = ""
    question: str = ""
    followup_question: str = ""
    student_answer: str = ""
    followup_answer: str = ""
    verdict: str = ""            # correct | partial | incorrect
    misconception: str | None = None
    fingerprint: dict[str, Any] | None = None
    grounding: dict[str, Any] | None = None
    action: str = ""            # reinforce | simplify | advance
    strategy: str = "analogy"
    language: str = "English"
    attempts: int = 0


_EVAL_SYS = (
    "You are a precise formative-assessment grader. You return ONLY JSON: "
    '{"verdict": "correct"|"partial"|"incorrect", "misconception": string|null, '
    '"feedback": string}. Diagnose the specific misconception when the answer is '
    "wrong or partial; use null only when the answer is fully correct.\n\n"
    "EXAMPLES\n"
    "Q: Voltage is constant. Resistance increases. What happens to current?\n"
    'A: "The current increases."\n'
    '=> {"verdict":"incorrect","misconception":"Believes current rises with '
    'resistance; the relationship is inverse at constant voltage (I = V/R).",'
    '"feedback":"Opposite direction — with V fixed, more R means less I."}\n\n'
    "Q: Same question.\n"
    'A: "It goes down because I equals V over R."\n'
    '=> {"verdict":"correct","misconception":null,"feedback":"Correct, and the '
    'reasoning via I = V/R is exactly right."}\n\n'
    "Q: Same question.\n"
    'A: "It changes."\n'
    '=> {"verdict":"partial","misconception":"Knows there is an effect but not '
    'its direction.","feedback":"Which way does it change, and why?"}'
)


class TeachingSession:
    def __init__(
        self,
        plan: LessonPlan,
        retriever: Retriever | None = None,
        language: str | None = None,
        preset_style: str = "",
        mode: str = "DIRECT",
    ):
        self.plan = plan
        self.retriever = retriever
        self.language = language or plan.language or "English"
        self.preset_style = preset_style
        self.mode = mode
        self.idx = 0
        self.state = State.EXPLAIN
        self.runs: list[SegmentRun] = []
        self.log: list[Transition] = []
        self._streak = 0            # consecutive correct answers
        self._depth_bump = 0        # raised difficulty accumulated

    def _record(self, state: str, detail: dict):
        seg = self.current_segment
        self.log.append(
            Transition(
                t=time.time(),
                segment_index=self.idx,
                concept=seg.concept if seg else "-",
                state=state,
                detail=detail,
            )
        )

    @property
    def current_segment(self) -> Segment | None:
        if 0 <= self.idx < len(self.plan.segments):
            return self.plan.segments[self.idx]
        return None

    @property
    def current_run(self) -> SegmentRun | None:
        return self.runs[-1] if self.runs and self.runs[-1].index == self.idx else None

    @property
    def finished(self) -> bool:
        return self.state == State.DONE

    def _grounding(self, seg: Segment) -> str:
        if seg.source_quote:
            return f'Grounded source: "{seg.source_quote}" {seg.source_label or ""}'.strip()
        if self.retriever is not None and len(self.retriever):
            return "Grounded source:\n" + self.retriever.context_block(seg.concept, k=3)
        return "No source excerpt; rely on standard curriculum knowledge."

    def _lang_hint(self) -> str:
        lang = self.language
        if lang == "Hindi":
            return "Write in natural Hindi (Devanagari script)."
        elif lang == "Hinglish":
            return "Write in Hinglish — conversational Hindi in Latin script mixed with English scientific terms."
        elif lang == "Tamil":
            return "Write in natural Tamil (தமிழ் script), keeping scientific terms clear in English."
        elif lang in config.LANGUAGES:
            native = config.LANGUAGES[lang].get("native", lang)
            return f"Write in natural {lang} ({native} script), keeping scientific equations clear in English."
        return "Write in clear English."

    # ------------------------------------------------------------------ #
    # EXPLAIN
    # ------------------------------------------------------------------ #
    def explain(self) -> str:
        seg = self.current_segment
        assert seg is not None

        depth = seg.depth
        if self._depth_bump > 0:
            depth += f" (raised difficulty: include one subtle edge case or deeper mechanism)"

        bharat_directive = get_bharat_context_prompt_directive(self.language, self.preset_style)

        prompt = (
            f"{self._lang_hint()}\n"
            f"{bharat_directive}\n"
            f"Teach this concept to a student:\n"
            f"Concept: {seg.concept}\n"
            f"Target depth: {depth}\n"
            f"Anchor example: {seg.example or 'a tangible everyday real-world example'}\n"
            f"{self._grounding(seg)}\n\n"
            "Requirements:\n"
            "- Tone: warm, engaging, spoken conversational style (no bullet points, no markdown headers).\n"
            "- Length: 60-95 words.\n"
            "- Clear cause-and-effect relationship.\n"
            "- Integrate the everyday anchor naturally."
        )

        text = generate_text(prompt, tag="explain", temperature=0.7).strip()
        text = indianize_text(text)

        # Hallucination Shield Verification
        chunk_list = []
        if self.retriever:
            if hasattr(self.retriever, "search"):
                res = self.retriever.search(seg.concept, top_k=2)
                chunk_list = [(c if isinstance(c, Chunk) else c[0]) for c in res]
            elif hasattr(self.retriever, "retrieve"):
                res = self.retriever.retrieve(seg.concept, k=2)
                chunk_list = [h.chunk for h in res]
        grounding_rep = verify_grounding(text, chunk_list, source_label=seg.source_label)

        run = SegmentRun(
            index=self.idx,
            concept=seg.concept,
            explanation=text,
            language=self.language,
            grounding=grounding_rep.to_dict(),
        )
        self.runs.append(run)
        self.state = State.QUESTION
        self._record(
            State.EXPLAIN,
            {
                "words": len(text.split()),
                "language": self.language,
                "grounded": grounding_rep.is_grounded,
                "grounding_confidence": grounding_rep.confidence_score,
            },
        )
        return text

    # ------------------------------------------------------------------ #
    # STUDENT-INITIATED FOLLOW-UP / DOUBT INTERRUPT
    # ------------------------------------------------------------------ #
    def answer_student_question(self, student_question: str) -> dict[str, Any]:
        """Answer a student-initiated follow-up question while maintaining lesson context and state machine progress."""
        seg = self.current_segment
        concept = seg.concept if seg else "General STEM"
        current_exp = self.current_run.explanation if self.current_run else ""

        # Build curriculum context
        prior_concepts = [s.concept for s in self.plan.segments[:self.idx]]
        future_concepts = [s.concept for s in self.plan.segments[self.idx + 1:]]

        # Hybrid RAG retrieval tailored to student question + active concept
        chunk_list: list[Chunk] = []
        retrieved_context = ""
        if self.retriever:
            query = f"{concept} {student_question}"
            if hasattr(self.retriever, "search"):
                res = self.retriever.search(query, top_k=3)
                chunk_list = [(c if isinstance(c, Chunk) else c[0]) for c in res]
            elif hasattr(self.retriever, "retrieve"):
                res = self.retriever.retrieve(query, k=3)
                chunk_list = [h.chunk for h in res]
            if chunk_list:
                retrieved_context = "\n".join(f"[{c.source_label or c.doc_name}]: {c.text}" for c in chunk_list)

        bharat_directive = get_bharat_context_prompt_directive(self.language, self.preset_style)

        prompt = (
            f"{self._lang_hint()}\n"
            f"{bharat_directive}\n"
            f"You are BHARATGURU, an expert adaptive teacher. A student has asked a question during the lesson.\n\n"
            f"Active Concept Being Taught: {concept}\n"
            f"Current Segment Explanation: {current_exp}\n"
            f"Prior Covered Concepts: {', '.join(prior_concepts) if prior_concepts else 'Beginning of lesson'}\n"
            f"Upcoming Concepts: {', '.join(future_concepts) if future_concepts else 'End of lesson'}\n\n"
            f"Student Question: \"{student_question}\"\n\n"
            f"Grounded Source Passages:\n{retrieved_context or 'Standard curriculum foundational knowledge.'}\n\n"
            "Requirements:\n"
            "- Tone: Encouraging, spoken conversational teacher tone.\n"
            "- Directly resolve their doubt with conceptual clarity.\n"
            "- Anchor in a tangible everyday Indian example if relevant.\n"
            "- Connect back to the active lesson concept.\n"
            "- Length: 60-90 words.\n"
            "- No markdown headers or bullet points."
        )

        answer_text = generate_text(prompt, tag="explain", temperature=0.6).strip()
        answer_text = indianize_text(answer_text)

        # Grounding verification with Hallucination Shield
        grounding_rep = verify_grounding(
            answer_text,
            chunk_list,
            source_label=seg.source_label if seg else None,
        )

        # Record in transition audit log WITHOUT advancing self.idx or modifying self.state
        self._record(
            "FOLLOWUP",
            {
                "student_question": student_question,
                "answer_words": len(answer_text.split()),
                "grounded": grounding_rep.is_grounded,
                "grounding_confidence": grounding_rep.confidence_score,
                "preserved_state": self.state.value,
            },
        )

        return {
            "question": student_question,
            "answer": answer_text,
            "concept": concept,
            "grounding": grounding_rep.to_dict(),
            "source_label": seg.source_label if seg else None,
            "source_quote": seg.source_quote if seg else None,
            "preserved_state": self.state.value,
        }

    # ------------------------------------------------------------------ #
    # QUESTION
    # ------------------------------------------------------------------ #
    def question(self) -> str:
        seg = self.current_segment
        run = self.current_run
        assert seg and run

        if seg.checkpoint_question and not run.question:
            run.question = seg.checkpoint_question
            self.state = State.EVALUATE
            self._record(State.QUESTION, {"question": run.question, "pre_planned": True})
            return run.question

        style = "a multiple-choice question with 4 options labelled A-D" if self.idx % 2 == 0 else "a one-sentence short-answer question"
        prompt = (
            f"{self._lang_hint()}\n"
            f"The student was just taught: {run.explanation}\n\n"
            f"Write {style} that checks genuine conceptual understanding of '{seg.concept}' "
            "(not recall of wording). Output only the question."
        )
        run.question = generate_text(prompt, tag="question", temperature=0.5).strip()
        self.state = State.EVALUATE
        self._record(State.QUESTION, {"question": run.question})
        return run.question

    # ------------------------------------------------------------------ #
    # EVALUATE
    # ------------------------------------------------------------------ #
    def evaluate(self, answer: str, *, followup: bool = False) -> dict:
        seg = self.current_segment
        if not seg:
            raise ValueError(f"No active segment at index {self.idx}")
        run = self.current_run
        if not run:
            run = SegmentRun(
                index=self.idx,
                concept=seg.concept,
                explanation="",
                question=seg.checkpoint_question or f"Explain the core principle of {seg.concept}.",
            )
            self.runs.append(run)

        q = run.followup_question if followup else (run.question or seg.checkpoint_question or f"Explain {seg.concept}.")
        if followup:
            run.followup_answer = answer
        else:
            run.student_answer = answer

        run.attempts += 1

        prompt = (
            f"Concept under test: {seg.concept}\n"
            f"Question: {q}\n"
            f'Student answer: "{answer}"\n'
            "Grade it. Return the JSON object described above."
        )
        data = generate_json(prompt, tag="evaluate", system=_EVAL_SYS, temperature=0.2)
        verdict = str(data.get("verdict", "partial")).lower()
        if verdict not in ("correct", "partial", "incorrect"):
            verdict = "partial"
        run.verdict = verdict
        run.misconception = data.get("misconception")

        # Misconception Engine Fingerprinting
        fingerprint = None
        if verdict in ("incorrect", "partial"):
            fp = fingerprint_misconception(seg.concept, q, answer)
            fingerprint = fp.to_dict()
            run.fingerprint = fingerprint
            run.misconception = fp.misconception

        self._record(
            State.EVALUATE,
            {
                "followup": followup,
                "verdict": verdict,
                "misconception": run.misconception,
                "fingerprint": fingerprint,
                "answer": answer,
            },
        )
        self.state = State.ADAPT
        data["verdict"] = verdict
        data["fingerprint"] = fingerprint
        return data

    # ------------------------------------------------------------------ #
    # ADAPT
    # ------------------------------------------------------------------ #
    def adapt(self) -> dict:
        seg = self.current_segment
        run = self.current_run
        assert seg and run

        if run.verdict == "correct":
            self._streak += 1
            run.action = "advance"
            if self._streak >= 2:
                self._depth_bump += 1
                self._streak = 0
                detail = {"action": "advance", "note": "two correct in a row -> depth raised"}
            else:
                detail = {"action": "advance", "note": "correct -> next segment"}
            self._record(State.ADAPT, detail)
            return {"action": "advance", **detail}

        # Policy Selector: Choose targeted pedagogical strategy
        strat = select_adaptive_strategy(run.attempts, misconception=run.misconception, mode=self.mode)
        run.strategy = strat.value
        strat_instruction = STRATEGY_INSTRUCTIONS.get(strat, "")

        self._streak = 0
        run.action = "simplify" if run.verdict == "incorrect" else "reinforce"
        mis = run.misconception or "the student's reasoning was unclear"
        intervention = run.fingerprint.get("recommended_intervention", "") if run.fingerprint else ""

        bharat_directive = get_bharat_context_prompt_directive(self.language, self.preset_style)

        prompt = (
            f"{self._lang_hint()}\n"
            f"{bharat_directive}\n"
            f"{strat_instruction}\n"
            f"Concept: {seg.concept}\n"
            f"First explanation: {run.explanation}\n"
            f"Student Misconception Fingerprint: {mis}\n"
            f"Prescribed Intervention: {intervention}\n"
            f"{self._grounding(seg)}\n\n"
            "Re-teach in 70-110 words applying this strategy and explicitly resolving the misconception. "
            "Spoken conversational style, no headers."
        )
        run.reexplanation = generate_text(prompt, tag="reexplain", temperature=0.7).strip()
        run.reexplanation = indianize_text(run.reexplanation)

        fq_prompt = (
            f"{self._lang_hint()}\n"
            f"Re-explanation: {run.reexplanation}\n"
            f"Write ONE new short-answer checkpoint question about '{seg.concept}', related "
            "to but not identical to the earlier one. Output only the question."
        )
        run.followup_question = generate_text(fq_prompt, tag="question", temperature=0.5).strip()

        self._record(
            State.ADAPT,
            {
                "action": run.action,
                "strategy": run.strategy,
                "misconception": mis,
                "reexplanation_words": len(run.reexplanation.split()),
                "followup_question": run.followup_question,
            },
        )
        self.state = State.EVALUATE
        return {
            "action": run.action,
            "strategy": run.strategy,
            "reexplanation": run.reexplanation,
            "followup_question": run.followup_question,
            "fingerprint": run.fingerprint,
        }

    # ------------------------------------------------------------------ #
    def advance(self) -> bool:
        """Move to the next segment. Returns False when the lesson is over."""
        self.idx += 1
        if self.idx >= len(self.plan.segments):
            self.state = State.DONE
            self._record(State.DONE, {"segments_taught": len(self.runs)})
            return False
        self.state = State.EXPLAIN
        return True

    # ------------------------------------------------------------------ #
    def set_language(self, language: str):
        """Switch teaching language mid-lesson without losing segment position."""
        if language in config.LANGUAGES:
            self.language = language
            self._record("LANG_SWITCH", {"new_language": language, "position": self.idx})

    def score_summary(self) -> dict:
        correct = sum(1 for r in self.runs if r.verdict == "correct")
        total = len(self.runs)
        weak = [r.concept for r in self.runs if r.verdict != "correct"]
        return {"correct": correct, "total": total, "weak": weak}

    def log_rows(self) -> list[dict]:
        return [asdict(t) for t in self.log]


def run_segment(
    session: TeachingSession,
    answer_fn=None,
) -> SegmentRun:
    """Helper to run through explain -> question -> answer -> adapt for one segment."""
    session.explain()
    q = session.question()
    ans = answer_fn(q) if answer_fn else "It is the rate of flow of charge."
    eval_res = session.evaluate(ans)
    if eval_res.get("verdict") != "correct":
        adapt_res = session.adapt()
        fq = adapt_res.get("followup_question", q)
        f_ans = answer_fn(fq) if answer_fn else "It decreases, current is inversely proportional to resistance."
        session.evaluate(f_ans, followup=True)
    session.advance()
    return session.runs[-1]
