from django.core.management import call_command
from django.test import TestCase
from parameterized import parameterized

from hct_mis_api.apps.core.models import CountryCodeMap


class TestCountryCodeMap(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("loadcountrycodes")

    @parameterized.expand(
        [
            ("equal", "AFG", "AFG"),
            ("case_insensitive", "afg", "AFG"),
            ("alpha2", "af", "AFG"),
            ("custom_code", "AUS", "AUL"),
        ]
    )
    def test_get_code(self, _, iso_code, expected):
        self.assertEqual(CountryCodeMap.objects.get_code(iso_code), expected)

    def test_cache(self):
        with self.assertNumQueries(1):
            self.assertEqual(CountryCodeMap.objects.get_code("AFG"), "AFG")
            self.assertEqual(CountryCodeMap.objects.get_code("afg"), "AFG")
            self.assertEqual(CountryCodeMap.objects.get_code("af"), "AFG")
            self.assertEqual(CountryCodeMap.objects.get_code("AUS"), "AUL")
