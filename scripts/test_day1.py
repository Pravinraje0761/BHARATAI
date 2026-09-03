"""Day 1 checklist: ingestion -> cited chunks -> retrieval -> lesson plan
(both uploaded-material and topic-only), plus the instruction parser.

    python scripts/test_day1.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
from src.ingestion import ingest  # noqa: E402
from src.lesson_planner import make_lesson_plan, parse_instruction  # noqa: E402
from src.llm import health_check  # noqa: E402
from src.retrieval import build_retriever  # noqa: E402

SAMPLE = config.SAMPLE_DIR / "electricity_chapter.txt"
HINDI_INSTRUCTION = (
    "I am a beginner, teach me Chapter 4 in 20 minutes, in Hindi, with simple examples"
)


def main() -> None:
    print("== LLM engine ==")
    print(" ", health_check())

    print("\n== [1] Ingestion -> cited chunks ==")
    chunks = ingest(SAMPLE)
    print(f"  {len(chunks)} chunks from {SAMPLE.name}")
    for c in chunks[:3]:
        print(f"   {c.citation()}  {c.text[:90]}...")
    assert all(c.source_label for c in chunks), "every chunk must carry a source label"

    print("\n== [2] Retrieval (correctly cited) ==")
    retr = build_retriever(chunks)
    hits = retr.retrieve("what is Ohm's law", k=3)
    for h in hits:
        print(f"   score={h.score:.3f}  {h.chunk.citation()}  {h.chunk.text[:80]}...")
    assert "ohm" in hits[0].chunk.text.lower(), "top hit should be the Ohm's-law section"

    print("\n== [3] Instruction parser ==")
    instr = parse_instruction(HINDI_INSTRUCTION)
    print(f"   {instr}")
    assert instr.language == "Hindi"
    assert instr.time_minutes == 20
    assert instr.level == "beginner"

    print("\n== [4] Lesson plan from UPLOADED material (cited) ==")
    plan_a = make_lesson_plan("Chapter 4: Electricity", instr, retr)
    print(f"   title: {plan_a.title}  | grounded={plan_a.grounded} | {len(plan_a)} segments")
    for s in plan_a.segments:
        print(f"     - {s.concept}  (cite: {s.source_label})  ex: {s.example[:50]}")
    assert plan_a.grounded and len(plan_a) >= 3

    print("\n== [5] Lesson plan from TOPIC ONLY (no upload) ==")
    instr_b = parse_instruction("Teach me Newton's Laws to a Class 8 student")
    plan_b = make_lesson_plan("Newton's Laws of Motion", instr_b, None)
    print(f"   title: {plan_b.title}  | grounded={plan_b.grounded} | {len(plan_b)} segments")
    for s in plan_b.segments:
        print(f"     - {s.concept}")
    assert not plan_b.grounded and len(plan_b) >= 3

    print("\nDAY 1 OK")


if __name__ == "__main__":
    main()
