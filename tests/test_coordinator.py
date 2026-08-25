"""Unit tests for coordinator.py's month selection logic."""
from __future__ import annotations

from datetime import datetime

from custom_components.healthepro_menu.coordinator import _select_target_month


def _now(year: int, month: int, day: int = 1) -> datetime:
    return datetime(year, month, day)


def test_current_month_published_is_used():
    published = ["2026-08-01", "2026-09-01"]
    assert _select_target_month(published, _now(2026, 8)) == (2026, 8)


def test_falls_forward_to_nearest_upcoming_month():
    # Summer break: only next school year is published, current month isn't.
    published = ["2026-09-01"]
    assert _select_target_month(published, _now(2026, 8, 24)) == (2026, 9)


def test_falls_back_to_latest_past_month_when_nothing_upcoming():
    published = ["2026-05-01", "2026-06-01"]
    assert _select_target_month(published, _now(2026, 8)) == (2026, 6)


def test_empty_published_months_returns_none():
    assert _select_target_month([], _now(2026, 8)) is None


def test_picks_nearest_of_multiple_upcoming_months():
    published = ["2026-09-01", "2026-10-01"]
    assert _select_target_month(published, _now(2026, 8)) == (2026, 9)
