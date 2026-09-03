"""Text-to-speech: edge-tts (primary) with a gTTS fallback.

edge-tts gives free neural voices with no signup. If a given voice/locale
misbehaves, ``synthesize`` transparently falls back to gTTS, then to a silent
placeholder so the video pipeline never hard-fails on a demo machine offline.
"""
from __future__ import annotations

import asyncio
import wave
from pathlib import Path

import config


def _voice_for(language: str) -> str:
    return config.LANGUAGES.get(language, config.LANGUAGES["English"])["voice"]


def _lang_code(language: str) -> str:
    return config.LANGUAGES.get(language, config.LANGUAGES["English"])["code"]


async def _edge_tts_async(text: str, voice: str, out_mp3: Path) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(out_mp3))


def _try_edge(text: str, language: str, out_mp3: Path) -> bool:
    try:
        asyncio.run(_edge_tts_async(text, _voice_for(language), out_mp3))
        return out_mp3.exists() and out_mp3.stat().st_size > 512
    except Exception as exc:  # noqa: BLE001
        print(f"[tts] edge-tts failed ({exc}); trying gTTS")
        return False


def _try_gtts(text: str, language: str, out_mp3: Path) -> bool:
    try:
        from gtts import gTTS

        code = _lang_code(language)
        # gTTS natively supports ta, te, bn, gu, mr, kn, ml, hi, ur, en
        gtts_lang = code if code in ("ta", "te", "bn", "gu", "mr", "kn", "ml", "hi", "ur", "en") else "en"
        gTTS(text=text, lang=gtts_lang).save(str(out_mp3))
        return out_mp3.exists() and out_mp3.stat().st_size > 512
    except Exception as exc:  # noqa: BLE001
        print(f"[tts] gTTS failed ({exc}); using silent placeholder")
        return False


def _silent_wav(path: Path, seconds: float = 3.0, rate: int = 22050) -> None:
    frames = int(seconds * rate)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * frames)


def synthesize(text: str, language: str, out_path: str | Path) -> Path:
    """Produce an audio file for *text*. Returns the actual path written
    (extension may change to .wav if both TTS engines are unavailable)."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = (text or "").strip() or "..."

    mp3 = out_path.with_suffix(".mp3")
    if _try_edge(text, language, mp3):
        return mp3
    if _try_gtts(text, language, mp3):
        return mp3

    wav = out_path.with_suffix(".wav")
    # ~0.35s per word is a reasonable narration pace
    _silent_wav(wav, seconds=max(2.0, 0.35 * len(text.split())))
    return wav
