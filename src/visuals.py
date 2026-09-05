"""Slide rendering with PIL.

Day-2 level: clean title + bullet layout per segment. A light subject tint is
picked from keywords so Physics / History / Biology lessons look distinct
(the "subject-aware visuals" nod) without pulling in matplotlib/graphviz.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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


def _vertical_gradient(w: int, h: int, top: tuple, bottom: tuple) -> Image.Image:
    t = np.linspace(0, 1, h, dtype=np.float32).reshape(h, 1, 1)
    c0 = np.array(top, dtype=np.float32)
    c1 = np.array(bottom, dtype=np.float32)
    row = (c0 * (1 - t) + c1 * t).astype(np.uint8)
    arr = np.repeat(row, w, axis=1)
    return Image.fromarray(arr, mode="RGB")


def render_slide(
    title: str,
    bullets: list[str],
    out_path: str | Path,
    subtitle: str = "",
    size: tuple[int, int] | None = None,
    production_tier: str = "express",
) -> Path:
    w, h = size or (config.VIDEO_W, config.VIDEO_H)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    bg = _tint_for(f"{title} {subtitle} {' '.join(bullets)}")
    is_realistic = production_tier == "realistic"

    title_size, sub_size, body_size = (60, 30, 38) if is_realistic else (52, 28, 34)
    f_title = _font(title_size)
    f_sub = _font(sub_size)
    f_body = _font(body_size)

    title_wrap = 30 if is_realistic else 34
    x = 84 if is_realistic else 70
    y0 = 80 if is_realistic else 70

    # --- Pass 1: lay out every line first (text, font, color, y) so the
    # backing panel below can be sized to actually fit the content, instead
    # of an estimate that drifts out of sync whenever wrapping changes. ---
    lines: list[tuple[str, ImageFont.FreeTypeFont, tuple, int]] = []
    y = y0
    for line in textwrap.wrap(title, width=title_wrap) or [""]:
        lines.append((line, f_title, (255, 255, 255), y))
        y += 70 if is_realistic else 62
    if subtitle:
        lines.append((subtitle, f_sub, (215, 215, 230), y + 6))
        y += 52
    y += 24
    for b in bullets:
        for i, line in enumerate(textwrap.wrap(b, width=52)):
            prefix = "•  " if i == 0 else "    "
            lines.append((prefix + line, f_body, (238, 238, 245), y))
            y += 50 if is_realistic else 46
        y += 16 if is_realistic else 14
        if y > h - 90:
            break
    content_bottom = y

    # --- Pass 2: paint background, panel (sized from pass 1), then text. ---
    if is_realistic:
        darker = tuple(max(0, c - 24) for c in bg)
        img = _vertical_gradient(w, h, bg, darker).convert("RGBA")
        glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([w - 720, h - 720, w + 60, h + 60], fill=(240, 190, 70, 130))
        glow = glow.filter(ImageFilter.GaussianBlur(160))
        img = Image.alpha_composite(img, glow)
        d = ImageDraw.Draw(img, "RGBA")

        d.rounded_rectangle(
            [40, 44, min(w - 60, 1180), min(h - 40, content_bottom + 20)],
            radius=28, fill=(10, 14, 22, 140),
        )
    else:
        img = Image.new("RGB", (w, h), bg)
        d = ImageDraw.Draw(img)

    d.rectangle([0, 0, w, 12], fill=(240, 190, 70))
    d.rectangle([0, h - 8, w, h], fill=(240, 190, 70))

    for text, font, color, ty in lines:
        prefix_offset = 10 if font is f_body else 0
        d.text((x + prefix_offset, ty), text, font=font, fill=color)

    img.convert("RGB").save(out_path)
    return out_path


def bullets_from_text(text: str, max_bullets: int = 4) -> list[str]:
    """Turn an explanation paragraph into a few short bullets."""
    import re

    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 12]
    out = []
    for s in sents[:max_bullets]:
        out.append(s if len(s) <= 120 else s[:117] + "...")
    return out or [text[:120]]
