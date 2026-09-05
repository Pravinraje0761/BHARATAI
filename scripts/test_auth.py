"""Test suite for SQLite Authentication Engine & API endpoints."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from src.auth import AuthStore, get_auth_store


def test_auth_store():
    print("== [1] Testing AuthStore Initialization & Demo Accounts ==")
    store = AuthStore()
    
    # 1. Verify demo student
    aarav = store.get_user_by_username("aarav")
    assert aarav is not None, "Demo student 'aarav' should exist"
    assert aarav["role"] == "student"
    assert "password_hash" not in aarav
    print("  [OK] Demo student 'aarav' verified")

    # 2. Verify demo teacher
    priya = store.get_user_by_username("priya")
    assert priya is not None, "Demo teacher 'priya' should exist"
    assert priya["role"] == "teacher"
    print("  [OK] Demo teacher 'priya' verified")

    # 3. Verify authentication of demo account
    auth_aarav = store.authenticate_user("aarav", "student123")
    assert auth_aarav is not None, "Authentication for aarav should succeed"
    print("  [OK] Password authentication passed for aarav")

    wrong = store.authenticate_user("aarav", "wrong_password")
    assert wrong is None, "Wrong password must be rejected"
    print("  [OK] Rejection of invalid password passed")

    # 4. Token issuance & verification
    token = store.create_session(auth_aarav["id"])
    assert token and len(token) > 20
    user_by_token = store.get_user_by_token(token)
    assert user_by_token is not None
    assert user_by_token["username"] == "aarav"
    print("  [OK] Session token issuance and verification passed")

    # 5. User registration
    import uuid
    test_user = f"student_{uuid.uuid4().hex[:6]}"
    test_email = f"{test_user}@bharatguru.edu"
    new_user = store.register_user(
        username=test_user,
        email=test_email,
        password="securepassword123",
        full_name="New Student Learner",
        role="student",
        grade_or_board="JEE Main & Advanced",
        preferred_language="Hindi",
    )
    assert new_user["username"] == test_user
    assert new_user["grade_or_board"] == "JEE Main & Advanced"
    assert new_user["preferred_language"] == "Hindi"
    print(f"  [OK] Registered new user '{test_user}' successfully")

    # 6. Session invalidation (logout)
    store.invalidate_session(token)
    assert store.get_user_by_token(token) is None, "Session token should be invalidated"
    print("  [OK] Session logout/invalidation passed")

    print("\nALL AUTH UNIT TESTS PASSED SUCCESSFULLY! [OK]")


def test_api_endpoints():
    print("\n== [2] Testing FastAPI Authentication Endpoints ==")
    from fastapi.testclient import TestClient
    from server import app
    client = TestClient(app)

    # 1. Health & Backend status
    res = client.get("/api/backend/status")
    assert res.status_code == 200
    b_data = res.json()
    assert b_data["free_tier"] is True
    print(f"  [OK] /api/backend/status passed (LLM={b_data['active_llm']})")

    # 2. 1-Click Demo Login (Student)
    res = client.post("/api/auth/demo-login", json={"role": "student"})
    assert res.status_code == 200
    stu_login = res.json()
    assert stu_login["success"] is True
    assert stu_login["user"]["role"] == "student"
    stu_token = stu_login["token"]
    print("  [OK] /api/auth/demo-login (student) passed")

    # 3. /api/auth/me with Bearer token
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {stu_token}"})
    assert res.status_code == 200
    me_data = res.json()
    assert me_data["user"]["username"] == stu_login["user"]["username"]
    print("  [OK] /api/auth/me passed")

    # 4. 1-Click Demo Login (Teacher)
    res = client.post("/api/auth/demo-login", json={"role": "teacher"})
    assert res.status_code == 200
    tea_login = res.json()
    assert tea_login["user"]["role"] == "teacher"
    tea_token = tea_login["token"]
    print("  [OK] /api/auth/demo-login (teacher) passed")

    # 5. User Registration via API
    import uuid
    u_name = f"api_user_{uuid.uuid4().hex[:5]}"
    res = client.post("/api/auth/register", json={
        "username": u_name,
        "email": f"{u_name}@test.com",
        "password": "mypassword123",
        "full_name": "API Learner",
        "role": "student",
        "grade_or_board": "CBSE Class 12",
        "preferred_language": "Tamil",
    })
    assert res.status_code == 200
    reg_data = res.json()
    assert reg_data["user"]["username"] == u_name
    api_token = reg_data["token"]
    print(f"  [OK] /api/auth/register passed for user '{u_name}'")

    # 6. Standard Login via API
    res = client.post("/api/auth/login", json={
        "username_or_email": u_name,
        "password": "mypassword123",
    })
    assert res.status_code == 200
    log_data = res.json()
    assert log_data["user"]["username"] == u_name
    print("  [OK] /api/auth/login passed")

    # 7. Update Profile via API
    res = client.put(
        "/api/auth/profile",
        json={"preferred_language": "Telugu", "grade_or_board": "JEE Main"},
        headers={"Authorization": f"Bearer {api_token}"},
    )
    assert res.status_code == 200
    upd_data = res.json()
    assert upd_data["user"]["preferred_language"] == "Telugu"
    print("  [OK] /api/auth/profile update passed")

    # 8. Logout via API
    res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {api_token}"})
    assert res.status_code == 200
    # verify token is gone
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {api_token}"})
    assert res.status_code == 401
    print("  [OK] /api/auth/logout invalidation passed")

    print("\nALL FASTAPI AUTH ENDPOINTS PASSED SUCCESSFULLY! [OK]")


if __name__ == "__main__":
    test_auth_store()
    test_api_endpoints()

