from django.core.management import call_command
from django.test import TestCase
from parameterized import parameterized

from hope.apps.core.models import CountryCodeMap


class TestCountryCodeMap(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadcountries")
        call_command("loadcountrycodes")

    @parameterized.expand(
        [
            ("equal", "AFG", "AFG"),
            ("case_insensitive", "afg", "AFG"),
            ("alpha2", "af", "AFG"),
            ("custom_code", "AUS", "AUL"),
        ]
    )
    def test_get_code(self, helper: str, iso_code: str, expected: str) -> None:
        assert CountryCodeMap.objects.get_code(iso_code) == expected

    @parameterized.expand(
        [
            ("equal", "AFG", "AF"),
            ("case_insensitive", "afg", "AF"),
            ("custom_code", "AUL", "AU"),
        ]
    )
    def test_get_iso2_code_from_ca_code(self, helper: str, ca_code: str, expected: str) -> None:
        assert CountryCodeMap.objects.get_iso2_code(ca_code) == expected

    @parameterized.expand(
        [
            ("equal", "AFG", "AFG"),
            ("case_insensitive", "afg", "AFG"),
            ("custom_code", "AUL", "AUS"),
        ]
    )
    def test_get_iso3_code_from_ca_code(self, helper: str, ca_code: str, expected: str) -> None:
        assert CountryCodeMap.objects.get_iso3_code(ca_code) == expected

    def test_cache(self) -> None:
        CountryCodeMap.objects._cache = {2: {}, 3: {}, "ca2": {}, "ca3": {}}
        with self.assertNumQueries(1):
            assert CountryCodeMap.objects.get_code("AFG") == "AFG"
            assert CountryCodeMap.objects.get_code("afg") == "AFG"
            assert CountryCodeMap.objects.get_code("af") == "AFG"
            assert CountryCodeMap.objects.get_code("AUS") == "AUL"
            assert CountryCodeMap.objects.get_iso3_code("AFG") == "AFG"
            assert CountryCodeMap.objects.get_iso3_code("afg") == "AFG"
            assert CountryCodeMap.objects.get_iso3_code("AUL") == "AUS"
            assert CountryCodeMap.objects.get_iso2_code("AFg") == "AF"
