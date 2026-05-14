"""Geo-related factories."""

import random

import factory
from factory.django import DjangoModelFactory

from hope.models import Area, AreaType, BusinessArea, Country


class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ("name", "short_name", "iso_code2", "iso_code3", "iso_num")

    name = factory.Sequence(lambda n: f"Country {n}")
    short_name = factory.LazyAttribute(lambda o: o.name)
    iso_code2 = factory.Sequence(lambda n: f"{chr(65 + (n % 26))}{chr(65 + ((n // 26) % 26))}")  # AA, BA, CA, etc.
    iso_code3 = factory.Sequence(lambda n: f"{chr(65 + (n % 26))}{chr(65 + ((n // 26) % 26))}A")  # AAA, BAA, etc.
    iso_num = factory.Sequence(lambda n: f"{n:04d}")


class AreaTypeFactory(DjangoModelFactory):
    class Meta:
        model = AreaType
        django_get_or_create = ("name", "country", "area_level")

    name = factory.Sequence(lambda n: f"Area Type {n}")
    country = factory.SubFactory(CountryFactory)
    area_level = 1


class AreaFactory(DjangoModelFactory):
    class Meta:
        model = Area
        django_get_or_create = ("p_code",)

    name = factory.Sequence(lambda n: f"Area {n}")
    p_code = factory.Sequence(lambda n: f"PC{n:06d}")
    area_type = factory.SubFactory(AreaTypeFactory)


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
    """generate a list of unique random p-codes with a given prefix."""
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


def generate_small_areas_for_afghanistan_only() -> None:
    country = CountryFactory(
        name="Afghanistan", short_name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="0004"
    )
    business_area, _ = BusinessArea.objects.get_or_create(
        code="0060",
        defaults={
            "name": country.short_name,
            "long_name": country.name,
            "region_code": country.iso_num,
            "region_name": country.iso_code3,
            "has_data_sharing_agreement": True,
            "active": True,
            "kobo_token": "abc_test",
            "is_accountability_applicable": True,
        },
    )
    parent = None
    for area_type_name, level in [("Province", 1), ("District", 2), ("Village", 3)]:
        parent = AreaTypeFactory(parent=parent, name=area_type_name, country=country, area_level=level)

    _create_constant_afghanistan_areas(country)
