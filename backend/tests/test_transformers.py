"""Unit tests for ETL transformation rules."""

from decimal import Decimal

from app.services.transformers import (
    EXTERNAL_DELIVERY_SOURCES,
    HALL_TYPES,
    adjust_quantity,
    get_labor_group,
    is_excluded_role,
    is_hall_role,
    is_kitchen_role,
    map_order_type,
    map_writeoff_category,
)


# ── map_order_type ──────────────────────────────────────────────


class TestMapOrderType:
    # Delivery via external sources
    def test_broniboy_source_is_delivery(self):
        assert map_order_type("Самовывоз", "Broniboy") == "delivery"

    def test_yandex_source_is_delivery(self):
        assert map_order_type("Самовывоз", "yandex_food") == "delivery"

    def test_delivery_club_source_is_delivery(self):
        assert map_order_type("Самовывоз", "delivery_club") == "delivery"

    def test_external_source_overrides_any_order_type(self):
        # Even an unknown OrderType becomes delivery if source is external
        assert map_order_type("WHATEVER", "Broniboy") == "delivery"

    # Hall types
    def test_obychny_zakaz_is_hall(self):
        assert map_order_type("ОБЫЧНЫЙ ЗАКАЗ") == "hall"

    def test_samovyvoz_without_source_is_hall(self):
        assert map_order_type("Самовывоз") == "hall"

    def test_s_soboy_is_hall(self):
        assert map_order_type("С СОБОЙ (СС)") == "hall"

    def test_predzakaz_is_hall(self):
        assert map_order_type("ПРЕДЗАКАЗ") == "hall"

    # Own-brand source still uses OrderType logic (not external)
    def test_own_brand_source_samovyvoz_is_hall(self):
        assert map_order_type("Самовывоз", "хинкалыч.рф") == "hall"

    # Excluded
    def test_unknown_type_no_source_is_excluded(self):
        assert map_order_type("SOME_UNKNOWN_TYPE") == "excluded"

    def test_empty_type_is_excluded(self):
        assert map_order_type("") == "excluded"

    # Edge cases
    def test_whitespace_stripping(self):
        assert map_order_type("  ОБЫЧНЫЙ ЗАКАЗ  ") == "hall"

    def test_none_source_falls_through(self):
        assert map_order_type("ОБЫЧНЫЙ ЗАКАЗ", None) == "hall"

    def test_empty_string_source_falls_through(self):
        assert map_order_type("ОБЫЧНЫЙ ЗАКАЗ", "") == "hall"

    def test_all_external_sources_covered(self):
        assert EXTERNAL_DELIVERY_SOURCES == {"Broniboy", "yandex_food", "delivery_club"}

    def test_all_hall_types_covered(self):
        assert HALL_TYPES == {"ОБЫЧНЫЙ ЗАКАЗ", "Самовывоз", "С СОБОЙ (СС)", "ПРЕДЗАКАЗ"}


# ── is_excluded_role ────────────────────────────────────────────


class TestIsExcludedRole:
    def test_manager_exact(self):
        assert is_excluded_role("Управляющий") is True

    def test_manager_lowercase(self):
        assert is_excluded_role("управляющий") is True

    def test_manager_with_suffix(self):
        assert is_excluded_role("Управляющий / Бухгалтер СВОБ") is True

    def test_sous_chef_exact(self):
        assert is_excluded_role("Су-шеф") is True

    def test_sous_chef_lowercase(self):
        assert is_excluded_role("су-шеф") is True

    def test_sous_chef_with_suffix(self):
        assert is_excluded_role("Су-шеф СВОБ") is True

    def test_cook_not_excluded(self):
        assert is_excluded_role("Повар СВОБ") is False

    def test_waiter_not_excluded(self):
        assert is_excluded_role("Официант СВОБ") is False

    def test_none_not_excluded(self):
        assert is_excluded_role(None) is False

    def test_empty_not_excluded(self):
        assert is_excluded_role("") is False


# ── is_kitchen_role ─────────────────────────────────────────────


class TestIsKitchenRole:
    def test_cook(self):
        assert is_kitchen_role("Повар СВОБ") is True

    def test_cook_lowercase(self):
        assert is_kitchen_role("повар") is True

    def test_cook_mangal(self):
        assert is_kitchen_role("Повар Мангал РАСП") is True

    def test_mangal_standalone(self):
        assert is_kitchen_role("Мангал") is True

    def test_waiter_not_kitchen(self):
        assert is_kitchen_role("Официант СВОБ") is False

    def test_dishwasher_not_kitchen(self):
        assert is_kitchen_role("Посудомойка СВОБ") is False

    def test_admin_not_kitchen(self):
        assert is_kitchen_role("Администратор зала СВОБ") is False

    def test_hostess_not_kitchen(self):
        assert is_kitchen_role("Хостес СВОБ") is False

    def test_zagotovshchik_is_kitchen(self):
        assert is_kitchen_role("Заготовщик СВОБ") is True

    def test_none_not_kitchen(self):
        assert is_kitchen_role(None) is False

    def test_empty_not_kitchen(self):
        assert is_kitchen_role("") is False


# ── is_hall_role ───────────────────────────────────────────────


class TestIsHallRole:
    def test_waiter(self):
        assert is_hall_role("Официант СВОБ") is True

    def test_hostess(self):
        assert is_hall_role("Хостес СВОБ") is True

    def test_runner(self):
        assert is_hall_role("Раннер") is True

    def test_bartender(self):
        assert is_hall_role("Бармен СВОБ") is True

    def test_admin(self):
        assert is_hall_role("Администратор зала СВОБ") is True

    def test_cook_not_hall(self):
        assert is_hall_role("Повар СВОБ") is False

    def test_dishwasher_not_hall(self):
        assert is_hall_role("Посудомойка СВОБ") is False

    def test_none_not_hall(self):
        assert is_hall_role(None) is False

    def test_empty_not_hall(self):
        assert is_hall_role("") is False


# ── get_labor_group ────────────────────────────────────────────


class TestGetLaborGroup:
    def test_cook_is_kitchen(self):
        assert get_labor_group("Повар СВОБ") == "kitchen"

    def test_mangal_is_kitchen(self):
        assert get_labor_group("Мангал РАСП") == "kitchen"

    def test_zagotovshchik_is_kitchen(self):
        assert get_labor_group("Заготовщик СВОБ") == "kitchen"

    def test_waiter_is_hall(self):
        assert get_labor_group("Официант СВОБ") == "hall"

    def test_admin_is_hall(self):
        assert get_labor_group("Администратор зала СВОБ") == "hall"

    def test_bartender_is_hall(self):
        assert get_labor_group("Бармен СВОБ") == "hall"

    def test_dishwasher_is_other(self):
        assert get_labor_group("Посудомойка СВОБ") == "other"

    def test_none_is_other(self):
        assert get_labor_group(None) == "other"

    def test_empty_is_other(self):
        assert get_labor_group("") == "other"


# ── adjust_quantity ─────────────────────────────────────────────


class TestAdjustQuantity:
    def test_dyuzhina_multiplied_by_12(self):
        result = adjust_quantity("Дюжина Хинкали", Decimal("2"))
        assert result == Decimal("24")

    def test_dyuzhina_case_insensitive(self):
        result = adjust_quantity("дюжина хинкали классические", Decimal("1"))
        assert result == Decimal("12")

    def test_regular_item_unchanged(self):
        result = adjust_quantity("Хачапури по-аджарски", Decimal("3"))
        assert result == Decimal("3")

    def test_none_item_name_returns_quantity(self):
        result = adjust_quantity(None, Decimal("5"))
        assert result == Decimal("5")

    def test_none_quantity_returns_none(self):
        result = adjust_quantity("Дюжина Хинкали", None)
        assert result is None

    def test_both_none(self):
        result = adjust_quantity(None, None)
        assert result is None

    def test_zero_quantity(self):
        result = adjust_quantity("Дюжина Хинкали", Decimal("0"))
        assert result == Decimal("0")


# ── map_writeoff_category ──────────────────────────────────────


class TestMapWriteoffCategory:
    # Spoilage
    def test_spoilage_brakerazh(self):
        assert map_writeoff_category("Бракераж") == "spoilage"

    def test_spoilage_brakerazh_double_k(self):
        assert map_writeoff_category("*4.13.Браккераж") == "spoilage"

    def test_spoilage_porcha(self):
        assert map_writeoff_category("*4.10.Порча продуктов") == "spoilage"

    def test_spoilage_porcha_employee(self):
        assert map_writeoff_category("*4.11.Порча по вине сотрудника") == "spoilage"

    def test_spoilage_dospisanie(self):
        assert map_writeoff_category("*4.9.Досписание отходов") == "spoilage"

    # Marketing
    def test_marketing(self):
        assert map_writeoff_category("2.10. Маркетинг") == "marketing"

    def test_marketing_iiko(self):
        assert map_writeoff_category("*5.6.Маркетинг") == "marketing"

    def test_marketing_mystery_shopper(self):
        assert map_writeoff_category("2.9.3 Тайный гость") == "marketing"

    # Staff meals
    def test_staff_meals_personnel(self):
        assert map_writeoff_category("*5.10.25.Питание персонала") == "staff_meals"

    def test_staff_meals_sotrudnikov(self):
        assert map_writeoff_category("2.8.4.Питание сотрудников") == "staff_meals"

    # Promo
    def test_promo_labyrinth(self):
        assert map_writeoff_category("*5.4.1.Лабиринты") == "promo"

    def test_promo_birthday(self):
        assert map_writeoff_category("*5.4.2.День рождения") == "promo"

    def test_promo_compliment(self):
        assert map_writeoff_category("*5.5.1.Комплимент") == "promo"

    def test_promo_gift(self):
        assert map_writeoff_category("*5.4.6.Подарок внутри") == "promo"

    def test_promo_certificate(self):
        assert map_writeoff_category("*5.4.10.Сертификат") == "promo"

    def test_promo_ugoshenie(self):
        assert map_writeoff_category("*5.5.2.Угощение гостей") == "promo"

    def test_promo_banquet(self):
        assert map_writeoff_category("Банкет") == "promo"

    # Beer drain
    def test_beer_drain(self):
        assert map_writeoff_category("*4.12.Слив пива") == "beer_drain"

    def test_beer_drain_system(self):
        assert map_writeoff_category("Слив системы") == "beer_drain"

    # Consumables
    def test_consumables_oil(self):
        assert map_writeoff_category("*4.7.Масло на фритюр") == "consumables"

    def test_consumables_dishes(self):
        assert map_writeoff_category("*5.10.29.Износ посуды, бой") == "consumables"

    def test_consumables_household(self):
        assert map_writeoff_category("*5.10.26.Хозяйственные товары") == "consumables"

    def test_consumables_packaging(self):
        assert map_writeoff_category("*5.10.38.Упаковка/Одноразовая посуда") == "consumables"

    # R&D
    def test_rnd_prorabotka(self):
        assert map_writeoff_category("*4.8.Проработка") == "r_and_d"

    def test_rnd_degustation(self):
        assert map_writeoff_category("Дегустация") == "r_and_d"

    # COGS
    def test_cogs(self):
        assert map_writeoff_category("*4.6.Себестоимость") == "cogs"

    # Founders meals
    def test_founders_meals(self):
        assert map_writeoff_category("*3.1.Питание учредителей") == "founders_meals"

    def test_founders_admin(self):
        assert map_writeoff_category("304. Питание администрации") == "founders_meals"

    def test_founders_representative(self):
        assert map_writeoff_category("Представительские и командировочные") == "founders_meals"

    # Other / unknown
    def test_unknown_returns_other(self):
        assert map_writeoff_category("some-random-article-uuid") == "other"

    def test_whitespace_stripped(self):
        assert map_writeoff_category("  Бракераж  ") == "spoilage"

    def test_case_insensitive(self):
        assert map_writeoff_category("бракераж") == "spoilage"
