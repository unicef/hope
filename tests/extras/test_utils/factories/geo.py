import random
from typing import List, Optional

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area, AreaType, Country

faker = Faker()


class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ("name", "short_name", "iso_code2", "iso_code3", "iso_num")

    name = "Afghanistan"
    short_name = "Afghanistan"
    iso_code2 = "AF"
    iso_code3 = "AFG"
    iso_num = "0004"
    parent = None


class AreaTypeFactory(DjangoModelFactory):
    class Meta:
        model = AreaType
        django_get_or_create = ("name", "country", "area_level")

    name = factory.LazyFunction(faker.domain_word)
    country = factory.SubFactory(CountryFactory)
    area_level = fuzzy.FuzzyChoice([1, 2, 3, 4])
    parent = None


class AreaFactory(DjangoModelFactory):
    class Meta:
        model = Area
        django_get_or_create = ("p_code",)

    name = factory.LazyFunction(faker.city)
    parent = None
    p_code = factory.LazyFunction(lambda: faker.bothify(text="AF@@@@@@"))
    area_type = factory.SubFactory(AreaTypeFactory)


def generate_area_types() -> None:
    for country in Country.objects.all():
        parent = None
        for area_type_name, level in [("Province", 1), ("State", 2), ("County", 3), ("Region", 4), ("District", 5)]:
            parent = AreaTypeFactory(parent=parent, name=area_type_name, country=country, area_level=level)


def generate_p_code(prefix: str, count: int) -> List[str]:
    """generate a list of unique random p-codes with a given prefix."""
    return [f"{prefix}{random.randint(10, 99)}" for _ in range(count)]


def generate_areas(country_names: Optional[List[str]] = None) -> None:
    """create areas in every level for country in country_names or by default only for Afghanistan"""
    if country_names is None:
        country_names = ["Afghanistan"]
    print(f"Generating Areas for {country_names}")
    for country in Country.objects.filter(short_name__in=country_names):
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
            for p_code in generate_p_code(area_l_1.p_code, 3):
                area_l_2 = AreaFactory(area_type=area_type_level_2, p_code=p_code, parent=area_l_1)
                # 3 level
                for p_code in generate_p_code(area_l_2.p_code, 2):
                    area_l_3 = AreaFactory(area_type=area_type_level_3, p_code=p_code, parent=area_l_2)
                    # 4 level
                    for p_code in generate_p_code(area_l_3.p_code, 2):
                        area_l_4 = AreaFactory(area_type=area_type_level_4, p_code=p_code, parent=area_l_3)
                        # 5 level
                        for p_code in generate_p_code(area_l_4.p_code, 2):
                            AreaFactory(area_type=area_type_level_5, p_code=p_code, parent=area_l_4)


def generate_small_areas_for_afghanistan_only() -> None:
    country = CountryFactory()
    business_area, _ = BusinessArea.objects.get_or_create(
        code="0060",
        defaults=dict(
            name=country.short_name,
            long_name=country.name,
            region_code=country.iso_num,
            region_name=country.iso_code3,
            has_data_sharing_agreement=True,
            active=True,
            kobo_token="abc_test",
            is_accountability_applicable=True,
        ),
    )
    parent = None
    for area_type_name, level in [("Province", 1), ("District", 2), ("Village", 3)]:
        parent = AreaTypeFactory(parent=parent, name=area_type_name, country=country, area_level=level)

    areas = [
        {"level": 1, "p_code": "AF01", "name": "Kabul"},
        {"level": 2, "p_code": "AF0107", "name": "Bagrami", "parent_name": "Kabul"},
        {"level": 2, "p_code": "AF0105", "name": "Chaharasyab", "parent_name": "Kabul"},
        {"level": 2, "p_code": "AF0110", "name": "Mirbachakot", "parent_name": "Kabul"},
        {"level": 2, "p_code": "AF0111", "name": "Guldara", "parent_name": "Kabul"},
        {"level": 2, "p_code": "AF0108", "name": "Qarabagh", "parent_name": "Kabul"},
        {"level": 2, "p_code": "AF0114", "name": "Estalef", "parent_name": "Kabul"},
        {"level": 2, "p_code": "AF0106", "name": "Musayi", "parent_name": "Kabul"},
        {"level": 2, "p_code": "AF0109", "name": "Kalakan", "parent_name": "Kabul"},
        {"level": 2, "p_code": "AF0115", "name": "Farza", "parent_name": "Kabul"},
        {"level": 2, "p_code": "AF0113", "name": "Surobi", "parent_name": "Kabul"},
        {"level": 2, "p_code": "AF0101", "name": "Kabul", "parent_name": "Kabul"},
        {"level": 2, "p_code": "AF0112", "name": "Khak-e-Jabbar", "parent_name": "Kabul"},
        {"level": 2, "p_code": "AF0104", "name": "Paghman", "parent_name": "Kabul"},
        {"level": 2, "p_code": "AF0102", "name": "Dehsabz", "parent_name": "Kabul"},
        {"level": 2, "p_code": "AF0103", "name": "Shakardara", "parent_name": "Kabul"},
    ]
    area_type_level_1 = AreaType.objects.filter(country=country, area_level=1).first()
    area_type_level_2 = AreaType.objects.filter(country=country, area_level=2).first()
    for area in areas:
        parent = None if not area.get("parent_name") else Area.objects.filter(name=area["parent_name"]).first()
        area_type = area_type_level_1 if area["level"] == 1 else area_type_level_2
        AreaFactory(p_code=area["p_code"], name=area["name"], area_type=area_type, parent=parent)
