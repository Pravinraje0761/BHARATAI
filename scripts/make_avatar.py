"""Regenerate the 3 avatar mouth-state images. Run once, then hand-edit if wanted."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.avatar import ensure_persona  # noqa: E402

if __name__ == "__main__":
    paths = ensure_persona()
    for state, p in paths.items():
        print(f"{state:>7}: {p}")
