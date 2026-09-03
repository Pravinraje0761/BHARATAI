"""Amplitude-driven mouth-swap avatar (pure CPU).

Three mouth-state images (closed / half / open) + the audio RMS envelope ->
one mouth state per video frame. No GPU, no model download. Satisfies the
"human-like avatar" requirement without SadTalker's CUDA setup.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import config

STATES = ("closed", "half", "open")
_SIZE = (360, 360)


# --------------------------------------------------------------------------- #
# Persona images
# --------------------------------------------------------------------------- #
def _draw_face(mouth: str) -> Image.Image:
    img = Image.new("RGBA", _SIZE, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = _SIZE[0] // 2, _SIZE[1] // 2

    # head
    d.ellipse([cx - 130, cy - 150, cx + 130, cy + 160], fill=(255, 224, 189, 255),
              outline=(120, 90, 60, 255), width=3)
    # hair
    d.chord([cx - 135, cy - 175, cx + 135, cy - 40], 180, 360, fill=(60, 42, 30, 255))
    # eyes
    for ex in (cx - 48, cx + 48):
        d.ellipse([ex - 18, cy - 40, ex + 18, cy - 8], fill=(255, 255, 255, 255),
                  outline=(80, 80, 80, 255), width=2)
        d.ellipse([ex - 7, cy - 32, ex + 7, cy - 18], fill=(40, 30, 20, 255))
    # brows
    d.line([cx - 66, cy - 52, cx - 30, cy - 58], fill=(60, 42, 30, 255), width=5)
    d.line([cx + 30, cy - 58, cx + 66, cy - 52], fill=(60, 42, 30, 255), width=5)
    # nose
    d.line([cx, cy - 12, cx - 10, cy + 28], fill=(200, 160, 130, 255), width=4)
    d.line([cx - 10, cy + 28, cx + 8, cy + 30], fill=(200, 160, 130, 255), width=4)

    # mouth by state
    my = cy + 78
    if mouth == "closed":
        d.line([cx - 40, my, cx + 40, my], fill=(150, 60, 60, 255), width=6)
    elif mouth == "half":
        d.ellipse([cx - 40, my - 12, cx + 40, my + 18], fill=(120, 40, 40, 255))
        d.ellipse([cx - 26, my + 2, cx + 26, my + 16], fill=(220, 150, 150, 255))
    else:  # open
        d.ellipse([cx - 44, my - 26, cx + 44, my + 34], fill=(110, 30, 30, 255))
        d.ellipse([cx - 24, my + 6, cx + 24, my + 30], fill=(220, 150, 150, 255))
    return img


def ensure_persona(directory: Path | None = None) -> dict[str, Path]:
    """Create the 3 mouth-state PNGs if missing. Returns {state: path}."""
    directory = Path(directory or config.AVATAR_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    paths = {}
    for state in STATES:
        p = directory / f"mouth_{state}.png"
        if not p.exists():
            _draw_face(state).save(p)
        paths[state] = p
    return paths


def load_persona(directory: Path | None = None) -> dict[str, Image.Image]:
    paths = ensure_persona(directory)
    return {s: Image.open(p).convert("RGBA") for s, p in paths.items()}


# --------------------------------------------------------------------------- #
# Audio envelope -> per-frame mouth state
# --------------------------------------------------------------------------- #
def audio_duration(audio_path: str | Path) -> float:
    try:
        import soundfile as sf

        info = sf.info(str(audio_path))
        return float(info.frames) / float(info.samplerate)
    except Exception:
        pass
    try:
        import librosa

        return float(librosa.get_duration(path=str(audio_path)))
    except Exception:
        return 0.0


def mouth_states_for_audio(audio_path: str | Path, fps: int | None = None) -> list[str]:
    """One entry of STATES per video frame, from the RMS volume envelope (fast soundfile + numpy)."""
    fps = fps or config.VIDEO_FPS
    y = None
    sr = None

    try:
        import soundfile as sf

        data, sr = sf.read(str(audio_path), dtype="float32")
        if data.ndim > 1:
            y = np.mean(data, axis=1)
        else:
            y = data
    except Exception:
        try:
            import librosa

            y, sr = librosa.load(str(audio_path), sr=None, mono=True)
        except Exception:
            return ["closed"]

    if y is None or y.size == 0 or not sr:
        return ["closed"]

    hop = max(1, int(sr / fps))
    frame_len = hop * 2

    # Fast NumPy RMS calculation across hopping windows
    pad_len = frame_len // 2
    y_padded = np.pad(y, (pad_len, pad_len), mode="reflect")
    n_hops = int(np.ceil(len(y) / hop))

    rms = np.empty(n_hops, dtype=np.float32)
    for h in range(n_hops):
        start = h * hop
        chunk = y_padded[start : start + frame_len]
        rms[h] = np.sqrt(np.mean(chunk**2)) if chunk.size > 0 else 0.0

    if rms.size == 0:
        return ["closed"]

    # normalise then threshold into 3 bands
    peak = float(rms.max()) or 1.0
    norm = rms / peak
    states = []
    for v in norm:
        if v < 0.15:
            states.append("closed")
        elif v < 0.45:
            states.append("half")
        else:
            states.append("open")
    # de-jitter: no isolated single-frame flips
    for i in range(1, len(states) - 1):
        if states[i - 1] == states[i + 1] != states[i]:
            states[i] = states[i - 1]
    return states
