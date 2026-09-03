"""Day 2 checklist: EXPLAIN->QUESTION->EVALUATE->ADAPT loop, wrong-answer
re-explanation, multilingual render, mid-lesson language switch, TTS, and one
segment exported as a real MP4 (avatar + voice + slide + captions).

    python scripts/test_day2.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
from src.lesson_planner import make_lesson_plan, parse_instruction  # noqa: E402
from src.ingestion import ingest  # noqa: E402
from src.pipeline import render_segment_media  # noqa: E402
from src.pipeline import LessonContext  # noqa: E402
from src.retrieval import build_retriever  # noqa: E402
from src.teaching import State, TeachingSession  # noqa: E402

SAMPLE = config.SAMPLE_DIR / "electricity_chapter.txt"


def main() -> None:
    chunks = ingest(SAMPLE)
    retr = build_retriever(chunks)
    instr = parse_instruction("beginner, 20 minutes, English, simple examples")
    plan = make_lesson_plan("Chapter 4: Electricity", instr, retr)
    # jump to the Ohm's-law segment for the misconception demo
    ohm_idx = max(
        range(len(plan.segments)),
        key=lambda i: ("ohm" in plan.segments[i].concept.lower())
        or ("resist" in plan.segments[i].concept.lower()),
    )

    print("== [1] Teaching loop with a deliberately WRONG answer ==")
    s = TeachingSession(plan, retr, language="English")
    s.idx = ohm_idx
    s.state = State.EXPLAIN
    exp1 = s.explain()
    print(f"  EXPLAIN ({len(exp1.split())}w): {exp1[:110]}...")
    q1 = s.question()
    print(f"  QUESTION: {q1}")
    ev = s.evaluate("The current increases.")
    print(f"  EVALUATE: verdict={ev['verdict']} misconception={ev.get('misconception')}")
    assert ev["verdict"] in ("incorrect", "partial")
    ad = s.adapt()
    print(f"  ADAPT: action={ad['action']}")
    print(f"  RE-EXPLAIN: {ad['reexplanation'][:110]}...")
    assert ad["reexplanation"] and ad["reexplanation"] != exp1, "re-explanation must differ"
    print(f"  FOLLOW-UP Q: {ad['followup_question']}")
    s.evaluate("It goes down, current is inversely proportional to resistance.", followup=True)
    print(f"  FOLLOW-UP verdict: {s.current_run.verdict}")

    print("\n== [2] Multilingual: same segment in EN / HI / Hinglish ==")
    for lang in ("English", "Hindi", "Hinglish"):
        s2 = TeachingSession(plan, retr, language=lang)
        s2.idx = ohm_idx
        s2.state = State.EXPLAIN
        txt = s2.explain()
        print(f"  [{lang}] {txt[:90]}...")

    print("\n== [3] Mid-lesson language switch keeps position + score ==")
    s3 = TeachingSession(plan, retr, language="English")
    s3.explain(); s3.question(); s3.evaluate("a good answer"); s3.adapt()
    pos_before, log_before = s3.idx, len(s3.log)
    s3.set_language("Hindi")
    assert s3.idx == pos_before and len(s3.log) == log_before + 1
    assert len(s3.runs) >= 1
    print(f"  position preserved at segment {s3.idx}; language now {s3.language}")

    print("\n== [4] One segment -> real MP4 (EN + HI) ==")
    ctx = LessonContext(topic="Chapter 4: Electricity", instruction=instr,
                        plan=plan, retriever=retr)
    for lang in ("English", "Hindi"):
        media = render_segment_media(ctx, ohm_idx, exp1, lang,
                                     workdir=config.WORKDIR / "day2_media")
        vp = Path(media["video"])
        print(f"  [{lang}] audio={Path(media['audio']).name}  video={vp.name} "
              f"({vp.stat().st_size // 1024} KB)")
        assert vp.exists() and vp.stat().st_size > 10_000

    print("\n== [5] Transition log captured ==")
    for row in s.log_rows():
        print("  ", row)

    print("\nDAY 2 OK")


if __name__ == "__main__":
    main()
