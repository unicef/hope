import logging
from typing import Any

from django.core.management import BaseCommand, call_command

from extras.test_utils.factories import AreaFactory
from extras.test_utils.factories.geo import (
    _create_constant_afghanistan_areas,
    generate_area_types,
    generate_p_code,
)
from hope.models import AreaType, Country

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        initialize_geo_fixtures()


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
