# this_file: tests/test_cli.py
"""Subprocess-based CLI smoke tests for twat-image Fire CLI."""

from __future__ import annotations

import re
import subprocess
import sys

PYTHON = sys.executable
MODULE = "twat_image"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, "-m", MODULE, *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_help_exits_zero():
    """twat-image --help exits 0 and produces output (Fire writes help to stderr)."""
    result = run("--help")
    assert result.returncode == 0, f"--help returned {result.returncode}\n{result.stderr}"
    combined = result.stdout + result.stderr
    assert combined, "--help produced no output on stdout or stderr"


def test_version_leaf_prints_semver():
    """twat-image version prints a semver string."""
    result = run("version")
    assert result.returncode == 0, f"version returned {result.returncode}\n{result.stderr}"
    output = (result.stdout + result.stderr).strip()
    assert re.search(r"\d+\.\d+\.\d+", output), f"No semver found in output: {output!r}"


def test_gray2alpha_help_exits_zero():
    """twat-image gray2alpha --help exits 0."""
    result = run("gray2alpha", "--help")
    assert result.returncode == 0, f"gray2alpha --help returned {result.returncode}\n{result.stderr}"


def test_info_help_exits_zero():
    """twat-image info --help exits 0."""
    result = run("info", "--help")
    assert result.returncode == 0, f"info --help returned {result.returncode}\n{result.stderr}"


def test_convert_help_exits_zero():
    """twat-image convert --help exits 0."""
    result = run("convert", "--help")
    assert result.returncode == 0, f"convert --help returned {result.returncode}\n{result.stderr}"


def test_scale_help_exits_zero():
    """twat-image scale --help exits 0."""
    result = run("scale", "--help")
    assert result.returncode == 0, f"scale --help returned {result.returncode}\n{result.stderr}"


def test_crop_help_exits_zero():
    """twat-image crop --help exits 0."""
    result = run("crop", "--help")
    assert result.returncode == 0, f"crop --help returned {result.returncode}\n{result.stderr}"


def test_outcrop_help_exits_zero():
    """twat-image outcrop --help exits 0."""
    result = run("outcrop", "--help")
    assert result.returncode == 0, f"outcrop --help returned {result.returncode}\n{result.stderr}"


def test_normalize_help_exits_zero():
    """twat-image normalize --help exits 0."""
    result = run("normalize", "--help")
    assert result.returncode == 0, f"normalize --help returned {result.returncode}\n{result.stderr}"


def test_genai_help_exits_zero():
    """twat-image genai --help exits 0."""
    result = run("genai", "--help")
    assert result.returncode == 0, f"genai --help returned {result.returncode}\n{result.stderr}"
