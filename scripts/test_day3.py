"""Day 3 checklist: full lesson end-to-end -> quiz -> report (their format) ->
profile store carrying progress between sessions -> next-topic recommendation.
Runs both required scenarios (uploaded PDF/text + topic-only).

    python scripts/test_day3.py            # no videos (fast)
    python scripts/test_day3.py --video    # also renders MP4s
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
from src.pipeline import build_lesson, run_full_lesson, save_run_artifacts  # noqa: E402
from src.profile_store import ProfileStore  # noqa: E402

SAMPLE = config.SAMPLE_DIR / "electricity_chapter.txt"
MAKE_VIDEO = "--video" in sys.argv


def main() -> None:
    db = config.WORKDIR / "test_profiles.sqlite3"
    if db.exists():
        db.unlink()
    store = ProfileStore(db)

    print("== Scenario A: uploaded material, beginner, Hindi, 20 min, one wrong answer ==")
    ctx_a = build_lesson(
        topic="Chapter 4: Electricity",
        instruction_text="I am a beginner, teach me Chapter 4 in 20 minutes, in Hindi, with simple examples",
        upload_paths=[SAMPLE],
    )
    res_a = run_full_lesson(ctx_a, student="asha", language="Hindi",
                            wrong_on_indices=(2,), make_videos=MAKE_VIDEO, store=store)
    print("\n--- REPORT A ---")
    print(res_a["report_text"])
    print("next topic:", res_a["next_topic"])
    save_run_artifacts(res_a, config.WORKDIR / "run_scenario_a.json")

    assert res_a["grounded"] is True
    assert res_a["report"]["needs_improvement"], "a wrong answer should surface a weak area"
    assert len(res_a["segments_taught"]) >= 3
    if MAKE_VIDEO:
        assert res_a["lesson_video"] and Path(res_a["lesson_video"]).exists()

    print("\n== Scenario B: topic only, English, no upload ==")
    ctx_b = build_lesson(
        topic="Photosynthesis",
        instruction_text="Explain photosynthesis to a class 7 student in English, 5 minutes",
    )
    res_b = run_full_lesson(ctx_b, student="asha", language="English",
                            wrong_on_indices=(), make_videos=False, store=store)
    print("\n--- REPORT B ---")
    print(res_b["report_text"])
    print("next topic:", res_b["next_topic"])
    assert res_b["grounded"] is False

    print("\n== Progress carried between sessions ==")
    prof = store.profile("asha")
    print("  sessions:", prof["sessions"])
    print("  topics_studied:", prof["topics_studied"])
    print("  recurring_weak:", prof["recurring_weak"])
    assert prof["sessions"] == 2
    rec = store.recommend_next_topic("asha", "Photosynthesis")
    print("  recommendation:", rec)

    store.close()
    print("\nDAY 3 OK")


if __name__ == "__main__":
    main()
