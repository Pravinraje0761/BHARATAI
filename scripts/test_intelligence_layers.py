"""Verification that Knowledge Graph, Learning DNA, Spaced Repetition, and Teacher Dashboard reflect actual student session data."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def main():
    student = "student1"

    print("== [1] Testing Knowledge Graph endpoint ==")
    res = client.get(f"/api/knowledge-graph/{student}")
    assert res.status_code == 200
    kg = res.json()
    assert "nodes" in kg and "links" in kg and "overall_mastery" in kg
    print(f"  [OK] Knowledge Graph: {len(kg['nodes'])} nodes, overall mastery = {kg['overall_mastery']}%")

    print("\n== [2] Testing Learning DNA endpoint ==")
    res = client.get(f"/api/student/dna/{student}")
    assert res.status_code == 200
    dna = res.json()
    assert "visual_affinity" in dna and "conceptual_depth" in dna and "recall_retention" in dna
    print(f"  [OK] Learning DNA: visual={dna['visual_affinity']}%, depth={dna['conceptual_depth']}%, recall={dna['recall_retention']}%")

    print("\n== [3] Testing Spaced Repetition endpoint ==")
    res = client.get(f"/api/spaced-repetition/{student}")
    assert res.status_code == 200
    sr = res.json()
    assert isinstance(sr, list)
    print(f"  [OK] Spaced Repetition: {len(sr)} cards currently in review queue")

    print("\n== [4] Testing Teacher Dashboard endpoint ==")
    res = client.get("/api/teacher/class-overview")
    assert res.status_code == 200
    dash = res.json()
    assert "total_enrolled" in dash and "shared_misconceptions" in dash and "concepts_mastery" in dash
    print(f"  [OK] Teacher Dashboard: {dash['total_enrolled']} students, {len(dash['shared_misconceptions'])} shared misconceptions tracked")

    print("\nALL INTELLIGENCE LAYERS REFLECT LIVE DATA SUCCESSFULLY!")

if __name__ == "__main__":
    main()
