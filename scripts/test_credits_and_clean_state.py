import requests
import json

BASE_URL = "http://localhost:8000"

def test_credits_and_clean():
    session = requests.Session()
    # Authenticate as student first so gated endpoints and index.html are accessible
    auth_res = session.post(f"{BASE_URL}/api/auth/demo-login", json={"role": "student"})
    assert auth_res.status_code == 200, f"Failed demo login: {auth_res.text}"

    print(">>> 1. Verifying HTML Credit Badge and Tier Selectors...")
    r = session.get(f"{BASE_URL}/index.html")
    assert r.status_code == 200, f"Failed GET /index.html: {r.status_code}"
    html = r.text
    assert "user-credits-badge" in html
    assert "tier-selector-container" in html
    assert "btn-upgrade-realistic-studio" in html
    assert 'value="express"' in html
    assert 'value="realistic"' in html
    print("  [PASS] HTML markup contains Credit Badge, Tier Selector, and Upgrade Button.")

    print("\n>>> 2. Testing Plan Generation with Express Tier (1 Credit)...")
    r1 = session.post(f"{BASE_URL}/api/plan", json={
        "topic": "Newtonian Dynamics",
        "instruction": "Explain Newton laws simply",
        "upload_paths": [],
        "language": "English",
        "mode": "DIRECT",
        "student": "test_credits_user",
        "production_tier": "express"
    })
    assert r1.status_code == 200, f"Plan failed: {r1.text}"
    d1 = r1.json()
    assert d1.get("production_tier") == "express"
    assert d1.get("credits_cost") == 1
    session_exp = d1["session_id"]
    print(f"  [PASS] Express plan generated. Tier: {d1['production_tier']}, Cost: {d1['credits_cost']} credit.")

    print("\n>>> 3. Testing Plan Generation with Realistic Studio Tier (5 Credits)...")
    r2 = session.post(f"{BASE_URL}/api/plan", json={
        "topic": "Cellular Respiration",
        "instruction": "Explain Krebs Cycle and ATP",
        "upload_paths": [],
        "language": "English",
        "mode": "DIRECT",
        "student": "test_credits_user",
        "production_tier": "realistic"
    })
    assert r2.status_code == 200, f"Plan failed: {r2.text}"
    d2 = r2.json()
    assert d2.get("production_tier") == "realistic"
    assert d2.get("credits_cost") == 5
    session_real = d2["session_id"]
    print(f"  [PASS] Realistic Studio plan generated. Tier: {d2['production_tier']}, Cost: {d2['credits_cost']} credits.")

    print("\n>>> 4. Testing Explain Endpoint for Tier Metadata...")
    exp1 = session.post(f"{BASE_URL}/api/session/explain", json={
        "session_id": session_exp,
        "segment_index": 0,
        "render_video": False,
        "production_tier": "express"
    }).json()
    assert exp1.get("production_tier") == "express"
    assert exp1.get("is_realistic_studio") is False
    print("  [PASS] Express explanation: is_realistic_studio is False.")

    exp2 = session.post(f"{BASE_URL}/api/session/explain", json={
        "session_id": session_real,
        "segment_index": 0,
        "render_video": False,
        "production_tier": "realistic"
    }).json()
    assert exp2.get("production_tier") == "realistic"
    assert exp2.get("is_realistic_studio") is True
    print("  [PASS] Realistic explanation: is_realistic_studio is True.")

    print("\n>>> 5. Testing Demo Account Isolation (Aarav vs Priya)...")
    demo_s = requests.post(f"{BASE_URL}/api/auth/demo-login", json={"role": "student"}).json()
    assert demo_s["user"]["username"] == "aarav"
    assert demo_s["user"]["role"] == "student"

    demo_t = requests.post(f"{BASE_URL}/api/auth/demo-login", json={"role": "teacher"}).json()
    assert demo_t["user"]["username"] == "priya"
    assert demo_t["user"]["role"] == "teacher"
    print("  [PASS] Demo accounts verified (student: aarav, teacher: priya).")

    print("\n============================================================")
    print("ALL TESTS PASSED! Credits & Clean Slate validated.")
    print("============================================================")

if __name__ == "__main__":
    test_credits_and_clean()
