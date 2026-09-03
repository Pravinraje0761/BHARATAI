"""End-of-lesson quiz generation, scoring, and the learner report."""
from __future__ import annotations

from dataclasses import dataclass, field

from src.lesson_planner import LessonPlan
from src.llm import generate_json


@dataclass
class QuizQuestion:
    type: str            # "mcq" | "short"
    concept: str
    question: str
    answer: str
    options: list[str] = field(default_factory=list)


@dataclass
class QuizResult:
    question: QuizQuestion
    student_answer: str
    verdict: str         # correct | partial | incorrect
    score: float         # 0.0 - 1.0
    feedback: str = ""


_QUIZ_SYS = (
    "You write short formative quizzes strictly limited to concepts the student "
    "was actually taught. Output only JSON."
)
_GRADE_SYS = (
    "You grade one quiz answer. Output only JSON: "
    '{"verdict":"correct"|"partial"|"incorrect","score":0..1,"feedback":str}.'
)
_REPORT_SYS = (
    "You write a concise learner report. Output only JSON with keys: topic, "
    "score, strong_areas, needs_improvement, recommendation."
)


def generate_quiz(plan: LessonPlan, taught_concepts: list[str], n: int | None = None) -> list[QuizQuestion]:
    n = n or max(3, min(6, len(taught_concepts) + 1))
    prompt = (
        f"Lesson: {plan.title} (level {plan.level}, language {plan.language})\n"
        f"Concepts taught this session: {taught_concepts}\n\n"
        f"Write {n} questions, mixing 'mcq' (4 options) and 'short'. JSON:\n"
        '{ "questions": [ {"type":"mcq"|"short","concept":str,"question":str,'
        '"options":[str,...] ,"answer":str} ] }\n'
        "Only use the concepts listed above."
    )
    data = generate_json(prompt, tag="quiz", system=_QUIZ_SYS, temperature=0.5)
    out = []
    for q in data.get("questions", [])[:n]:
        out.append(
            QuizQuestion(
                type=q.get("type", "short"),
                concept=q.get("concept", taught_concepts[0] if taught_concepts else "topic"),
                question=q.get("question", ""),
                answer=q.get("answer", ""),
                options=q.get("options", []) or [],
            )
        )
    return [q for q in out if q.question]


def grade_answer(q: QuizQuestion, student_answer: str) -> QuizResult:
    sa = (student_answer or "").strip()
    if not sa:
        return QuizResult(q, sa, "incorrect", 0.0, "No answer given.")

    if q.type == "mcq" and q.answer:
        # exact / letter / substring match before spending an LLM call
        norm = sa.lower().strip().rstrip(".")
        ans = q.answer.lower().strip()
        letters = {chr(ord("a") + i): opt.lower() for i, opt in enumerate(q.options)}
        if norm == ans or letters.get(norm) == ans or norm in ans or ans in norm:
            return QuizResult(q, sa, "correct", 1.0, "Correct.")

    prompt = (
        f"Question ({q.type}): {q.question}\n"
        f"Reference answer: {q.answer}\n"
        + (f"Options: {q.options}\n" if q.options else "")
        + f'Student answer: "{sa}"\nGrade it.'
    )
    data = generate_json(prompt, tag="grade_quiz", system=_GRADE_SYS, temperature=0.1)
    verdict = str(data.get("verdict", "partial")).lower()
    if verdict not in ("correct", "partial", "incorrect"):
        verdict = "partial"
    try:
        score = float(data.get("score", {"correct": 1.0, "partial": 0.5, "incorrect": 0.0}[verdict]))
    except Exception:
        score = {"correct": 1.0, "partial": 0.5, "incorrect": 0.0}[verdict]
    return QuizResult(q, sa, verdict, max(0.0, min(1.0, score)), data.get("feedback", ""))


def build_report(plan: LessonPlan, results: list[QuizResult], session_weak: list[str] | None = None) -> dict:
    total = sum(r.score for r in results)
    out_of = len(results)
    by_concept: dict[str, list[float]] = {}
    for r in results:
        by_concept.setdefault(r.question.concept, []).append(r.score)
    strong = [c for c, v in by_concept.items() if sum(v) / len(v) >= 0.75]
    weak = [c for c, v in by_concept.items() if sum(v) / len(v) < 0.5]
    for c in session_weak or []:
        if c not in weak and c not in strong:
            weak.append(c)

    prompt = (
        f"Topic: {plan.title}\n"
        f"Raw score: {total:.1f} / {out_of}\n"
        f"Per-concept scores: "
        f"{ {c: round(sum(v)/len(v),2) for c,v in by_concept.items()} }\n"
        f"Concepts the student struggled with during teaching: {session_weak or []}\n\n"
        "Return JSON: topic, score (\"X/Y\" string), strong_areas (list), "
        "needs_improvement (list), recommendation (one concrete sentence)."
    )
    data = generate_json(prompt, tag="report", system=_REPORT_SYS, temperature=0.3)

    return {
        "topic": data.get("topic", plan.title),
        "score": data.get("score", f"{total:.1f}/{out_of}"),
        "strong_areas": data.get("strong_areas") or strong or ["-"],
        "needs_improvement": data.get("needs_improvement") or weak or ["-"],
        "recommendation": data.get(
            "recommendation",
            "Revise the weak concepts with two worked examples each, then re-test.",
        ),
        "raw_score": total,
        "out_of": out_of,
    }


def format_report(report: dict) -> str:
    lines = [
        f"Topic: {report['topic']}",
        f"Score: {report['score']}",
        f"Strong areas: {', '.join(report['strong_areas'])}",
        f"Needs improvement: {', '.join(report['needs_improvement'])}",
        f"Recommendation: {report['recommendation']}",
    ]
    return "\n".join(lines)
