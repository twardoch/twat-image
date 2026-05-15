"""Test path setup for local src imports."""
# this_file: tests/conftest.py

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
