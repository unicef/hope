import pytest

from hope.models import Area, AreaType, Country


@pytest.mark.django_db
def test_country_get_by_natural_key():
    country = Country.objects.create(
        name="Test Country",
        iso_code2="TC",
        iso_code3="TCY",
        iso_num="123",
    )
    found_country = Country.objects.get_by_natural_key("TCY")
    assert found_country == country


@pytest.mark.django_db
def test_area_type_get_by_natural_key():
    country = Country.objects.create(
        name="Test Country",
        iso_code2="TC",
        iso_code3="TCY",
        iso_num="123",
    )
    area_type = AreaType.objects.create(
        name="Test Area Type",
        country=country,
        area_level=1,
    )
    found_area_type = AreaType.objects.get_by_natural_key(
        name="Test Area Type",
        country="TCY",
        area_level=1,
    )
    assert found_area_type == area_type


@pytest.mark.django_db
def test_area_natural_key():
    country = Country.objects.create(
        name="Test Country",
        iso_code2="TC",
        iso_code3="TCY",
        iso_num="123",
    )
    area_type = AreaType.objects.create(
        name="Test Area Type",
        country=country,
        area_level=1,
    )
    area = Area.objects.create(
        name="Test Area",
        area_type=area_type,
        p_code="PCODE123",
    )
    assert area.natural_key() == (area_type, "PCODE123")


@pytest.mark.django_db
def test_area_get_by_natural_key():
    country = Country.objects.create(
        name="Test Country",
        iso_code2="TC",
        iso_code3="TCY",
        iso_num="123",
    )
    area_type = AreaType.objects.create(
        name="Test Area Type",
        country=country,
        area_level=1,
    )
    area = Area.objects.create(
        name="Test Area",
        area_type=area_type,
        p_code="PCODE123",
    )
    found_area = Area.objects.get_by_natural_key(
        p_code="PCODE123",
        name="Test Area Type",
        country="TCY",
        area_level=1,
    )
    assert found_area == area
