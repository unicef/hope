import pytest

from extras.test_utils.factories.core import CountryCodeMapFactory
from extras.test_utils.factories.geo import CountryFactory
from hope.models import CountryCodeMap


@pytest.fixture
def afghanistan(db):
    return CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="0004",
    )


@pytest.fixture
def australia(db):
    return CountryFactory(
        name="Australia",
        short_name="Australia",
        iso_code2="AU",
        iso_code3="AUS",
        iso_num="0036",
    )


@pytest.fixture
def country_code_maps(afghanistan, australia):
    afg_map = CountryCodeMapFactory(country=afghanistan, ca_code="AFG")
    aus_map = CountryCodeMapFactory(country=australia, ca_code="AUL")
    return afg_map, aus_map


@pytest.mark.parametrize(
    ("iso_code", "expected"),
    [
        ("AFG", "AFG"),
        ("afg", "AFG"),
        ("af", "AFG"),
        ("AUS", "AUL"),
    ],
    ids=["equal", "case_insensitive", "alpha2", "custom_code"],
)
def test_country_code_map_get_code_returns_expected_ca_code(country_code_maps, iso_code, expected):
    result = CountryCodeMap.objects.get_code(iso_code)

    assert result == expected


@pytest.mark.parametrize(
    ("ca_code", "expected"),
    [
        ("AFG", "AF"),
        ("afg", "AF"),
        ("AUL", "AU"),
    ],
    ids=["equal", "case_insensitive", "custom_code"],
)
def test_country_code_map_get_iso2_code_returns_expected_iso2(country_code_maps, ca_code, expected):
    result = CountryCodeMap.objects.get_iso2_code(ca_code)

    assert result == expected


@pytest.mark.parametrize(
    ("ca_code", "expected"),
    [
        ("AFG", "AFG"),
        ("afg", "AFG"),
        ("AUL", "AUS"),
    ],
    ids=["equal", "case_insensitive", "custom_code"],
)
def test_country_code_map_get_iso3_code_returns_expected_iso3(country_code_maps, ca_code, expected):
    result = CountryCodeMap.objects.get_iso3_code(ca_code)

    assert result == expected


def test_country_code_map_uses_cache_for_multiple_queries(country_code_maps, django_assert_num_queries):
    CountryCodeMap.objects._cache = {2: {}, 3: {}, "ca2": {}, "ca3": {}}

    with django_assert_num_queries(1):
        assert CountryCodeMap.objects.get_code("AFG") == "AFG"
        assert CountryCodeMap.objects.get_code("afg") == "AFG"
        assert CountryCodeMap.objects.get_code("af") == "AFG"
        assert CountryCodeMap.objects.get_code("AUS") == "AUL"
        assert CountryCodeMap.objects.get_iso3_code("AFG") == "AFG"
        assert CountryCodeMap.objects.get_iso3_code("afg") == "AFG"
        assert CountryCodeMap.objects.get_iso3_code("AUL") == "AUS"
        assert CountryCodeMap.objects.get_iso2_code("AFg") == "AF"
