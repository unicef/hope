from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.geo.fixtures import CountryFactory
from hct_mis_api.apps.program.models import Program
from tests.unit.api.base import HOPEApiTestCase


class APIProgramStatuesTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    def test_get_program_statues(self) -> None:
        url = reverse("api:program-statuses-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), dict(Program.STATUS_CHOICE))


class APICountriesTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    def test_get_countries(self) -> None:
        country_afghanistan = CountryFactory()
        country_poland = CountryFactory(
            name="Poland",
            short_name="Poland",
            iso_code2="PL",
            iso_code3="POL",
            iso_num="0620",
        )
        url = reverse("api:country-list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "name": country_afghanistan.name,
                "short_name": country_afghanistan.short_name,
                "iso_code2": country_afghanistan.iso_code2,
                "iso_code3": country_afghanistan.iso_code3,
                "iso_num": country_afghanistan.iso_num,
            },
            {
                "name": country_poland.name,
                "short_name": country_poland.short_name,
                "iso_code2": country_poland.iso_code2,
                "iso_code3": country_poland.iso_code3,
                "iso_num": country_poland.iso_num,
            },
        ]
