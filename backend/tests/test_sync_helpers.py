"""Unit tests for sync_service helper functions."""

from datetime import datetime
from decimal import Decimal

from app.services.sync_service import _compute_fullness, _parse_datetime, _safe_decimal, _safe_int


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


# ── _compute_fullness ─────────────────────────────────────────


class TestComputeFullness:
    MAPPING = {
        "Хинкали": "main",
        "Горячие блюда": "main",
        "Закуски и салаты": "side",
        "Холодные напитки": "drink",
        "Сладкое": "dessert",
        "Упаковка": None,  # ignored
    }

    def test_ideal_check_has_4_categories(self):
        rows = [
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Хинкали"},
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Закуски и салаты"},
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Холодные напитки"},
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Сладкое"},
        ]
        result = _compute_fullness(rows, self.MAPPING)
        avg_f, pct_i = result[("2026-02-21", "Иван")]
        assert avg_f == Decimal("4.0")
        assert pct_i == Decimal("100.0")

    def test_partial_check(self):
        rows = [
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Хинкали"},
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Холодные напитки"},
        ]
        result = _compute_fullness(rows, self.MAPPING)
        avg_f, pct_i = result[("2026-02-21", "Иван")]
        assert avg_f == Decimal("2.0")
        assert pct_i == Decimal("0.0")

    def test_mixed_checks(self):
        """2 checks: one ideal (4 cat), one with 2 cat → avg=3.0, pct=50%."""
        rows = [
            # Check 1: ideal
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Хинкали"},
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Закуски и салаты"},
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Холодные напитки"},
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Сладкое"},
            # Check 2: only main + drink
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "2", "WaiterName": "Иван", "DishGroup.SecondParent": "Горячие блюда"},
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "2", "WaiterName": "Иван", "DishGroup.SecondParent": "Холодные напитки"},
        ]
        result = _compute_fullness(rows, self.MAPPING)
        avg_f, pct_i = result[("2026-02-21", "Иван")]
        assert avg_f == Decimal("3.0")
        assert pct_i == Decimal("50.0")

    def test_ignored_groups_not_counted(self):
        rows = [
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Хинкали"},
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Упаковка"},
        ]
        result = _compute_fullness(rows, self.MAPPING)
        avg_f, pct_i = result[("2026-02-21", "Иван")]
        assert avg_f == Decimal("1.0")
        assert pct_i == Decimal("0.0")

    def test_duplicate_category_counted_once(self):
        """Two main dishes in same check → still 1 category."""
        rows = [
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Хинкали"},
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Горячие блюда"},
        ]
        result = _compute_fullness(rows, self.MAPPING)
        avg_f, pct_i = result[("2026-02-21", "Иван")]
        assert avg_f == Decimal("1.0")

    def test_empty_rows(self):
        result = _compute_fullness([], self.MAPPING)
        assert result == {}

    def test_multiple_waiters(self):
        rows = [
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Хинкали"},
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "2", "WaiterName": "Мария", "DishGroup.SecondParent": "Хинкали"},
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "2", "WaiterName": "Мария", "DishGroup.SecondParent": "Холодные напитки"},
        ]
        result = _compute_fullness(rows, self.MAPPING)
        assert result[("2026-02-21", "Иван")][0] == Decimal("1.0")
        assert result[("2026-02-21", "Мария")][0] == Decimal("2.0")

    def test_only_ignored_groups_not_in_result(self):
        """Check with only ignored groups doesn't appear in results."""
        rows = [
            {"OpenDate.Typed": "2026-02-21", "OrderNum": "1", "WaiterName": "Иван", "DishGroup.SecondParent": "Упаковка"},
        ]
        result = _compute_fullness(rows, self.MAPPING)
        assert ("2026-02-21", "Иван") not in result
