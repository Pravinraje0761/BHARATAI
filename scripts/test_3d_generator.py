"""Test for Natural Language to 3D Generation (/api/3d/generate) and Presets (/api/3d/model)."""
import sys
from pathlib import Path

# Windows consoles default to cp1252 and choke on scientific unicode (H2O -> H₂O).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def main():
    # Authenticate client with demo student
    auth_res = client.post("/api/auth/demo-login", json={"role": "student"})
    assert auth_res.status_code == 200
    token = auth_res.json()["token"]
    client.headers["Authorization"] = f"Bearer {token}"

    test_cases = [
        ("human eye", "Human Eye", "human_eye"),
        ("Water molecule H2O with bond angles", "Water Molecule", "procedural_scene"),
        ("Solar system with sun and orbital rings", "Solar System", "solar_orbits"),
        ("human heart", "Human Heart", "procedural_scene"),
        ("plant cell", "Plant Cell", "procedural_scene"),
        ("glass prism dispersion", "Prism", "procedural_scene"),
    ]

    for q, expected_substring, expected_model_type in test_cases:
        res = client.post("/api/3d/generate", json={"query": q})
        assert res.status_code == 200, f"Failed for {q}: {res.text}"
        data = res.json()
        title = data.get("title", "")
        model_type = data.get("model_type", "")
        annotations = data.get("annotations", [])
        assert expected_substring.lower() in title.lower(), f"Expected '{expected_substring}' in title '{title}' for query '{q}'"
        assert len(annotations) > 0, f"Expected annotations for query '{q}'"
        print(f"  [OK] \"{q}\" -> Title: {title} | Type: {model_type} | Annotations: {len(annotations)}")

    # Test preset endpoint GET /api/3d/model?concept=eye
    res_eye = client.get("/api/3d/model?concept=eye")
    assert res_eye.status_code == 200
    eye_data = res_eye.json()
    assert "eye" in eye_data["title"].lower()
    print(f"  [OK] GET /api/3d/model?concept=eye -> Title: {eye_data['title']}")

    print("\nALL NATURAL LANGUAGE 3D GENERATOR TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
