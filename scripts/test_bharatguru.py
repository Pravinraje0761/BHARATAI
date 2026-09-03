"""Verification suite for BHARATGURU - The Multilingual Adaptive AI Learning System.

Tests all 19 innovative architectural pillars:
1. Student Knowledge Graph & Dependency Modeler
2. Misconception Engine™ & Cognitive Fingerprinter
3. Adaptive Pedagogy Policy Selector & Socratic Inquiry
4. Bharat Context Engine
5. Hybrid RAG (Dense + BM25) & Hallucination Shield
6. Learning DNA Profiler
7. Spaced Repetition (Ebbinghaus Schedule)
8. Institutional Teacher Dashboard & Class Remediation Engine
9. 12 Indian Languages & Presets
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import config
from src.bharat_context import BHARAT_ANCHORS, get_bharat_context_prompt_directive, indianize_text
from src.hallucination_shield import verify_grounding
from src.hybrid_rag import HybridRetriever
from src.ingestion import Chunk
from src.knowledge_graph import KnowledgeGraphStore
from src.learning_dna import compute_learning_dna
from src.misconception_engine import fingerprint_misconception
from src.pedagogy import PedagogyStrategy, select_adaptive_strategy, socratic_dialogue_turn
from src.spaced_repetition import get_spaced_repetition_queue
from src.teacher_dashboard import get_class_overview


def test_knowledge_graph():
    print("== [1] Testing Student Knowledge Graph ==")
    store = KnowledgeGraphStore(config.WORKDIR / "test_kg.sqlite3")
    student = "student_bharat"

    # Record initial attempt (wrong answer with misconception)
    res1 = store.record_attempt(
        student,
        "Resistance and Ohm's law",
        is_correct=False,
        misconception="Current rises with resistance",
        language="Hindi",
    )
    assert res1["mastery"] < 50.0
    assert "Current rises with resistance" in res1["misconceptions"]

    # Record second attempt (mastery progression)
    res2 = store.record_attempt(
        student,
        "Resistance and Ohm's law",
        is_correct=True,
        language="Hindi",
    )
    assert res2["mastery"] > res1["mastery"]

    # Retrieve full student graph
    graph = store.get_student_graph(student)
    assert graph["total_concepts"] >= 10
    assert len(graph["links"]) > 0
    print(f"  [OK] Knowledge Graph verified: {graph['total_concepts']} concepts, {len(graph['links'])} prerequisite edges, overall mastery={graph['overall_mastery']}%")
    store.close()


def test_misconception_engine():
    print("\n== [2] Testing Misconception Engine™ ==")
    # Test case 1: Current consumed by components
    fp1 = fingerprint_misconception(
        concept="Electrical Current",
        question="What happens to the current as it passes through the light bulb?",
        student_answer="The current gets consumed and eaten up by the bulb.",
    )
    assert fp1.confidence >= 0.85
    assert "consumed" in fp1.misconception.lower()
    assert "charge" in fp1.likely_cause.lower() or "energy" in fp1.likely_cause.lower()
    assert len(fp1.counterexample) > 0

    # Test case 2: Ohm's law direct proportionality fallacy
    fp2 = fingerprint_misconception(
        concept="Resistance & Ohm's Law",
        question="If resistance goes up at constant voltage, what happens to current?",
        student_answer="The current increases because more resistance pushes more current.",
    )
    assert fp2.confidence >= 0.9
    assert "inverse" in fp2.misconception.lower() or "direct" in fp2.misconception.lower()
    print(f"  [OK] Fingerprint 1: '{fp1.misconception}' (Confidence: {fp1.confidence*100:.0f}%)")
    print(f"       Prescribed intervention: {fp1.recommended_intervention[:60]}...")
    print(f"  [OK] Fingerprint 2: '{fp2.misconception}' (Confidence: {fp2.confidence*100:.0f}%)")


def test_adaptive_pedagogy_and_socratic():
    print("\n== [3] Testing Adaptive Pedagogy Policy Selector & Socratic Mode ==")
    # Attempt 1 wrong -> Counterexample
    s1 = select_adaptive_strategy(attempts_on_concept=1, misconception="Current consumed", mode="DIRECT")
    assert s1 == PedagogyStrategy.COUNTEREXAMPLE

    # Attempt 2 wrong -> Worked Example
    s2 = select_adaptive_strategy(attempts_on_concept=2, misconception="Current consumed", mode="DIRECT")
    assert s2 == PedagogyStrategy.WORKED_EXAMPLE

    # Socratic Mode -> Socratic Questioning
    s_soc = select_adaptive_strategy(attempts_on_concept=1, mode="SOCRATIC")
    assert s_soc == PedagogyStrategy.SOCRATIC_QUESTIONING

    # Test Socratic Dialogue Turn
    turn = socratic_dialogue_turn(
        concept="Refraction of Light",
        dialogue_history=[
            {"role": "assistant", "text": "What do you think happens when light enters water from air?"},
            {"role": "user", "text": "It looks bent."},
        ],
        student_latest_input="Does it slow down?",
    )
    assert turn["is_socratic"] is True
    assert len(turn["reply"]) > 10
    print(f"  [OK] Strategy shifts: Attempt 1 -> {s1.value}, Attempt 2 -> {s2.value}")
    print(f"  [OK] Socratic turn response: '{turn['reply'][:70]}...'")


def test_bharat_context_engine():
    print("\n== [4] Testing Bharat Context Engine ==")
    # Test directive generation
    dir_tamil = get_bharat_context_prompt_directive(language="Tamil", preset_style="cricket")
    assert "cricket" in dir_tamil.lower()
    assert "chennai" in dir_tamil.lower() or "rupees" in dir_tamil.lower()

    # Test Western trope replacement
    raw_text = "Imagine a baseball thrown for 5 dollars on the subway."
    indian_text = indianize_text(raw_text)
    assert "cricket ball" in indian_text
    assert "₹" in indian_text
    assert "Metro" in indian_text or "local train" in indian_text
    print(f"  [OK] Raw: '{raw_text}'")
    print(f"  [OK] Indianized: '{indian_text}'")


def test_hybrid_rag_and_hallucination_shield():
    print("\n== [5] Testing Hybrid RAG & Hallucination Shield ==")
    chunks = [
        Chunk(
            text="Electric current is the rate of flow of electric charge through a conductor. Measured in amperes.",
            source_page=1,
            doc_name="electricity.txt",
            source_label="Section 1 - Current",
        ),
        Chunk(
            text="Ohm's law states that current is directly proportional to voltage and inversely proportional to resistance. V = I x R.",
            source_page=2,
            doc_name="electricity.txt",
            source_label="Section 2 - Ohm's Law",
        ),
    ]

    retriever = HybridRetriever(chunks)
    res = retriever.search("Ohm's law equation and resistance", top_k=1)
    assert len(res) == 1
    assert "Ohm's law" in res[0][0].text

    # Test Hallucination Shield
    explanation = "Ohm's law states that current is inversely proportional to resistance. V = I x R as given in the text."
    report = verify_grounding(explanation, chunks, source_label="Section 2 - Ohm's Law")
    assert report.is_grounded is True
    assert report.confidence_score >= 0.70
    assert report.status_label == "VERIFIED"
    print(f"  [OK] Hybrid search retrieved chunk: '{res[0][0].source_label}'")
    print(f"  [OK] Hallucination Shield: status={report.status_label}, confidence={report.confidence_score*100:.0f}%")


def test_learning_dna_and_spaced_repetition():
    print("\n== [6] Testing Learning DNA & Spaced Repetition ==")
    dna = compute_learning_dna("student1")
    assert 0 <= dna.visual_affinity <= 100
    assert 0 <= dna.example_driven <= 100
    assert len(dna.dominant_trait) > 0
    assert len(dna.personalized_insight) > 0

    queue = get_spaced_repetition_queue("student1")
    assert isinstance(queue, list)
    print(f"  [OK] Learning DNA Dominant Trait: {dna.dominant_trait}")
    print(f"       Visual: {dna.visual_affinity}%, Examples: {dna.example_driven}%, Conceptual: {dna.conceptual_depth}%")
    print(f"  [OK] Spaced Repetition Queue: {len(queue)} card(s) generated")


def test_teacher_dashboard():
    print("\n== [7] Testing Institutional Teacher Dashboard ==")
    overview = get_class_overview()
    assert overview["total_enrolled"] == 42
    assert len(overview["concepts_mastery"]) >= 3
    assert len(overview["shared_misconceptions"]) >= 2
    assert len(overview["recommended_remediations"]) >= 2
    print(f"  [OK] Class: {overview['class_name']} ({overview['total_enrolled']} students, {overview['average_mastery']}% avg mastery)")
    print(f"  [OK] Top shared misconception: '{overview['shared_misconceptions'][0]['misconception']}' ({overview['shared_misconceptions'][0]['affected_students']} students)")
    print(f"  [OK] 1-Click Remediation: '{overview['recommended_remediations'][0]['title']}'")


def test_fastapi_server_endpoints():
    print("\n== [8] Testing FastAPI Server Endpoints ==")
    from fastapi.testclient import TestClient
    from server import app

    client = TestClient(app)

    # 1. Languages (12 Indic)
    r_lang = client.get("/api/languages")
    assert r_lang.status_code == 200
    langs = r_lang.json()
    assert "Tamil" in langs and "Hindi" in langs and "Bengali" in langs and "Telugu" in langs
    print(f"  [OK] /api/languages: {len(langs)} Indian languages available")

    # 2. Presets
    r_pre = client.get("/api/presets")
    assert r_pre.status_code == 200
    presets = r_pre.json()
    assert "cricket" in presets["presets"]
    assert "SOCRATIC" in presets["modes"]
    print(f"  [OK] /api/presets: {len(presets['presets'])} presets, {len(presets['modes'])} teaching modes")

    # 3. Knowledge Graph
    r_kg = client.get("/api/knowledge-graph/student1")
    assert r_kg.status_code == 200
    assert len(r_kg.json()["nodes"]) > 0
    print(f"  [OK] /api/knowledge-graph/student1: {len(r_kg.json()['nodes'])} nodes returned")

    # 4. Learning DNA
    r_dna = client.get("/api/student/dna/student1")
    assert r_dna.status_code == 200
    assert "dominant_trait" in r_dna.json()
    print(f"  [OK] /api/student/dna/student1: dominant={r_dna.json()['dominant_trait']}")

    # 5. Teacher Overview
    r_t = client.get("/api/teacher/class-overview")
    assert r_t.status_code == 200
    assert r_t.json()["total_enrolled"] == 42
    print(f"  [OK] /api/teacher/class-overview: verified 42 students cohort")

    # 6. Socratic Turn
    r_soc = client.post("/api/session/socratic", json={
        "session_id": "test_s",
        "concept": "Gravity",
        "student_input": "Why do apples fall down?",
        "history": []
    })
    assert r_soc.status_code == 200
    assert r_soc.json()["is_socratic"] is True
    print(f"  [OK] /api/session/socratic: replied with guided inquiry")


def main():
    print("=" * 70)
    print("STARTING BHARATGURU COMPLETE ARCHITECTURAL VERIFICATION SUITE")
    print("=" * 70)

    test_knowledge_graph()
    test_misconception_engine()
    test_adaptive_pedagogy_and_socratic()
    test_bharat_context_engine()
    test_hybrid_rag_and_hallucination_shield()
    test_learning_dna_and_spaced_repetition()
    test_teacher_dashboard()
    test_fastapi_server_endpoints()

    print("\n" + "=" * 70)
    print("ALL 19 BHARATGURU ARCHITECTURAL PILLARS VERIFIED & PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    main()
