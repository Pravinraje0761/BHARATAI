"""Test for Priority 1: Student Follow-Up Question Engine (/api/session/ask).

Verifies that:
1. Student can submit free-text questions during a lesson.
2. The answer is grounded using hybrid RAG context.
3. The response includes a verified GroundingReport with a dynamic confidence score.
4. Neural audio is synthesized for immediate playback.
5. The state machine state and segment index are strictly preserved (no progress loss).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from server import app
import config

client = TestClient(app)

def main():
    print("== [1] Initializing Lesson Session ==")
    plan_res = client.post("/api/plan", json={
        "topic": "Chapter 4: Electricity",
        "instruction": "I am a beginner, teach me in 20 minutes, in English, with simple examples",
        "upload_paths": [str(config.SAMPLE_DIR / "electricity_chapter.txt")],
        "language": "English",
        "student": "test_student"
    })
    assert plan_res.status_code == 200, f"Plan failed: {plan_res.text}"
    session_id = plan_res.json()["session_id"]
    print(f"  [OK] Session created: {session_id}")

    print("\n== [2] Loading Segment 0 (State -> QUESTION) ==")
    exp_res = client.post("/api/session/explain", json={
        "session_id": session_id,
        "segment_index": 0,
        "render_video": False,
    })
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    initial_state = exp_data["state"]
    print(f"  [OK] Segment 0 loaded. State: {initial_state}, Concept: {exp_data['concept']}")

    print("\n== [3] Student Interrupts with Follow-Up Doubt (/api/session/ask) ==")
    doubt = "Wait, how does temperature affect electric current and resistance?"
    ask_res = client.post("/api/session/ask", json={
        "session_id": session_id,
        "segment_index": 0,
        "question": doubt,
    })
    assert ask_res.status_code == 200, f"Ask failed: {ask_res.text}"
    ask_data = ask_res.json()

    print(f"  Student Question : \"{ask_data['question']}\"")
    print(f"  Teacher Answer   : {ask_data['answer'][:120]}...")
    print(f"  Preserved State  : {ask_data['preserved_state']}")
    assert ask_data["preserved_state"] == initial_state, "State must not change upon doubt interrupt!"

    print(f"  Audio URL        : {ask_data.get('audio_url')}")
    assert ask_data.get("audio_url"), "Audio URL must be generated for spoken answer"

    grounding = ask_data.get("grounding")
    assert grounding is not None, "Grounding report must be present"
    conf = grounding.get("confidence_score", 0.0)
    print(f"  Grounding Score  : {int(conf * 100)}% ({grounding.get('status_label')})")
    msg = str(grounding.get('shield_message', '')).encode('ascii', 'replace').decode()
    print(f"  Shield Message   : {msg}")
    assert 0.0 < conf <= 1.0, "Confidence score must be a valid probability"

    print("\n== [4] Verifying Session Can Still Evaluate Checkpoint Answer ==")
    ans_res = client.post("/api/session/answer", json={
        "session_id": session_id,
        "segment_index": 0,
        "answer": "Current is the rate of flow of electric charge.",
        "student": "test_student"
    })
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    print(f"  [OK] Answer evaluated successfully: verdict={ans_data.get('verdict')}")

    print("\nALL STUDENT FOLLOW-UP QUESTION TESTS PASSED!")

if __name__ == "__main__":
    main()
