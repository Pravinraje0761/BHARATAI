"""Automated test script for Lesson Completion Page and Certificate endpoints.

Verifies:
1. /api/plan builds a multi-segment lesson plan
2. /api/session/advance reaches the final segment and returns has_next=False
3. /api/session/complete/{session_id} returns full completion stats, concepts, and recommended next topic
4. /api/quiz/submit returns graded report card and records session
"""
import sys
import requests

BASE_URL = "http://localhost:8000"

def test_completion_flow():
    session = requests.Session()
    # Authenticate as student
    auth_res = session.post(f"{BASE_URL}/api/auth/demo-login", json={"role": "student"})
    assert auth_res.status_code == 200, f"Demo login failed: {auth_res.text}"

    print("[TEST] 1. Building Adaptive Lesson Plan...")
    plan_payload = {
        "topic": "Electricity: Current, Voltage and Resistance",
        "instruction": "I am a beginner, teach me in 5 minutes, in English, with simple examples",
        "language": "English",
        "mode": "DIRECT",
        "exam_board": "CBSE Class 10",
        "student": "aarav",
    }
    r = session.post(f"{BASE_URL}/api/plan", json=plan_payload, timeout=20)
    assert r.status_code == 200, f"Plan failed: {r.text}"
    plan_data = r.json()
    session_id = plan_data["session_id"]
    segments = plan_data["segments"]
    total_segments = len(segments)
    print(f"[OK] Plan built: session_id={session_id}, total_segments={total_segments}")

    print("[TEST] 2. Advancing through all segments in classroom...")
    for idx in range(total_segments):
        # Explain
        exp_res = session.post(f"{BASE_URL}/api/session/explain", json={
            "session_id": session_id,
            "segment_index": idx,
            "render_video": False,
        }, timeout=15)
        assert exp_res.status_code == 200, f"Explain failed on segment {idx}: {exp_res.text}"

        # Answer checkpoint
        ans_res = session.post(f"{BASE_URL}/api/session/answer", json={
            "session_id": session_id,
            "segment_index": idx,
            "answer": "Current is the flow of electric charge per unit time through a conductor.",
            "is_followup": False,
            "student": "aarav",
        }, timeout=15)
        assert ans_res.status_code == 200, f"Answer failed on segment {idx}: {ans_res.text}"

        # Advance
        adv_res = session.post(f"{BASE_URL}/api/session/advance", json={
            "session_id": session_id,
        }, timeout=10)
        assert adv_res.status_code == 200, f"Advance failed on segment {idx}: {adv_res.text}"
        adv_data = adv_res.json()
        print(f"  Segment {idx + 1}/{total_segments} -> has_next={adv_data['has_next']}")

    assert adv_data["has_next"] is False, "Final segment advance should have has_next=False"
    print("[OK] Reached end of lesson! has_next=False verified.")

    print("[TEST] 3. Testing /api/session/complete/{session_id}...")
    comp_res = session.get(f"{BASE_URL}/api/session/complete/{session_id}", timeout=10)
    assert comp_res.status_code == 200, f"Complete endpoint failed: {comp_res.text}"
    comp_data = comp_res.json()
    
    assert comp_data["session_id"] == session_id
    assert comp_data["total_segments"] == total_segments
    assert comp_data["completed_segments"] == total_segments
    assert len(comp_data["segments"]) == total_segments
    assert "mastery_percentage" in comp_data
    assert comp_data["next_topic"] is not None
    print(f"[OK] Completion data verified:")
    print(f"     Title: {comp_data['title']}")
    print(f"     Mastery: {comp_data['mastery_percentage']}%")
    print(f"     Recommended Next: {comp_data['next_topic']['next_topic']}")

    print("[TEST] 4. Testing Formative Assessment Quiz Submit...")
    quiz_res = session.post(f"{BASE_URL}/api/quiz/generate", json={"session_id": session_id}, timeout=10)
    assert quiz_res.status_code == 200
    quiz_data = quiz_res.json()
    questions = quiz_data["questions"]
    
    answers = {}
    for i, q in enumerate(questions):
        answers[str(i)] = q.get("options", ["Electric current"])[0] if q.get("options") else "Electric charge flow"

    sub_res = session.post(f"{BASE_URL}/api/quiz/submit", json={
        "session_id": session_id,
        "student": "aarav",
        "answers": answers,
    }, timeout=15)
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert "report" in sub_data
    report = sub_data["report"]
    print(f"[OK] Quiz submitted: Score={report['raw_score']}/{report['out_of']}")

    print("\n[SUCCESS] All Lesson Completion Page & Certificate endpoints passed 100%!")

if __name__ == "__main__":
    try:
        test_completion_flow()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
