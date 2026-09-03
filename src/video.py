"""Compositing: slide + picture-in-picture avatar + burned-in captions + audio.

Frames are drawn with PIL, written to a silent MP4 with OpenCV, then muxed with
the narration audio via ffmpeg. ffmpeg is located on PATH, else the binary
bundled with ``imageio-ffmpeg`` is used, so no OS-level install is required.
"""
from __future__ import annotations

import shutil
import subprocess
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import config
from src.avatar import audio_duration, load_persona, mouth_states_for_audio
from src.visuals import bullets_from_text, render_slide


def _ffmpeg_exe() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "ffmpeg not found on PATH and imageio-ffmpeg is not installed. "
            "Run: pip install imageio-ffmpeg"
        ) from exc


def _font(size: int):
    for name in ("arial.ttf", "DejaVuSans.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _caption_lines(text: str, width: int = 68) -> list[str]:
    return textwrap.wrap(" ".join(text.split()), width=width)


def _draw_caption(frame: Image.Image, text: str):
    if not text:
        return
    w, h = frame.size
    d = ImageDraw.Draw(frame, "RGBA")
    f = _font(30)
    lines = _caption_lines(text)[-3:]
    pad = 16
    line_h = 40
    box_h = line_h * len(lines) + pad * 2
    d.rectangle([0, h - box_h, w, h], fill=(0, 0, 0, 170))
    y = h - box_h + pad
    for ln in lines:
        tw = d.textlength(ln, font=f)
        d.text(((w - tw) / 2, y), ln, font=f, fill=(255, 255, 255, 255))
        y += line_h


def compose_segment_video(
    *,
    title: str,
    explanation_text: str,
    audio_path: str | Path,
    out_path: str | Path,
    subtitle: str = "",
    fps: int | None = None,
) -> Path:
    import cv2

    fps = fps or config.VIDEO_FPS
    w, h = config.VIDEO_W, config.VIDEO_H
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    audio_path = Path(audio_path)

    # 1. background slide
    slide_png = out_path.with_name(out_path.stem + "_slide.png")
    render_slide(title, bullets_from_text(explanation_text), slide_png, subtitle=subtitle)
    slide = Image.open(slide_png).convert("RGB").resize((w, h))

    # 2. avatar frames + timing
    persona = load_persona()
    av_box = 300
    persona = {k: v.resize((av_box, av_box)) for k, v in persona.items()}
    est = max(2.0, 0.35 * len(explanation_text.split()))
    try:
        dur = audio_duration(audio_path)
    except Exception:
        dur = 0.0
    if dur <= 0.5:
        dur = est
    states = mouth_states_for_audio(audio_path, fps=fps)
    n_frames = max(int(dur * fps), len(states), fps)

    cap_lines = _caption_lines(explanation_text)
    silent_mp4 = out_path.with_name(out_path.stem + "_silent.mp4")
    vw = cv2.VideoWriter(
        str(silent_mp4), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h)
    )
    if not vw.isOpened():
        raise RuntimeError("cv2.VideoWriter failed to open (mp4v codec missing?)")

    ax, ay = w - av_box - 40, h - av_box - 40

    # Pre-render gold avatar border onto slide
    slide.paste(
        Image.new("RGB", (av_box + 12, av_box + 12), (240, 190, 70)),
        (ax - 6, ay - 6),
    )

    # Pre-render composite frames for each (mouth_state, caption_step)
    # Eliminates hundreds of expensive PIL copies/composites/conversions into a fast pre-cache
    n_cap = max(1, len(cap_lines))
    cached_bgr = {}
    for st, av_img in persona.items():
        base_st = slide.copy()
        base_st.paste(av_img, (ax, ay), av_img)
        if cap_lines:
            for shown in range(1, n_cap + 1):
                f = base_st.copy()
                _draw_caption(f, " ".join(cap_lines[:shown]))
                cached_bgr[(st, shown)] = cv2.cvtColor(np.array(f), cv2.COLOR_RGB2BGR)
        else:
            cached_bgr[(st, 1)] = cv2.cvtColor(np.array(base_st), cv2.COLOR_RGB2BGR)

    default_bgr = list(cached_bgr.values())[0]

    for i in range(n_frames):
        state = states[min(i, len(states) - 1)] if states else "closed"
        shown = max(1, round((i + 1) / n_frames * len(cap_lines))) if cap_lines else 1
        vw.write(cached_bgr.get((state, shown), default_bgr))

    vw.release()

    # 3. mux audio with ultrafast preset to a temporary target, then atomic rename
    ff = _ffmpeg_exe()
    tmp_out = out_path.with_name(out_path.stem + "_rendering.mp4")
    tmp_out.unlink(missing_ok=True)

    cmd = [
        ff, "-y", "-i", str(silent_mp4), "-i", str(audio_path),
        "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage", "-crf", "26",
        "-pix_fmt", "yuv420p", "-c:a", "aac",
        "-movflags", "+faststart",
        "-shortest", str(tmp_out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not tmp_out.exists():
        # keep the silent version as a usable fallback
        shutil.copyfile(silent_mp4, out_path)
        print(f"[video] audio mux failed, kept silent video. ffmpeg said:\n{proc.stderr[-500:]}")
    else:
        tmp_out.replace(out_path)
        silent_mp4.unlink(missing_ok=True)
    return out_path


def concat_videos(parts: list[Path], out_path: str | Path) -> Path:
    """Concatenate segment MP4s into one lesson video."""
    out_path = Path(out_path)
    if not parts:
        raise ValueError("no parts to concat")
    if len(parts) == 1:
        shutil.copyfile(parts[0], out_path)
        return out_path
    listing = out_path.with_suffix(".txt")
    listing.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in parts))
    ff = _ffmpeg_exe()
    proc = subprocess.run(
        [ff, "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-c", "copy", str(out_path)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        # re-encode fallback
        subprocess.run(
            [ff, "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(out_path)],
            capture_output=True, text=True,
        )
    listing.unlink(missing_ok=True)
    return out_path
