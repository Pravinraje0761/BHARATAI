"""Amplitude-driven mouth-swap avatar (pure CPU).

Three mouth-state images (closed / half / open) + the audio RMS envelope ->
one mouth state per video frame. No GPU, no model download. Satisfies the
"human-like avatar" requirement without SadTalker's CUDA setup.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import config

STATES = ("closed", "half", "open")
_SIZE = (360, 360)
_SIZE_HQ = (480, 480)


# --------------------------------------------------------------------------- #
# Persona images — Express (flat, fast) vs Realistic Studio (shaded, softer)
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


def _radial_shade(size: int, center_color: tuple, edge_color: tuple) -> Image.Image:
    """Cheap radial gradient disc (numpy), used for shaded skin instead of a flat fill."""
    yy, xx = np.mgrid[0:size, 0:size]
    cx = cy = size / 2
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (size / 2)
    dist = np.clip(dist, 0, 1)[..., None]
    c0 = np.array(center_color, dtype=np.float32)
    c1 = np.array(edge_color, dtype=np.float32)
    rgb = (c0 * (1 - dist) + c1 * dist).astype(np.uint8)
    return Image.fromarray(rgb, mode="RGB").convert("RGBA")


def _draw_face_hq(mouth: str) -> Image.Image:
    """Realistic Studio persona: gradient-shaded skin, soft blush/highlights,
    drop shadow, larger canvas — same amplitude-driven mouth-swap technique,
    but a noticeably more polished render for the paid tier."""
    size = _SIZE_HQ[0]
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx, cy = size // 2, size // 2

    # soft drop shadow beneath the head
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([cx - 150, cy - 130, cx + 150, cy + 210], fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, shadow)

    # head: radial-shaded skin instead of a flat fill
    head_mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(head_mask).ellipse([cx - 172, cy - 198, cx + 172, cy + 210], fill=255)
    skin = _radial_shade(size, (255, 232, 205), (222, 180, 145))
    skin.putalpha(head_mask)
    img = Image.alpha_composite(img, skin)

    d = ImageDraw.Draw(img)
    d.ellipse([cx - 172, cy - 198, cx + 172, cy + 210], outline=(150, 110, 80, 200), width=3)

    # hair with a subtle gradient sheen
    hair_mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(hair_mask).chord([cx - 178, cy - 232, cx + 178, cy - 50], 180, 360, fill=255)
    hair = _radial_shade(size, (92, 64, 45), (48, 32, 22))
    hair.putalpha(hair_mask)
    img = Image.alpha_composite(img, hair)

    d = ImageDraw.Draw(img)
    # cheek blush
    for ex in (cx - 92, cx + 92):
        blush = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        bd = ImageDraw.Draw(blush)
        bd.ellipse([ex - 30, cy + 18, ex + 30, cy + 58], fill=(235, 130, 120, 70))
        blush = blush.filter(ImageFilter.GaussianBlur(14))
        img = Image.alpha_composite(img, blush)
    d = ImageDraw.Draw(img)

    # eyes with catchlight highlight
    for ex in (cx - 64, cx + 64):
        d.ellipse([ex - 24, cy - 54, ex + 24, cy - 10], fill=(255, 255, 255, 255),
                  outline=(90, 90, 100, 255), width=2)
        d.ellipse([ex - 10, cy - 44, ex + 10, cy - 24], fill=(52, 38, 26, 255))
        d.ellipse([ex - 5, cy - 42, ex + 1, cy - 36], fill=(255, 255, 255, 230))
    # brows (gentle curve via arcs)
    d.arc([cx - 96, cy - 90, cx - 34, cy - 58], 200, 340, fill=(70, 48, 34, 255), width=6)
    d.arc([cx + 34, cy - 90, cx + 96, cy - 58], 200, 340, fill=(70, 48, 34, 255), width=6)
    # nose
    d.line([cx, cy - 16, cx - 14, cy + 38], fill=(196, 152, 122, 255), width=4)
    d.line([cx - 14, cy + 38, cx + 10, cy + 40], fill=(196, 152, 122, 255), width=4)

    # mouth by state, softer palette
    my = cy + 104
    if mouth == "closed":
        d.line([cx - 52, my, cx + 52, my], fill=(165, 78, 78, 255), width=7)
    elif mouth == "half":
        d.ellipse([cx - 52, my - 16, cx + 52, my + 22], fill=(140, 55, 55, 255))
        d.ellipse([cx - 34, my + 2, cx + 34, my + 20], fill=(232, 168, 168, 255))
    else:  # open
        d.ellipse([cx - 58, my - 34, cx + 58, my + 44], fill=(128, 42, 42, 255))
        d.ellipse([cx - 32, my + 8, cx + 32, my + 38], fill=(232, 168, 168, 255))
    return img


def ensure_persona(directory: Path | None = None, style: str = "express") -> dict[str, Path]:
    """Create the 3 mouth-state PNGs if missing. Returns {state: path}."""
    directory = Path(directory or config.AVATAR_DIR)
    if style == "realistic":
        directory = directory / "realistic"
    directory.mkdir(parents=True, exist_ok=True)
    draw_fn = _draw_face_hq if style == "realistic" else _draw_face
    paths = {}
    for state in STATES:
        p = directory / f"mouth_{state}.png"
        if not p.exists():
            draw_fn(state).save(p)
        paths[state] = p
    return paths


def load_persona(directory: Path | None = None, style: str = "express") -> dict[str, Image.Image]:
    paths = ensure_persona(directory, style=style)
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
