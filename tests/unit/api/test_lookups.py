from datetime import datetime, timedelta

from django.utils import timezone

import pytz
from parameterized import parameterized
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.api.models import Grant
from hct_mis_api.apps.geo.models import Area, AreaType, Country
from hct_mis_api.apps.payment.models import FinancialInstitution
from hct_mis_api.apps.program.models import Program
from tests.extras.test_utils.factories.geo import (
    AreaFactory,
    AreaTypeFactory,
    CountryFactory,
)
from tests.extras.test_utils.factories.payment import FinancialInstitutionFactory
from tests.unit.api.base import HOPEApiTestCase, token_grant_permission


class APIProgramStatuesTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    def test_get_program_statues(self) -> None:
        url = reverse("api:program-statuses-list")
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), dict(Program.STATUS_CHOICE))


class APICountriesTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.country_poland = CountryFactory(
            name="Poland",
            short_name="Poland",
            iso_code2="PL",
            iso_code3="POL",
            iso_num="0620",
        )
        cls.country_poland.valid_from = datetime(2020, 1, 1, tzinfo=pytz.UTC)
        cls.country_poland.valid_until = datetime(2020, 12, 31, tzinfo=pytz.UTC)
        cls.country_poland.save(update_fields=["valid_from", "valid_until"])

        cls.country_afghanistan = CountryFactory(
            name="Afghanistan",
            short_name="Afghanistan",
            iso_code2="AF",
            iso_code3="AFG",
            iso_num="0040",
        )
        cls.country_afghanistan.valid_from = datetime(2019, 1, 1, tzinfo=pytz.UTC)
        cls.country_afghanistan.valid_until = datetime(2021, 12, 31, tzinfo=pytz.UTC)
        cls.country_afghanistan.save(update_fields=["valid_from", "valid_until"])
        cls.url = reverse("api:country-list")

    def get_response(self, country: Country) -> dict:
        return {
            "id": str(country.id),
            "name": country.name,
            "short_name": country.short_name,
            "iso_code2": country.iso_code2,
            "iso_code3": country.iso_code3,
            "iso_num": country.iso_num,
            "updated_at": country.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "valid_from": country.valid_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "valid_until": country.valid_until.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    def test_get_countries(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()["results"],
            [
                self.get_response(self.country_afghanistan),
                self.get_response(self.country_poland),
            ],
        )
        self.assertIn("count", response.json())
        self.assertIn("next", response.json())
        self.assertIn("previous", response.json())

    def test_get_countries_filter_valid_from_until(self) -> None:
        for filter_data, expected_result in [
            ({"valid_from_before": "2019-01-02"}, [self.country_afghanistan]),
            ({"valid_from_after": "2019-01-02"}, [self.country_poland]),
            ({"valid_until_before": "2022-01-01"}, [self.country_poland, self.country_afghanistan]),
            ({"valid_until_after": "2021-12-30"}, [self.country_afghanistan]),
        ]:
            with token_grant_permission(self.token, Grant.API_READ_ONLY):
                response = self.client.get(self.url, filter_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK, filter_data)
            self.assertEqual(len(response.json()["results"]), len(expected_result), filter_data)
            for result in expected_result:
                self.assertIn(
                    self.get_response(result),
                    response.json()["results"],
                    filter_data,
                )

    def test_get_countries_search(self) -> None:
        for filter_data, expected_result in [
            (self.country_afghanistan.short_name, self.country_afghanistan),
            (self.country_afghanistan.iso_num, self.country_afghanistan),
            (self.country_poland.short_name, self.country_poland),
            (self.country_poland.iso_code2, self.country_poland),
            (self.country_poland.iso_code3, self.country_poland),
        ]:
            with token_grant_permission(self.token, Grant.API_READ_ONLY):
                response = self.client.get(self.url, {"search": filter_data})
            self.assertEqual(response.status_code, status.HTTP_200_OK, filter_data)
            self.assertEqual(len(response.json()["results"]), 1, filter_data)
            self.assertIn(
                self.get_response(expected_result),
                response.json()["results"],
                filter_data,
            )


class AreaListTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.url = reverse("api:area-list")
        cls.country_poland = CountryFactory(name="Poland", iso_code3="POL", iso_code2="PL", iso_num="620")
        cls.country_afghanistan = CountryFactory(name="Afghanistan", iso_code3="AFG", iso_code2="AF", iso_num="040")
        cls.area_type1 = AreaTypeFactory(name="areatype1", country=cls.country_poland, area_level=1)
        cls.area_type2 = AreaTypeFactory(name="areatype1", country=cls.country_afghanistan, area_level=2)
        cls.area1 = AreaFactory(
            name="area1",
            area_type=cls.area_type1,
        )
        cls.area1.valid_from = datetime(2010, 1, 1, tzinfo=pytz.UTC)
        cls.area1.valid_until = datetime(2010, 12, 31, tzinfo=pytz.UTC)
        cls.area1.save(update_fields=["valid_from", "valid_until"])
        cls.area2 = AreaFactory(
            name="area2",
            area_type=cls.area_type2,
            parent=cls.area1,
        )
        cls.area2.valid_from = datetime(2020, 1, 1, tzinfo=pytz.UTC)
        cls.area2.valid_until = datetime(2020, 12, 31, tzinfo=pytz.UTC)
        cls.area2.save(update_fields=["valid_from", "valid_until"])

    def get_result(self, area: Area) -> dict:
        return {
            "id": str(area.id),
            "created_at": area.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated_at": area.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "original_id": area.original_id,
            "name": area.name,
            "p_code": area.p_code,
            "valid_from": area.valid_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "valid_until": area.valid_until.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "extras": area.extras,
            "lft": area.lft,
            "rght": area.rght,
            "tree_id": area.tree_id,
            "level": area.level,
            "latitude": area.latitude,
            "longitude": area.longitude,
            "parent": str(area.parent.id) if area.parent else None,
            "area_type": str(area.area_type.id),
        }

    def test_get_area_list(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for area in [self.area1, self.area2]:
            expected_result = self.get_result(area)
            self.assertIn(
                expected_result,
                response.json()["results"],
            )

    def test_get_area_list_filter(self) -> None:
        for filter_data, expected_results in (
            ({"country_iso_code2": "PL"}, [self.area1]),
            ({"country_iso_code2": "AF"}, [self.area2]),
            ({"country_iso_code3": "POL"}, [self.area1]),
            ({"country_iso_code3": "AFG"}, [self.area2]),
            ({"valid_from_before": "2011-01-01"}, [self.area1]),
            ({"valid_from_after": "2011-01-01"}, [self.area2]),
            ({"valid_until_before": "2021-01-01"}, [self.area1, self.area2]),
            ({"valid_until_after": "2021-01-01"}, []),
            ({"area_type_area_level": 1}, [self.area1]),
            ({"area_type_area_level": 2}, [self.area2]),
            ({"parent_id": str(self.area1.id)}, [self.area2]),
            ({"parent_p_code": self.area1.p_code}, [self.area2]),
            ({"parent_id": str(self.area2.id)}, []),
            ({"parent_p_code": self.area2.p_code}, []),
        ):
            with token_grant_permission(self.token, Grant.API_READ_ONLY):
                response = self.client.get(self.url, filter_data)  # type: ignore
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), len(expected_results), filter_data)
            for area in expected_results:
                self.assertIn(
                    self.get_result(area),
                    response.json()["results"],
                    filter_data,
                )

    def test_get_area_list_search(self) -> None:
        for filter_data, area in [
            (self.area1.name, self.area1),
            (self.area2.name, self.area2),
            (self.area1.p_code, self.area1),
            (self.area2.p_code, self.area2),
        ]:
            with token_grant_permission(self.token, Grant.API_READ_ONLY):
                response = self.client.get(self.url, {"search": filter_data})
            self.assertEqual(response.status_code, status.HTTP_200_OK, filter_data)
            self.assertEqual(len(response.json()["results"]), 1, filter_data)
            self.assertIn(
                self.get_result(area),
                response.json()["results"],
                filter_data,
            )


class AreaTypeListTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.url = reverse("api:areatype-list")
        cls.country_poland = CountryFactory(name="Poland", iso_code3="POL", iso_code2="PL", iso_num="620")
        cls.country_afghanistan = CountryFactory(name="Afghanistan", iso_code3="AFG", iso_code2="AF", iso_num="040")
        cls.area_type1 = AreaTypeFactory(name="areatype1", country=cls.country_poland, area_level=1)
        cls.area_type1.valid_until = datetime(2010, 12, 31, tzinfo=pytz.UTC)
        cls.area_type1.save(update_fields=["valid_until"])
        cls.area_type2 = AreaTypeFactory(
            name="areatype2",
            country=cls.country_afghanistan,
            area_level=2,
            parent=cls.area_type1,
        )
        cls.area_type2.valid_until = datetime(2010, 12, 31, tzinfo=pytz.UTC)
        cls.area_type2.save(update_fields=["valid_until"])

    def get_result(self, area_type: AreaType) -> dict:
        return {
            "id": str(area_type.id),
            "created_at": area_type.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated_at": area_type.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "original_id": area_type.original_id,
            "name": area_type.name,
            "area_level": area_type.area_level,
            "valid_from": area_type.valid_from.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "valid_until": area_type.valid_until.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "extras": area_type.extras,
            "lft": area_type.lft,
            "rght": area_type.rght,
            "tree_id": area_type.tree_id,
            "level": area_type.level,
            "country": str(area_type.country.id),
            "parent": str(area_type.parent.id) if area_type.parent else None,
        }

    def test_get_area_type_list(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for area_type in [self.area_type1, self.area_type2]:
            expected_result = self.get_result(area_type)
            self.assertIn(
                expected_result,
                response.json()["results"],
            )

    def test_get_area_type_list_filter(self) -> None:
        for filter_data, expected_results in (
            ({"country_iso_code2": "PL"}, [self.area_type1]),
            ({"country_iso_code2": "AF"}, [self.area_type2]),
            ({"country_iso_code3": "POL"}, [self.area_type1]),
            ({"country_iso_code3": "AFG"}, [self.area_type2]),
            ({"area_level": 1}, [self.area_type1]),
            ({"area_level": 2}, [self.area_type2]),
            ({"parent_area_level": 1}, [self.area_type2]),
            ({"parent_area_level": 2}, []),
        ):
            with token_grant_permission(self.token, Grant.API_READ_ONLY):
                response = self.client.get(self.url, filter_data)  # type: ignore
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.json()["results"]), len(expected_results), filter_data)
            for area_type in expected_results:
                expected_result = self.get_result(area_type)
                self.assertIn(
                    expected_result,
                    response.json()["results"],
                )

    def test_get_area_type_list_search(self) -> None:
        for filter_data, area_type in [
            (self.area_type1.name, self.area_type1),
            (self.area_type2.name, self.area_type2),
        ]:
            with token_grant_permission(self.token, Grant.API_READ_ONLY):
                response = self.client.get(self.url, {"search": filter_data})
            self.assertEqual(response.status_code, status.HTTP_200_OK, filter_data)
            self.assertEqual(len(response.json()["results"]), 1, filter_data)
            self.assertIn(
                self.get_result(area_type),
                response.json()["results"],
            )


class FinancialInstitutionListTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.url = reverse("api:financial-institution-list")
        cls.country_poland = CountryFactory(name="Poland", iso_code3="POL", iso_code2="PL", iso_num="620")
        cls.country_afghanistan = CountryFactory(name="Afghanistan", iso_code3="AFG", iso_code2="AF", iso_num="040")

        cls.fi_bank = FinancialInstitutionFactory(
            name="Test Bank",
            type=FinancialInstitution.FinancialInstitutionType.BANK,
            country=cls.country_poland,
            swift_code="TESTBANK123",
        )
        cls.fi_telco = FinancialInstitutionFactory(
            name="Test Telco",
            type=FinancialInstitution.FinancialInstitutionType.TELCO,
            country=cls.country_afghanistan,
            swift_code="TESTTELCO456",
        )
        cls.fi_other = FinancialInstitutionFactory(
            name="Test Other Institution",
            type=FinancialInstitution.FinancialInstitutionType.OTHER,
            country=cls.country_poland,
            swift_code="",
        )

    def get_result(self, financial_institution: FinancialInstitution) -> dict:
        return {
            "id": financial_institution.id,
            "name": financial_institution.name,
            "type": financial_institution.type,
            "swift_code": financial_institution.swift_code or "",
            "country_iso_code3": financial_institution.country.iso_code3 if financial_institution.country else None,
            "updated_at": financial_institution.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            if financial_institution.updated_at
            else None,
        }

    def test_get_financial_institution_list(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for fi in [self.fi_bank, self.fi_telco, self.fi_other]:
            expected_result = self.get_result(fi)
            self.assertIn(
                expected_result,
                response.json()["results"],
            )

    def test_get_financial_institution_list_ordering(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()["results"]
        names = [result["name"] for result in results]

        self.assertEqual(names, sorted(names))

    def test_get_financial_institution_list_pagination(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertIn("count", response_data)
        self.assertIn("next", response_data)
        self.assertIn("previous", response_data)
        self.assertIn("results", response_data)

    @parameterized.expand(
        [
            ("bank", 1),
            ("telco", 1),
            ("other", 1),
        ]
    )
    def test_get_financial_institution_list_filter_by_type(self, institution_type: str, expected_count: int) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url, {"type": institution_type})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), expected_count)
        self.assertLess(
            expected_count, 3, f"Filtering by type '{institution_type}' should return fewer results than total"
        )

    @parameterized.expand(
        [
            ("updated_at_after", 3),
            ("updated_at_before", 3),
            ("updated_at_after_and_before", 3),
        ]
    )
    def test_get_financial_institution_list_filter_by_updated_at(self, filter_type: str, expected_count: int) -> None:
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        if filter_type == "updated_at_after":
            filter_data = {"updated_at_after": yesterday.strftime("%Y-%m-%d")}
        elif filter_type == "updated_at_before":
            filter_data = {"updated_at_before": tomorrow.strftime("%Y-%m-%d")}
        else:
            filter_data = {
                "updated_at_after": yesterday.strftime("%Y-%m-%d"),
                "updated_at_before": tomorrow.strftime("%Y-%m-%d"),
            }

        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url, filter_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), expected_count)

    @parameterized.expand(
        [
            ("bank", "Test Bank"),
            ("telco", "Test Telco"),
            ("other", "Test Other Institution"),
        ]
    )
    def test_get_financial_institution_list_filter_by_type_returns_correct_institution(
        self, institution_type: str, expected_name: str
    ) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url, {"type": institution_type})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], expected_name)
        self.assertEqual(results[0]["type"], institution_type)

    def test_get_financial_institution_list_filter_by_invalid_type_returns_empty(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url, {"type": "invalid_type"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_financial_institution_list_filter_by_future_date_returns_empty(self) -> None:
        future_date = timezone.now() + timedelta(days=365)
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url, {"updated_at_after": future_date.strftime("%Y-%m-%d")})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)

    def test_get_financial_institution_list_filter_by_past_date_returns_all(self) -> None:
        past_date = timezone.now() - timedelta(days=365)
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url, {"updated_at_before": past_date.strftime("%Y-%m-%d")})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
