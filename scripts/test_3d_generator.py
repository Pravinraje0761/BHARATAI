"""Test for Natural Language to 3D Generation (/api/3d/generate)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def main():
    queries = [
        "Water molecule H2O with bond angles",
        "Solar system with sun and orbital rings",
        "Magnetic field lines around a bar magnet"
    ]
    for q in queries:
        res = client.post("/api/3d/generate", json={"query": q})
        assert res.status_code == 200, f"Failed for {q}: {res.text}"
        data = res.json()
        assert "objects" in data or "concept" in data or "description" in data
        obj_count = len(data.get("objects", []))
        title = data.get("title") or data.get("concept") or q
        print(f"  [OK] 3D spec for \"{q}\": {obj_count} objects -> {title}")

    print("\nALL NATURAL LANGUAGE 3D GENERATOR TESTS PASSED!")

if __name__ == "__main__":
    main()
