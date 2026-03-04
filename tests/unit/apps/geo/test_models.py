"""Tests for natural keys on Country, AreaType, and Area models."""

import pytest

from extras.test_utils.factories import AreaFactory, AreaTypeFactory, CountryFactory
from hope.models import Area, AreaType, Country

pytestmark = pytest.mark.django_db


@pytest.fixture
def country(db):
    return CountryFactory(
        name="Test Country",
        iso_code2="TC",
        iso_code3="TCY",
        iso_num="123",
    )


@pytest.fixture
def area_type(country):
    return AreaTypeFactory(
        name="Test Area Type",
        country=country,
        area_level=1,
    )


@pytest.fixture
def area(area_type):
    return AreaFactory(
        name="Test Area",
        area_type=area_type,
        p_code="PCODE123",
    )


def test_country_get_by_natural_key(country):
    found_country = Country.objects.get_by_natural_key("TCY")

    assert found_country == country


def test_area_type_get_by_natural_key(area_type):
    found_area_type = AreaType.objects.get_by_natural_key(
        name="Test Area Type",
        country="TCY",
        area_level=1,
    )

    assert found_area_type == area_type


def test_area_natural_key_returns_expected_tuple(area, area_type):
    assert area.natural_key() == (area_type, "PCODE123")


def test_area_get_by_natural_key(area):
    found_area = Area.objects.get_by_natural_key(
        p_code="PCODE123",
        name="Test Area Type",
        country="TCY",
        area_level=1,
    )
    assert found_area == area
