"""Unit tests for sync_service helper functions."""

from datetime import datetime
from decimal import Decimal

from app.services.sync_service import _parse_datetime, _safe_decimal, _safe_int


# ── _parse_datetime ─────────────────────────────────────────────


class TestParseDatetime:
    def test_iso_with_timezone(self):
        result = _parse_datetime("2026-02-08T12:00:00+03:00")
        assert result == datetime(2026, 2, 8, 12, 0, 0)
        assert result.tzinfo is None

    def test_iso_without_timezone(self):
        result = _parse_datetime("2026-02-08T14:30:00")
        assert result == datetime(2026, 2, 8, 14, 30, 0)

    def test_datetime_with_space(self):
        result = _parse_datetime("2026-02-08 09:15:00")
        assert result == datetime(2026, 2, 8, 9, 15, 0)

    def test_date_only(self):
        result = _parse_datetime("2026-02-08")
        assert result == datetime(2026, 2, 8, 0, 0, 0)

    def test_none_returns_none(self):
        assert _parse_datetime(None) is None

    def test_empty_returns_none(self):
        assert _parse_datetime("") is None

    def test_garbage_returns_none(self):
        assert _parse_datetime("not-a-date") is None


# ── _safe_decimal ───────────────────────────────────────────────


class TestSafeDecimal:
    def test_integer(self):
        assert _safe_decimal(42) == Decimal("42")

    def test_float_string(self):
        assert _safe_decimal("123.45") == Decimal("123.45")

    def test_none_returns_default(self):
        assert _safe_decimal(None) == Decimal("0")

    def test_none_custom_default(self):
        assert _safe_decimal(None, Decimal("99")) == Decimal("99")

    def test_invalid_string_returns_default(self):
        assert _safe_decimal("not-a-number") == Decimal("0")


# ── _safe_int ───────────────────────────────────────────────────


class TestSafeInt:
    def test_integer(self):
        assert _safe_int(42) == 42

    def test_string_number(self):
        assert _safe_int("7") == 7

    def test_none_returns_default(self):
        assert _safe_int(None) == 0

    def test_invalid_string_returns_default(self):
        assert _safe_int("abc") == 0

    def test_float_truncates(self):
        assert _safe_int(3.9) == 3
