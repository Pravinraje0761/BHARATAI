"""Automated test suite for Firebase Cloud Backend & Authentication Integration."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from server import app
from src.firebase_backend import get_firebase_backend

client = TestClient(app)


def test_firebase_backend_unit():
    print("== [1] Testing FirebaseBackend Core Module ==")
    fb = get_firebase_backend()

    # 1. Config & Status
    cfg = fb.get_public_config()
    assert "apiKey" in cfg
    assert "projectId" in cfg
    assert "measurementId" in cfg
    assert cfg["projectId"] == "bharat-ai-47b02"
    assert cfg["measurementId"] == "G-E8H1KTTB6B"
    print(f"  [OK] Firebase public Web config verified (projectId={cfg['projectId']}, measurementId={cfg['measurementId']})")

    status = fb.get_status()
    assert "configured" in status
    assert "admin_sdk_active" in status
    print(f"  [OK] Firebase status report verified (configured={status['configured']}, admin_sdk={status['admin_sdk_active']})")

    # 2. Token verification
    decoded = fb.verify_firebase_id_token("demo_firebase_token_for_student")
    assert decoded["email"] == "demo.student@bharatguru.firebase.io"
    assert "uid" in decoded
    print(f"  [OK] Firebase ID token verification pipeline passed (user={decoded['name']})")

    # 3. Invalid token rejection
    try:
        fb.verify_firebase_id_token("")
        assert False, "Should raise on empty token"
    except ValueError:
        print("  [OK] Rejection of empty/invalid Firebase token passed")


def test_firebase_api_endpoints():
    print("\n== [2] Testing Firebase REST Endpoints on FastAPI ==")

    # 1. GET /api/firebase/config
    res = client.get("/api/firebase/config")
    assert res.status_code == 200
    cfg = res.json()
    assert "apiKey" in cfg
    print("  [OK] GET /api/firebase/config passed")

    # 2. GET /api/firebase/status
    res = client.get("/api/firebase/status")
    assert res.status_code == 200
    st = res.json()
    assert "configured" in st
    print("  [OK] GET /api/firebase/status passed")

    # 3. POST /api/auth/firebase-login (Google Sign-In simulation for Student)
    res = client.post("/api/auth/firebase-login", json={
        "id_token": "demo_firebase_token_for_student",
        "role": "student",
        "grade_or_board": "CBSE Class 10",
        "preferred_language": "Hindi",
    })
    assert res.status_code == 200
    login_data = res.json()
    assert login_data["success"] is True
    assert "token" in login_data
    assert login_data["user"]["role"] == "student"
    stu_token = login_data["token"]
    print(f"  [OK] POST /api/auth/firebase-login (Student) passed (username={login_data['user']['username']})")

    # Verify session token works with /api/auth/me
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {stu_token}"})
    assert res.status_code == 200
    me = res.json()
    assert me["user"]["email"] == "demo.student@bharatguru.firebase.io"
    print("  [OK] Firebase-issued bearer session validated on /api/auth/me")

    # 4. POST /api/auth/firebase-login (Google Sign-In simulation for Teacher)
    res = client.post("/api/auth/firebase-login", json={
        "id_token": "demo_firebase_token_for_teacher",
        "role": "teacher",
        "grade_or_board": "Physics Faculty",
        "preferred_language": "English",
    })
    assert res.status_code == 200
    tea_data = res.json()
    assert tea_data["user"]["role"] == "teacher"
    print(f"  [OK] POST /api/auth/firebase-login (Teacher) passed (username={tea_data['user']['username']})")

    # 5. POST /api/firebase/sync
    res = client.post("/api/firebase/sync", json={
        "collection": "students",
        "student": "demo_student",
        "data": {"concepts_mastered": 5, "average_score": 85},
    })
    assert res.status_code == 200
    sync_res = res.json()
    assert "status" in sync_res
    print(f"  [OK] POST /api/firebase/sync passed (status={sync_res['status']})")

    print("\nALL FIREBASE INTEGRATION TESTS PASSED SUCCESSFULLY! [OK]")


if __name__ == "__main__":
    test_firebase_backend_unit()
    test_firebase_api_endpoints()
