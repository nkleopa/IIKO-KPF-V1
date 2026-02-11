"""ETL transformation rules for iiko data."""

from decimal import Decimal

from app.core.logger import logger

# --- OrderType mapping (revenue) ---
# Exact-match whitelist per official KPF report "02 Отчет по выручке СХ"

DELIVERY_TYPES = {
    "ДОСТАВКА",                       # iiko OLAP aggregate delivery type
    "Яндекс",                         # may appear as sub-type
    "Бронибой",                        # may appear as sub-type
    "Личная курьерская доставка",      # may appear as sub-type
}

HALL_TYPES = {
    "ОБЫЧНЫЙ ЗАКАЗ",                   # iiko OLAP: regular hall order
    "Самовывоз",                       # iiko OLAP: takeout (all variants)
}


def map_order_type(raw_type: str) -> str:
    """Map iiko OrderType to delivery/hall/excluded.

    Only the whitelisted types count towards KPF revenue.
    Everything else is 'excluded'.
    """
    stripped = raw_type.strip()
    if stripped in DELIVERY_TYPES:
        return "delivery"
    if stripped in HALL_TYPES:
        return "hall"
    return "excluded"


# --- Labor exclusion rules (substring match against iiko role names) ---

EXCLUDED_LABOR_PATTERNS = ["управляющий", "су-шеф"]

# --- Kitchen roles (for KC% calculation, substring match) ---

KITCHEN_PATTERNS = ["повар", "мангал"]


def is_excluded_role(role_name: str | None) -> bool:
    """Check if a role should be excluded from hourly labor calculations."""
    if not role_name:
        return False
    lower = role_name.lower()
    return any(p in lower for p in EXCLUDED_LABOR_PATTERNS)


def is_kitchen_role(role_name: str | None) -> bool:
    """Check if a role counts towards kitchen labor (KC%)."""
    if not role_name:
        return False
    lower = role_name.lower()
    return any(p in lower for p in KITCHEN_PATTERNS)


# --- Dyuzhina Khinkali quantity rule ---


def adjust_quantity(item_name: str | None, quantity: Decimal | None) -> Decimal | None:
    """If item contains 'Дюжина Хинкали', multiply quantity by 12."""
    if quantity is None or item_name is None:
        return quantity
    if "дюжина хинкали" in item_name.lower():
        return quantity * 12
    return quantity


# --- Write-off article mapping ---

WRITEOFF_MAPPING: dict[str, str] = {
    "бракераж": "spoilage",
    "2.10.1 маркетинг": "marketing",
}


def map_writeoff_category(article_name: str) -> str:
    """Map iiko write-off article to local category."""
    lower = article_name.strip().lower()
    for key, category in WRITEOFF_MAPPING.items():
        if key in lower:
            return category
    logger.warning(f"Unknown writeoff article: '{article_name}' — mapped to 'other'")
    return "other"
