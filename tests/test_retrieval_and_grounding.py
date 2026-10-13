from src.hallucination_shield import verify_grounding
from src.hybrid_rag import BM25Index
from src.ingestion import Chunk


def _chunks():
    texts = [
        "Ohm's law states that current through a conductor is proportional to the voltage.",
        "Photosynthesis converts light energy into chemical energy in plants.",
        "Resistance of a wire increases with its length and decreases with its area.",
    ]
    return [Chunk(text=t, source_page=i + 1, source_label=f"p.{i + 1}", doc_name="doc", index=i)
            for i, t in enumerate(texts)]


def test_bm25_ranks_the_matching_passage_first():
    scores = BM25Index(_chunks()).score("voltage and current ohm")
    assert max(range(3), key=scores.__getitem__) == 0


def test_bm25_gives_zero_for_unseen_terms():
    assert BM25Index(_chunks()).score("quantum chromodynamics") == [0.0, 0.0, 0.0]


def test_grounding_without_sources_is_flagged_as_general_knowledge():
    report = verify_grounding("Current flows from high to low potential.", [])
    assert report.is_grounded is False
    assert report.status_label == "GENERAL_KNOWLEDGE"


def test_grounding_report_scores_are_bounded():
    report = verify_grounding("Resistance increases with the length of the wire.", _chunks())
    assert 0.0 <= report.confidence_score <= 1.0
