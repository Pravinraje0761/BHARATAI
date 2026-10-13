"""Every test gets its own working directory and database, and no API keys."""
import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def isolated_workdir(tmp_path, monkeypatch):
    monkeypatch.setenv("AITEACHER_WORKDIR", str(tmp_path))
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY", "NVIDIA_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    import config
    importlib.reload(config)
    yield tmp_path
