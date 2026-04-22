"""Shared test fixtures."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def april_overwrites() -> list[dict]:
    with open(FIXTURE_DIR / "april_2026_overwrites.json") as f:
        return json.load(f)["data"]


@pytest.fixture
def school_day_record(april_overwrites) -> dict:
    """First non-off-day record in April 2026 (April 1)."""
    return april_overwrites[0]


@pytest.fixture
def spring_break_record(april_overwrites) -> dict:
    """A Spring Break day (April 7)."""
    return next(r for r in april_overwrites if r["day"] == "2026-04-07")
