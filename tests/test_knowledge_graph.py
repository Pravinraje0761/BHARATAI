from src.knowledge_graph import KnowledgeGraphStore


def test_correct_attempts_raise_mastery_and_wrong_ones_record_misconceptions(tmp_path):
    kg = KnowledgeGraphStore(tmp_path / "kg.sqlite3")
    first = kg.record_attempt("s1", "Electric Current", is_correct=True)
    second = kg.record_attempt("s1", "Electric Current", is_correct=True)
    assert second["mastery"] >= first["mastery"]
    wrong = kg.record_attempt("s1", "Electric Current", is_correct=False,
                              misconception="Thinks current is used up")
    assert "Thinks current is used up" in wrong["misconceptions"]
    graph = kg.get_student_graph("s1")
    assert any(n["concept"] == "Electric Current" for n in graph["nodes"])
    kg.close()
