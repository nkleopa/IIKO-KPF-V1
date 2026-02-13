"""ETL transformation rules for iiko data."""

from decimal import Decimal

from app.core.logger import logger

# --- OrderType mapping (revenue) ---
# Uses iiko OLAP fields: OrderType + Delivery.SourceKey
#
# Delivery.SourceKey identifies the external delivery platform.
# External platforms → "delivery"; everything else uses OrderType whitelist.

EXTERNAL_DELIVERY_SOURCES = {
    "Broniboy",
    "yandex_food",
    "delivery_club",
}

HALL_TYPES = {
    "ОБЫЧНЫЙ ЗАКАЗ",                   # iiko OLAP: regular hall order
    "Самовывоз",                       # iiko OLAP: takeout (all variants)
    "С СОБОЙ (СС)",                    # iiko OLAP: takeaway
    "ПРЕДЗАКАЗ",                       # iiko OLAP: pre-order
}


def map_order_type(raw_type: str, delivery_source: str | None = None) -> str:
    """Map iiko OrderType + Delivery.SourceKey to delivery/hall/excluded.

    1. If delivery_source is an external platform → "delivery"
    2. Elif OrderType in HALL_TYPES → "hall"
    3. Else → "excluded"
    """
    if delivery_source and delivery_source in EXTERNAL_DELIVERY_SOURCES:
        return "delivery"
    stripped = raw_type.strip()
    if stripped in HALL_TYPES:
        return "hall"
    return "excluded"


# --- Labor exclusion rules (substring match against iiko role names) ---

EXCLUDED_LABOR_PATTERNS = ["управляющий", "су-шеф"]

# --- Kitchen roles (for KC% calculation, substring match) ---

KITCHEN_PATTERNS = ["повар", "мангал", "заготовщик"]

# --- Hall roles (for hall labor sub-total, substring match) ---

HALL_PATTERNS = ["официант", "хостес", "раннер", "бармен", "администратор"]


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


def is_hall_role(role_name: str | None) -> bool:
    """Check if a role counts towards hall labor."""
    if not role_name:
        return False
    lower = role_name.lower()
    return any(p in lower for p in HALL_PATTERNS)


def get_labor_group(role_name: str | None) -> str:
    """Classify role into kitchen/hall/other."""
    if is_kitchen_role(role_name):
        return "kitchen"
    if is_hall_role(role_name):
        return "hall"
    return "other"


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
    # Spoilage (Бракераж/Порча)
    "бракераж": "spoilage",       # single к (correct spelling)
    "браккераж": "spoilage",      # double к (iiko variant)
    "порча": "spoilage",
    "досписание отходов": "spoilage",
    # Marketing
    "маркетинг": "marketing",
    "тайный гость": "marketing",
    # Staff meals
    "питание персонала": "staff_meals",
    "питание сотрудников": "staff_meals",
    # Dish removal
    "удаление блюд": "dish_removal",
    # Promo / Gifts
    "акции": "promo",
    "комплимент": "promo",
    "угощение": "promo",
    "день рождения": "promo",
    "лабиринт": "promo",
    "сертификат": "promo",
    "подарок": "promo",
    "лотерея": "promo",
    "аджарики": "promo",
    "кубики удачи": "promo",
    "банкет": "promo",
    # Beer drain
    "слив пива": "beer_drain",
    "слив системы": "beer_drain",
    "промывка системы": "beer_drain",
    # Consumables
    "масло на фритюр": "consumables",
    "списание масла": "consumables",
    "упаковка": "consumables",
    "расходные": "consumables",
    "хозяйственные": "consumables",
    "хозтовары": "consumables",
    "износ посуды": "consumables",
    "посуда персонал": "consumables",
    "аптечка": "consumables",
    # R&D
    "проработка": "r_and_d",
    "дегустация": "r_and_d",
    # COGS
    "себестоимость": "cogs",
    # Founders meals
    "питание учредителей": "founders_meals",
    "питание администрации": "founders_meals",
    "представительские": "founders_meals",
    # Explicitly other
    "неплательщики": "other",
    "финансирование": "other",
}


def map_writeoff_category(article_name: str) -> str:
    """Map iiko write-off account name to local category."""
    lower = article_name.strip().lower()
    for key, category in WRITEOFF_MAPPING.items():
        if key in lower:
            return category
    logger.warning(f"Unknown writeoff article: '{article_name}' — mapped to 'other'")
    return "other"
