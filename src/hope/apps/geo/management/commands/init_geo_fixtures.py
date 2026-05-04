import logging
import random
from typing import Any

from django.core.management import BaseCommand, call_command

from extras.test_utils.factories import AreaFactory, AreaTypeFactory
from hope.models import Area, AreaType, Country

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        initialize_geo_fixtures()


def generate_area_types() -> None:
    for country in Country.objects.all():
        parent = None
        for area_type_name, level in [
            ("Province", 1),
            ("State", 2),
            ("County", 3),
            ("Region", 4),
            ("District", 5),
        ]:
            parent = AreaTypeFactory(parent=parent, name=area_type_name, country=country, area_level=level)


def generate_p_code(prefix: str, count: int) -> list[str]:
    """Generate a list of unique random p-codes with a given prefix."""
    return [f"{prefix}{random.randint(10, 99)}" for _ in range(count)]


CONSTANT_AFGHANISTAN_AREAS = [
    # Admin level 1
    {"level": 1, "p_code": "AF01", "name": "Kabul"},
    {"level": 1, "p_code": "AF11", "name": "Badakhshan"},
    # Admin level 2
    {"level": 2, "p_code": "AF0101", "name": "Kabul", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF0102", "name": "Dehsabz", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF0103", "name": "Shakardara", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF0104", "name": "Paghman", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF0105", "name": "Chaharasyab", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF0106", "name": "Musayi", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF0107", "name": "Bagrami", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF0108", "name": "Qarabagh", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF0109", "name": "Kalakan", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF0110", "name": "Mirbachakot", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF0111", "name": "Guldara", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF0112", "name": "Khak-e-Jabbar", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF0113", "name": "Surobi", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF0114", "name": "Estalef", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF0115", "name": "Farza", "parent_p_code": "AF01"},
    {"level": 2, "p_code": "AF1115", "name": "Argo", "parent_p_code": "AF11"},
]


def _create_constant_afghanistan_areas(country: Country) -> None:
    """Create constant areas for Afghanistan so that known p-codes are always available (e.g. for RDI Excel imports)."""
    for area_def in CONSTANT_AFGHANISTAN_AREAS:
        area_type = AreaType.objects.filter(country=country, area_level=area_def["level"]).first()
        if not area_type:
            continue
        parent = Area.objects.filter(p_code=area_def.get("parent_p_code")).first()
        AreaFactory(p_code=area_def["p_code"], name=area_def["name"], area_type=area_type, parent=parent)


def generate_areas(country_names: list[str] | None = None) -> None:
    """Create areas in every level for country in country_names or by default only for Afghanistan."""
    if country_names is None:
        country_names = ["Afghanistan"]

    for country in Country.objects.filter(short_name__in=country_names):
        # Create constant areas for Afghanistan
        if country.short_name == "Afghanistan":
            _create_constant_afghanistan_areas(country)

        p_code_prefix = country.iso_code2
        area_type_level_1 = AreaType.objects.get(country=country, area_level=1)
        area_type_level_2 = area_type_level_1.get_children().first()
        area_type_level_3 = area_type_level_2.get_children().first()
        area_type_level_4 = area_type_level_3.get_children().first()
        area_type_level_5 = area_type_level_4.get_children().first()
        # 1 level
        for p_code in generate_p_code(p_code_prefix, 3):
            area_l_1 = AreaFactory(area_type=area_type_level_1, p_code=p_code)
            # 2 level
            for p_code_l1 in generate_p_code(area_l_1.p_code, 3):
                area_l_2 = AreaFactory(area_type=area_type_level_2, p_code=p_code_l1, parent=area_l_1)
                # 3 level
                for p_code_2 in generate_p_code(area_l_2.p_code, 2):
                    area_l_3 = AreaFactory(area_type=area_type_level_3, p_code=p_code_2, parent=area_l_2)
                    # 4 level
                    for p_code_3 in generate_p_code(area_l_3.p_code, 2):
                        area_l_4 = AreaFactory(
                            area_type=area_type_level_4,
                            p_code=p_code_3,
                            parent=area_l_3,
                        )
                        # 5 level
                        for p_code_4 in generate_p_code(area_l_4.p_code, 2):
                            AreaFactory(
                                area_type=area_type_level_5,
                                p_code=p_code_4,
                                parent=area_l_4,
                            )


def initialize_geo_fixtures() -> None:
    call_command("loadcountries")
    generate_area_types()
    generate_areas()
