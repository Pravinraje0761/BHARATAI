"""Verification of the Tri-Tier LLM Cascade with Fallback & Graceful Degradation.

Verifies:
1. Groq / NVIDIA NIM / Gemini live inference works or falls back cleanly.
2. When live APIs are unreachable or invalid, the system automatically falls back
   to the built-in pedagogical mock engine without crashing (0% failure rate).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from src.llm import generate_text, generate_json, _mock_text, _mock_json

def main():
    print("== [1] Testing Standard generate_text ==")
    t = generate_text("Explain Ohm's Law in 30 words", tag="explain")
    assert len(t) > 10, "Text generation failed"
    print(f"  [OK] generate_text returned: {t[:80]}...")

    print("\n== [2] Testing Standard generate_json ==")
    j = generate_json("Generate a quiz for Ohm's Law with 1 question", tag="quiz")
    assert j and isinstance(j, (dict, list)), "JSON generation failed"
    print(f"  [OK] generate_json returned valid structure: keys={list(j.keys()) if isinstance(j, dict) else len(j)}")

    print("\n== [3] Testing Graceful Degradation when APIs are Disabled ==")
    orig_groq = config.GROQ_API_KEY
    orig_nvidia = config.NVIDIA_API_KEY
    orig_gemini = config.GEMINI_API_KEY

    try:
        # Force cloud failure by invalidating keys
        config.GROQ_API_KEY = ""
        config.NVIDIA_API_KEY = ""
        config.GEMINI_API_KEY = ""

        mock_t = generate_text("Explain Resistance in Hindi", tag="explain")
        assert len(mock_t) > 10
        print(f"  [OK] Zero-crash fallback text: {mock_t[:80]}...")

        mock_j = generate_json("Grade this answer", tag="evaluate")
        assert isinstance(mock_j, dict) and "verdict" in mock_j
        print(f"  [OK] Zero-crash fallback JSON: verdict={mock_j.get('verdict')}")
    finally:
        config.GROQ_API_KEY = orig_groq
        config.NVIDIA_API_KEY = orig_nvidia
        config.GEMINI_API_KEY = orig_gemini

    print("\nALL LLM CASCADE & DEGRADATION TESTS PASSED!")

if __name__ == "__main__":
    main()
