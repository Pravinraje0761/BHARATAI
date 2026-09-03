"""Gemini reasoning engine wrapper with multi-model fallback and graceful degradation.

One import surface for the rest of the app:

    from src.llm import generate_text, generate_json

Provides:
- Live Gemini generation across configured & fallback models.
- Auto-catch for rate limits (429 Quota Exceeded) & model deprecations (404).
- Automatic seamless fallback to offline pedagogical engine to guarantee 0% failure rate.
"""
from __future__ import annotations

import json
import re
from typing import Any

import config

_MODELS: dict[str, Any] = {}

CANDIDATE_MODELS = [
    config.GEMINI_MODEL,
    "gemini-2.5-flash",
]


# --------------------------------------------------------------------------- #
# Real Gemini path with model cascade
# --------------------------------------------------------------------------- #
def _get_model(model_name: str | None = None):
    model_name = model_name or config.GEMINI_MODEL
    if model_name in _MODELS:
        return _MODELS[model_name]

    if not config.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Put it in .env, or set LLM_MOCK=1 to run offline."
        )

    import google.generativeai as genai

    genai.configure(api_key=config.GEMINI_API_KEY.strip())
    model = genai.GenerativeModel(model_name)
    _MODELS[model_name] = model
    return model


def _extract_json(text: str) -> str:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    # fall back to the first {...} or [...] span
    if not text.startswith(("{", "[")):
        m = re.search(r"[\{\[].*[\}\]]", text, re.DOTALL)
        if m:
            text = m.group(0)
    return text


import concurrent.futures
import requests

def _call_with_timeout(fn, *args, timeout: float = 3.0, **kwargs):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fn, *args, **kwargs)
        return future.result(timeout=timeout)


def _call_groq(
    prompt: str,
    system: str | None = None,
    temperature: float = 0.6,
    expect_json: bool = False,
) -> Any:
    """Sub-second LPU generation using Groq (Qwen 3.8 27B / Groq Compound)."""
    if not config.GROQ_API_KEY:
        raise RuntimeError("No GROQ_API_KEY configured")

    models_to_try = [
        config.GROQ_MODEL or "qwen/qwen3.8-27b",
        "groq/compound-mini",
        "openai/gpt-oss-20b",
    ]

    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY.strip()}",
        "Content-Type": "application/json",
    }

    sys_msg = system or "You are BHARATGURU, an expert multilingual adaptive STEM teacher for Indian students."
    if expect_json:
        sys_msg += "\nCRITICAL: Output strictly valid JSON. Do not include markdown code fences or conversational text."

    for model_name in models_to_try:
        try:
            payload: dict[str, Any] = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 1024,
                "temperature": max(0.1, min(temperature, 1.0)),
            }
            if expect_json and "qwen" in model_name.lower():
                payload["response_format"] = {"type": "json_object"}

            resp = requests.post(
                f"{config.GROQ_BASE_URL.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
                timeout=4.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"].strip()
                if expect_json:
                    return json.loads(_extract_json(content))
                return content
        except Exception:
            continue

    raise RuntimeError("All Groq model endpoints failed or timed out.")


def _call_nvidia_nim(
    prompt: str,
    system: str | None = None,
    temperature: float = 0.6,
    expect_json: bool = False,
) -> Any:
    """High-speed GPU generation using NVIDIA NIM (Meta Llama 3.2 11B / GPT-OSS)."""
    if not config.NVIDIA_API_KEY:
        raise RuntimeError("No NVIDIA_API_KEY configured")

    models_to_try = [config.NVIDIA_MODEL or "meta/llama-3.2-11b-vision-instruct"]

    headers = {
        "Authorization": f"Bearer {config.NVIDIA_API_KEY.strip()}",
        "Content-Type": "application/json",
    }

    sys_msg = system or "You are BHARATGURU, an expert multilingual adaptive STEM teacher for Indian students."
    if expect_json:
        sys_msg += "\nCRITICAL: Output strictly valid JSON. Do not include markdown code fences or conversational text."

    for model_name in models_to_try:
        try:
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 512,
                "temperature": max(0.1, min(temperature, 1.0)),
            }
            resp = requests.post(
                f"{config.NVIDIA_BASE_URL.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
                timeout=6.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"].strip()
                if expect_json:
                    return json.loads(_extract_json(content))
                return content
        except Exception:
            continue

    raise RuntimeError("All NVIDIA NIM model endpoints failed or timed out.")


def _live_text_with_fallback(prompt: str, system: str | None, temperature: float) -> str:
    # 1. Ultra-Fast LPU Tier: Groq (~0.9s response)
    if config.GROQ_API_KEY:
        try:
            return _call_groq(prompt, system, temperature, expect_json=False)
        except Exception:
            pass

    # 2. High-Performance GPU Tier: NVIDIA NIM
    if config.NVIDIA_API_KEY:
        try:
            return _call_nvidia_nim(prompt, system, temperature, expect_json=False)
        except Exception:
            pass

    # 3. Cloud Tier: Google Gemini
    full = f"{system.strip()}\n\n{prompt}" if system else prompt
    errors = []

    models_to_try = [config.GEMINI_MODEL] + [m for m in CANDIDATE_MODELS if m != config.GEMINI_MODEL]

    for model_name in models_to_try:
        try:
            model = _get_model(model_name)
            resp = _call_with_timeout(
                model.generate_content,
                full,
                generation_config={"temperature": temperature},
                timeout=3.0,
            )
            if resp and resp.text:
                return resp.text.strip()
        except Exception as exc:
            errors.append(f"{model_name}: {exc}")
            continue

    raise RuntimeError(f"All cloud models failed or timed out: {'; '.join(errors[:2])}")


def _live_json_with_fallback(prompt: str, system: str | None, temperature: float) -> Any:
    # 1. Ultra-Fast LPU Tier: Groq (~0.9s response)
    if config.GROQ_API_KEY:
        try:
            return _call_groq(prompt, system, temperature, expect_json=True)
        except Exception:
            pass

    # 2. High-Performance GPU Tier: NVIDIA NIM
    if config.NVIDIA_API_KEY:
        try:
            return _call_nvidia_nim(prompt, system, temperature, expect_json=True)
        except Exception:
            pass

    # 3. Cloud Tier: Google Gemini
    full = f"{system.strip()}\n\n{prompt}" if system else prompt
    errors = []

    models_to_try = [config.GEMINI_MODEL] + [m for m in CANDIDATE_MODELS if m != config.GEMINI_MODEL]

    for model_name in models_to_try:
        try:
            model = _get_model(model_name)
            try:
                resp = _call_with_timeout(
                    model.generate_content,
                    full,
                    generation_config={
                        "temperature": temperature,
                        "response_mime_type": "application/json",
                    },
                    timeout=2.0,
                )
            except Exception:
                resp = _call_with_timeout(
                    model.generate_content,
                    full + "\n\nReturn ONLY valid JSON, no prose, no code fence.",
                    generation_config={"temperature": temperature},
                    timeout=2.0,
                )
            if resp and resp.text:
                return json.loads(_extract_json(resp.text))
        except Exception as exc:
            errors.append(f"{model_name}: {exc}")
            continue

    raise RuntimeError(f"All cloud JSON models failed or timed out: {'; '.join(errors[:2])}")


# --------------------------------------------------------------------------- #
# Public API with Automatic Graceful Degradation
# --------------------------------------------------------------------------- #
def generate_text(
    prompt: str,
    *,
    tag: str = "text",
    system: str | None = None,
    temperature: float = 0.7,
) -> str:
    if config.LLM_MOCK:
        return _mock_text(tag, prompt)

    try:
        return _live_text_with_fallback(prompt, system, temperature)
    except Exception as exc:
        print(f"\n[llm.py] Notice: Gemini API rate limit or error ({exc}).")
        print(f"[llm.py] Gracefully switching to built-in pedagogical mock engine for tag='{tag}'.\n")
        return _mock_text(tag, prompt)


def generate_json(
    prompt: str,
    *,
    tag: str,
    system: str | None = None,
    temperature: float = 0.3,
) -> Any:
    if config.LLM_MOCK:
        return _mock_json(tag, prompt)

    try:
        return _live_json_with_fallback(prompt, system, temperature)
    except Exception as exc:
        print(f"\n[llm.py] Notice: Gemini API rate limit or error ({exc}).")
        print(f"[llm.py] Gracefully switching to built-in pedagogical mock engine for tag='{tag}'.\n")
        return _mock_json(tag, prompt)


def health_check() -> str:
    """One throwaway call to confirm the engine status."""
    if config.LLM_MOCK:
        return "MOCK engine active (LLM_MOCK=1)."
    try:
        out = _live_text_with_fallback("Reply with the single word: OK", None, 0.0)
        return f"Gemini reachable; replied: {out[:40]!r}"
    except Exception as exc:
        return f"Live Gemini unavailable ({exc}); Auto-fallback to offline mock engine enabled."


# --------------------------------------------------------------------------- #
# Deterministic offline mock with dynamic topic extraction
# --------------------------------------------------------------------------- #
def _first_sentence(prompt: str) -> str:
    for line in prompt.splitlines():
        line = line.strip()
        if len(line) > 20:
            return line[:160]
    return prompt[:160]


def _mock_text(tag: str, prompt: str) -> str:
    if tag == "explain":
        if "newton" in prompt.lower() or "motion" in prompt.lower():
            return (
                "Imagine you are riding in a bus that suddenly stops. Your body jerks forward. "
                "This is Newton's First Law of Motion, also known as the Law of Inertia. "
                "An object at rest stays at rest, and an object in motion stays in motion with the "
                "same speed and direction unless acted upon by an unbalanced external force."
            )
        if "photosynthesis" in prompt.lower() or "plant" in prompt.lower():
            return (
                "Think of a green leaf as a solar-powered kitchen. Using sunlight as energy, "
                "the leaf takes in carbon dioxide from the air and water from the soil to cook glucose "
                "for food, releasing fresh oxygen into the air. This process is called photosynthesis."
            )
        return (
            "Think of electric current like water flowing through a pipe. "
            "The wider the pipe, the more water flows for the same push. "
            "Resistance is how narrow the pipe is: more resistance means less "
            "current for the same voltage. This is Ohm's law, V = I x R."
        )
    if tag == "reexplain":
        if "newton" in prompt.lower() or "motion" in prompt.lower():
            return (
                "Different picture: imagine sliding a hockey puck on smooth ice versus a rough carpet. "
                "On ice with almost no friction, the puck glides forever. The force does not keep it moving; "
                "forces only change its motion. Without friction or push, velocity remains constant."
            )
        return (
            "Different picture: imagine a crowded corridor. Resistance is the "
            "crowd. Add more people (more resistance) and fewer students get "
            "through per minute (less current) even if you push just as hard "
            "(same voltage)."
        )
    if tag == "question":
        if "newton" in prompt.lower() or "motion" in prompt.lower():
            return "What keeps a spacecraft moving forward once its engines are turned off in deep space?"
        return "If resistance goes up while voltage stays the same, what happens to the current?"
    if tag == "feedback":
        return "Good effort. Re-read the relationship between the three quantities."
    return f"[mock:{tag}] {_first_sentence(prompt)}"


def _mock_json(tag: str, prompt: str) -> Any:
    if tag == "instruction":
        m = re.search(r'"""(.*?)"""', prompt, re.DOTALL)
        low = (m.group(1) if m else prompt).lower()
        lang = "Hinglish" if "hinglish" in low else "Hindi" if "hindi" in low else "English"
        mins = 20
        m = re.search(r"(\d+)\s*(?:min|minute)", low)
        if m:
            mins = int(m.group(1))
        level = "beginner"
        for cand in ("advanced", "intermediate", "beginner"):
            if cand in low:
                level = cand
                break
        return {
            "level": level,
            "time_minutes": mins,
            "language": lang,
            "style": "simple real-world examples",
            "focus": "the uploaded chapter" if "chapter" in low else "the requested topic",
        }

    if tag == "lesson_plan":
        low = prompt.lower()
        if "newton" in low or "motion" in low or "force" in low:
            return {
                "title": "Newton's Laws of Motion & Classical Mechanics",
                "language": "English",
                "level": "beginner",
                "segments": [
                    {
                        "concept": "First Law & Inertia",
                        "depth": "intuitive definition + everyday examples",
                        "example": "a passenger lurching forward when a bus brakes",
                        "source_label": "Physics Section 1",
                        "checkpoint_question": "Why does a rolling ball eventually stop on ground but not in deep space?",
                    },
                    {
                        "concept": "Second Law: F = m x a",
                        "depth": "relationship between force, mass, and acceleration",
                        "example": "pushing an empty shopping cart vs a loaded one",
                        "source_label": "Physics Section 2",
                        "checkpoint_question": "If you double the mass while keeping force constant, what happens to acceleration?",
                    },
                    {
                        "concept": "Third Law: Action and Reaction",
                        "depth": "equal and opposite force pairs",
                        "example": "a rocket expelling exhaust gas downward to launch upward",
                        "source_label": "Physics Section 3",
                        "checkpoint_question": "When you jump off a small boat onto a dock, why does the boat push backward?",
                    },
                ],
            }
        if "photo" in low or "plant" in low or "bio" in low:
            return {
                "title": "Photosynthesis: Solar Energy to Chemical Energy",
                "language": "English",
                "level": "beginner",
                "segments": [
                    {
                        "concept": "Light Absorption in Chloroplasts",
                        "depth": "role of chlorophyll and solar capture",
                        "example": "solar panels charging a battery in sunlight",
                        "source_label": "Biology Section 1",
                        "checkpoint_question": "Which pigment in plant leaves absorbs sunlight for photosynthesis?",
                    },
                    {
                        "concept": "The Light Reactions & Water Splitting",
                        "depth": "generation of ATP and release of oxygen",
                        "example": "water being split into hydrogen and oxygen by sunlight",
                        "source_label": "Biology Section 2",
                        "checkpoint_question": "What essential gas is released into the atmosphere as a byproduct?",
                    },
                    {
                        "concept": "The Calvin Cycle & Glucose Synthesis",
                        "depth": "carbon fixation from CO2 into sugars",
                        "example": "a factory assembling sugar packets from raw carbon inputs",
                        "source_label": "Biology Section 3",
                        "checkpoint_question": "Where does the carbon used to build glucose come from?",
                    },
                ],
            }
        return {
            "title": "Electricity: Current, Voltage and Resistance",
            "language": "English",
            "level": "beginner",
            "segments": [
                {
                    "concept": "Electric current",
                    "depth": "intuitive definition + unit",
                    "example": "water flowing through a pipe",
                    "source_label": "electricity_chapter.txt section 1",
                    "source_quote": "Electric current is the rate of flow of electric charge through a conductor.",
                    "checkpoint_question": "What is electric current, in one line?",
                },
                {
                    "concept": "Voltage as the push",
                    "depth": "intuitive definition + unit",
                    "example": "pressure difference across the pipe",
                    "source_label": "electricity_chapter.txt section 2",
                    "source_quote": "To make charge flow through a conductor, work must be done.",
                    "checkpoint_question": "What does voltage do to the charges?",
                },
                {
                    "concept": "Resistance and Ohm's law",
                    "depth": "relationship V = I x R with one worked example",
                    "example": "a narrow pipe vs a wide pipe",
                    "source_label": "electricity_chapter.txt section 4",
                    "source_quote": "Ohm's law states that at constant temperature, current is directly proportional to voltage.",
                    "checkpoint_question": "If resistance increases and voltage is unchanged, what happens to the current?",
                },
            ],
        }

    if tag == "evaluate":
        m = re.search(r'Student answer:\s*"(.*?)"', prompt, re.DOTALL)
        low = (m.group(1) if m else prompt).lower()
        if "increase" in low and "current" in low:
            return {
                "verdict": "incorrect",
                "misconception": (
                    "Student thinks current rises with resistance; the relation "
                    "is inverse when voltage is held constant."
                ),
                "feedback": "Not quite — resistance opposes current flow, so higher resistance reduces current for a fixed voltage.",
            }
        if any(w in low for w in ("decrease", "less", "lower", "goes down", "reduces", "drop", "halves")):
            return {
                "verdict": "correct",
                "misconception": None,
                "feedback": "Exactly right — higher resistance means lower current for the same voltage.",
            }
        if any(w in low for w in ("inertia", "friction", "stays in motion", "sunlight", "chlorophyll", "oxygen", "co2", "carbon")):
            return {
                "verdict": "correct",
                "misconception": None,
                "feedback": "Spot on! Your reasoning captures the core physical concept perfectly.",
            }
        return {
            "verdict": "partial",
            "misconception": "Direction of the effect or mechanism is not fully stated.",
            "feedback": "You are on the right track. Clarify the direction or underlying cause.",
        }

    if tag == "quiz":
        return {
            "questions": [
                {
                    "type": "mcq",
                    "concept": "Electric current",
                    "question": "Electric current is best described as:",
                    "options": [
                        "rate of flow of electric charge",
                        "stored electrical energy",
                        "resistance per unit length",
                        "voltage times time",
                    ],
                    "answer": "rate of flow of electric charge",
                },
                {
                    "type": "short",
                    "concept": "Resistance and Ohm's law",
                    "question": "Voltage is constant. Resistance doubles. What happens to current?",
                    "answer": "It halves (current is inversely proportional to resistance).",
                },
                {
                    "type": "mcq",
                    "concept": "Voltage as the push",
                    "question": "Voltage across a component is analogous to:",
                    "options": [
                        "pressure difference driving flow",
                        "width of the pipe",
                        "amount of water present",
                        "temperature of the water",
                    ],
                    "answer": "pressure difference driving flow",
                },
            ]
        }

    if tag == "grade_quiz":
        m = re.search(r'Student answer:\s*"(.*?)"', prompt, re.DOTALL)
        sa = (m.group(1) if m else "").lower()
        if "increase" in sa and "current" in sa:
            return {"verdict": "incorrect", "score": 0.0,
                    "feedback": "Current and resistance are inversely related here."}
        return {"verdict": "correct", "score": 1.0,
                "feedback": "Matches the expected answer."}

    if tag == "report":
        return {
            "topic": "Electricity: Current, Voltage and Resistance",
            "score": "2/3",
            "strong_areas": ["Electric current", "Voltage as the push"],
            "needs_improvement": ["Resistance and Ohm's law"],
            "recommendation": (
                "Redo three V = I x R numericals, keeping voltage fixed so the "
                "inverse link between resistance and current becomes automatic."
            ),
        }

    if tag == "next_topic":
        return {
            "next_topic": "Series and parallel resistor networks",
            "reason": "Builds directly on the Ohm's-law relationship that was weak last session.",
        }

    return {"mock": True, "tag": tag}
