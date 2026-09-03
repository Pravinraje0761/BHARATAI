"""Test suite for server.py FastAPI endpoints."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


def main():
    print("== [1] Testing / (Stitch Frontend index.html) ==")
    res = client.get("/")
    assert res.status_code == 200
    assert "BHARATGURU" in res.text or "Bharat" in res.text
    print("  [OK] Static Stitch index.html served successfully")

    print("\n== [2] Testing /api/sample-files ==")
    res = client.get("/api/sample-files")
    assert res.status_code == 200
    data = res.json()
    samples = data if isinstance(data, list) else data.get("samples", [])
    assert len(samples) >= 1
    sample_path = samples[0]["path"]
    print(f"  [OK] Sample file available: {samples[0]['name']}")

    print("\n== [3] Testing /api/plan (Lesson Planner API) ==")
    plan_payload = {
        "topic": "Chapter 4: Electricity",
        "instruction": "I am a beginner, teach me Chapter 4 in 20 minutes, in Hindi, with simple examples",
        "upload_paths": [sample_path],
        "language": "Hindi"
    }
    res = client.post("/api/plan", json=plan_payload)
    assert res.status_code == 200
    plan_data = res.json()
    sid = plan_data["session_id"]
    assert sid
    assert len(plan_data["segments"]) >= 3
    print(f"  [OK] Lesson plan generated (session={sid}, {len(plan_data['segments'])} segments)")

    print("\n== [4] Testing /api/session/explain (Explanation & Checkpoint) ==")
    res = client.post("/api/session/explain", json={
        "session_id": sid,
        "segment_index": 0,
        "render_video": False
    })
    assert res.status_code == 200
    exp_data = res.json()
    assert exp_data["explanation"]
    assert exp_data["question"]
    print(f"  [OK] Explanation & Question retrieved for segment 0")

    print("\n== [5] Testing /api/session/answer (Misconception Diagnosis) ==")
    # Wrong answer deliberately
    res = client.post("/api/session/answer", json={
        "session_id": sid,
        "segment_index": 0,
        "answer": "The current increases.",
        "is_followup": False
    })
    assert res.status_code == 200
    ans_data = res.json()
    print(f"  [OK] Evaluator verdict: {ans_data['verdict']}, misconception: {ans_data.get('misconception')}")

    print("\n== [6] Testing /api/session/adapt (Adaptive Re-explanation) ==")
    res = client.post("/api/session/adapt", json={
        "session_id": sid,
        "segment_index": 0,
        "render_video": False
    })
    assert res.status_code == 200
    adapt_data = res.json()
    assert adapt_data["reexplanation"]
    assert adapt_data["followup_question"]
    print(f"  [OK] Adaptation triggered: {adapt_data['action']} with new analogy & follow-up question")

    print("\n== [7] Testing /api/quiz/generate & /api/quiz/submit ==")
    res = client.post("/api/quiz/generate", json={"session_id": sid})
    assert res.status_code == 200
    quiz_data = res.json()
    assert len(quiz_data["questions"]) >= 1
    print(f"  [OK] Quiz generated with {len(quiz_data['questions'])} questions")

    res = client.post("/api/quiz/submit", json={
        "session_id": sid,
        "student": "test_student",
        "answers": {"0": "Sample answer"}
    })
    assert res.status_code == 200
    sub_data = res.json()
    assert "report" in sub_data
    assert "next_topic" in sub_data
    next_top = str(sub_data['next_topic']['next_topic']).encode('ascii', 'replace').decode()
    print(f"  [OK] Quiz graded & report recorded. Recommended next: {next_top}")

    print("\n== [8] Testing /api/profile/test_student ==")
    res = client.get("/api/profile/test_student")
    assert res.status_code == 200
    prof_data = res.json()
    assert prof_data["total_sessions"] >= 1
    print(f"  [OK] Student profile verified: {prof_data['total_sessions']} session(s)")

    print("\nALL SERVER & STITCH FRONTEND API TESTS PASSED!")


if __name__ == "__main__":
    main()
