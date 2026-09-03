"""Slide rendering with PIL.

Day-2 level: clean title + bullet layout per segment. A light subject tint is
picked from keywords so Physics / History / Biology lessons look distinct
(the "subject-aware visuals" nod) without pulling in matplotlib/graphviz.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import config

_SUBJECT_TINTS = {
    "physics": (28, 40, 66), "electric": (28, 40, 66), "force": (28, 40, 66),
    "chemistry": (30, 55, 44), "reaction": (30, 55, 44),
    "biology": (44, 32, 54), "cell": (44, 32, 54),
    "history": (66, 46, 28), "war": (66, 46, 28), "empire": (66, 46, 28),
    "math": (24, 24, 24), "equation": (24, 24, 24), "algebra": (24, 24, 24),
}
_DEFAULT_TINT = (22, 28, 38)


def _font(size: int):
    for name in ("arial.ttf", "DejaVuSans.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _tint_for(text: str):
    low = (text or "").lower()
    for key, col in _SUBJECT_TINTS.items():
        if key in low:
            return col
    return _DEFAULT_TINT


def render_slide(
    title: str,
    bullets: list[str],
    out_path: str | Path,
    subtitle: str = "",
    size: tuple[int, int] | None = None,
) -> Path:
    w, h = size or (config.VIDEO_W, config.VIDEO_H)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    bg = _tint_for(f"{title} {subtitle} {' '.join(bullets)}")
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)

    # accent bar
    d.rectangle([0, 0, w, 12], fill=(240, 190, 70))
    d.rectangle([0, h - 8, w, h], fill=(240, 190, 70))

    f_title = _font(52)
    f_sub = _font(28)
    f_body = _font(34)

    y = 70
    for line in textwrap.wrap(title, width=34) or [""]:
        d.text((70, y), line, font=f_title, fill=(255, 255, 255))
        y += 62
    if subtitle:
        d.text((72, y + 6), subtitle, font=f_sub, fill=(210, 210, 220))
        y += 48
    y += 20

    for b in bullets:
        for i, line in enumerate(textwrap.wrap(b, width=52)):
            prefix = "•  " if i == 0 else "    "
            d.text((80, y), prefix + line, font=f_body, fill=(235, 235, 240))
            y += 46
        y += 14
        if y > h - 90:
            break

    img.save(out_path)
    return out_path


def bullets_from_text(text: str, max_bullets: int = 4) -> list[str]:
    """Turn an explanation paragraph into a few short bullets."""
    import re

    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 12]
    out = []
    for s in sents[:max_bullets]:
        out.append(s if len(s) <= 120 else s[:117] + "...")
    return out or [text[:120]]
