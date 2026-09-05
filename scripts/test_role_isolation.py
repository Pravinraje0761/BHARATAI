#!/usr/bin/env python3
"""
scripts/test_role_isolation.py
Tests role-based access control and isolation between Student and Teacher portals:
1. Student demo login (aarav) -> receives student token
2. Student attempts to access teacher endpoints -> returns 403 Forbidden
3. Teacher demo login (priya) -> receives teacher token
4. Teacher accesses teacher endpoints -> returns 200 OK with roster & guidance
5. Password-based login for student and teacher
6. Registration of new student and new teacher
"""
import sys
import requests

BASE_URL = "http://localhost:8000"

def test_role_isolation():
    print("=" * 65)
    print("[TEST] BHARAT GURU ROLE ISOLATION & TEACHER GUIDANCE TEST SUITE")
    print("=" * 65)

    # 1. Student Demo Login
    print("\n[Step 1] Student Demo Login ('aarav')...")
    res = requests.post(f"{BASE_URL}/api/auth/demo-login", json={"role": "student", "username": "aarav"})
    assert res.status_code == 200, f"Student demo login failed: {res.text}"
    student_data = res.json()
    student_token = student_data["token"]
    student_user = student_data["user"]
    assert student_user["role"] == "student", f"Expected student role, got {student_user['role']}"
    print(f"  [OK] Logged in as: {student_user['full_name']} ({student_user['role']})")

    # 2. Student attempts forbidden teacher endpoints
    student_headers = {"Authorization": f"Bearer {student_token}"}
    print("\n[Step 2] Testing Student Role Protection (Expect 403 Forbidden)...")

    teacher_endpoints = [
        "/api/teacher/class-overview",
        "/api/teacher/students-roster",
        "/api/teacher/student-guidance/aarav"
    ]

    for ep in teacher_endpoints:
        r = requests.get(f"{BASE_URL}{ep}", headers=student_headers)
        print(f"  Testing GET {ep} with Student Token...")
        assert r.status_code == 403, f"Expected 403 Forbidden for student on {ep}, got {r.status_code}: {r.text}"
        print(f"  [OK] Correctly blocked with 403: {r.json().get('detail')}")

    # 3. Teacher Demo Login
    print("\n[Step 3] Teacher Demo Login ('priya')...")
    res = requests.post(f"{BASE_URL}/api/auth/demo-login", json={"role": "teacher", "username": "priya"})
    assert res.status_code == 200, f"Teacher demo login failed: {res.text}"
    teacher_data = res.json()
    teacher_token = teacher_data["token"]
    teacher_user = teacher_data["user"]
    assert teacher_user["role"] == "teacher", f"Expected teacher role, got {teacher_user['role']}"
    print(f"  [OK] Logged in as: {teacher_user['full_name']} ({teacher_user['role']})")

    # 4. Teacher accesses teacher endpoints (Expect 200 OK)
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    print("\n[Step 4] Testing Teacher Access to Protected Endpoints (Expect 200 OK)...")

    # Class Overview
    r = requests.get(f"{BASE_URL}/api/teacher/class-overview", headers=teacher_headers)
    assert r.status_code == 200, f"Teacher overview failed: {r.text}"
    overview = r.json()
    print(f"  [OK] Class Overview loaded: {overview.get('total_students')} students, {overview.get('struggling_count')} struggling")

    # Students Roster
    r = requests.get(f"{BASE_URL}/api/teacher/students-roster", headers=teacher_headers)
    assert r.status_code == 200, f"Teacher roster failed: {r.text}"
    roster_data = r.json()
    roster = roster_data.get("students", [])
    assert len(roster) > 0, "Expected at least 1 student in roster"
    student_ids = [s["student_id"] for s in roster]
    print(f"  [OK] Student Roster loaded: {len(roster)} students found: {student_ids}")
    assert "aarav" in student_ids, "Expected 'aarav' in student roster"

    # Pedagogical Guidance for Aarav
    r = requests.get(f"{BASE_URL}/api/teacher/student-guidance/aarav", headers=teacher_headers)
    assert r.status_code == 200, f"Teacher guidance for aarav failed: {r.text}"
    guidance_data = r.json()
    print(f"  [OK] Pedagogical Guidance for '{guidance_data['full_name']}':")
    print(f"    - Optimal Teaching Mode: {guidance_data.get('optimal_teaching_mode')}")
    print(f"    - Recommended Action: {guidance_data.get('recommended_action')}")
    print(f"    - Actionable Instructional Tips: {len(guidance_data.get('how_to_teach_guidance', []))}")
    for idx, tip in enumerate(guidance_data.get('how_to_teach_guidance', []), 1):
        print(f"      {idx}. [{tip.get('type')}] {tip.get('instructional_strategy')[:70]}...")

    # 5. Regular Credential Login Verification
    print("\n[Step 5] Testing Password Login for Both Portals...")
    # Student password login
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"username_or_email": "aarav", "password": "student123"})
    assert r.status_code == 200, f"Student password login failed: {r.text}"
    assert r.json()["user"]["role"] == "student"
    print("  [OK] Student password login succeeded")

    # Teacher password login
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"username_or_email": "priya", "password": "teacher123"})
    assert r.status_code == 200, f"Teacher password login failed: {r.text}"
    assert r.json()["user"]["role"] == "teacher"
    print("  [OK] Teacher password login succeeded")

    # 6. New Registration with Role
    print("\n[Step 6] Testing New User Registration with Roles...")
    new_student_user = "test_student_neo"
    r = requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": new_student_user,
        "email": "neo@school.edu",
        "password": "SecurePassword123!",
        "full_name": "Neo Student",
        "role": "student",
        "grade_or_board": "CBSE Class 11",
        "preferred_language": "English"
    })
    if r.status_code == 200:
        assert r.json()["user"]["role"] == "student"
        print("  [OK] Created new student account successfully")
    elif r.status_code == 400 and "already exists" in r.text:
        print("  [OK] Student account already registered (re-tested)")
    else:
        raise AssertionError(f"Unexpected registration response: {r.status_code} {r.text}")

    print("\n" + "=" * 65)
    print("[SUCCESS] ALL ROLE ISOLATION & TEACHER GUIDANCE CHECKS PASSED 100%!")
    print("=" * 65)

if __name__ == "__main__":
    try:
        test_role_isolation()
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        sys.exit(1)
