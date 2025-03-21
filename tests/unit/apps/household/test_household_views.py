import json
<<<<<<< HEAD
from typing import Any, Optional, Tuple
=======
from typing import Any, Dict, Optional, Tuple
>>>>>>> e509e33f3be98f6d786746662626b55f342b0433

from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

import pytest
from constance.test import override_config
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan, create_ukraine
from hct_mis_api.apps.core.utils import (
    encode_id_base64_required,
    resolve_flex_fields_choices_to_string,
)
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    DocumentTypeFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import DUPLICATE, HOST, REFUGEE, Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index
from hct_mis_api.apps.utils.models import MergeStatusModel

pytestmark = pytest.mark.django_db


def get_encoded_household_id(household: Household) -> str:
    return encode_id_base64_required(household.id, "Household")


class TestHouseholdList:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        different_program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.list_url = reverse(
            "api:households:households-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program.slug},
        )
        self.count_url = reverse(
            "api:households:households-count",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program.slug},
        )

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.country = CountryFactory()
        admin_type_1 = AreaTypeFactory(country=self.country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=self.country, area_level=2, parent=admin_type_1)

        self.area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
        self.area2 = AreaFactory(parent=self.area1, p_code="AF0101", area_type=admin_type_2)

        self.household1 = self._create_household(self.program)
        self.household2 = self._create_household(self.program)
        self.household_from_different_program = self._create_household(different_program)

    def _create_household(self, program: Program) -> Household:
        household, _ = create_household_and_individuals(
            household_data={
                "admin1": self.area1,
                "admin2": self.area2,
                "country_origin": self.country,
                "program": program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        return household

    @pytest.mark.parametrize(
        "permissions",
        [
            (Permissions.RDI_VIEW_DETAILS,),
            (Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,),
        ],
    )
    def test_household_list_with_permissions(
        self,
        permissions: list,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        response_results = response.json()["results"]
        assert len(response_results) == 2

        response_count = self.api_client.get(self.count_url)
        assert response_count.status_code == status.HTTP_200_OK
        assert response_count.json()["count"] == 2

        response_ids = [result["id"] for result in response_results]
        assert get_encoded_household_id(self.household1) in response_ids

        for i, household in enumerate([self.household1, self.household2]):
            household_result_first = response_results[i]
            assert household_result_first["id"] == encode_id_base64_required(household.id, "Household")
            assert household_result_first["unicef_id"] == household.unicef_id
            assert household_result_first["head_of_household"] == household.head_of_household.full_name
            assert household_result_first["admin1"] == household.admin1.name
            assert household_result_first["admin2"] == household.admin2.name
            assert household_result_first["program"] == household.program.name
            assert household_result_first["status"] == household.status
            assert household_result_first["size"] == household.size
            assert household_result_first["residence_status"] == household.residence_status
            assert household_result_first["total_cash_received"] == household.total_cash_received
            assert household_result_first["total_cash_received_usd"] == household.total_cash_received_usd
            assert (
                household_result_first["last_registration_date"]
                == f"{household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}"
            )

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_household_count(
        self,
        permissions: list,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.count_url)
        assert response.status_code == expected_status

        if expected_status == status.HTTP_200_OK:
            assert response.json()["count"] == 2

    @pytest.mark.parametrize(
        "permissions",
        [
            [],
            (Permissions.PROGRAMME_ACTIVATE,),
        ],
    )
    def test_household_list_without_permissions(
        self, permissions: list, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(self.list_url)
        assert response.status_code == 403

    def test_household_list_on_draft_program(self, create_user_role_with_permissions: Any) -> None:
        program = ProgramFactory(business_area=self.afghanistan, status=Program.DRAFT)
        list_url = reverse(
            "api:households:households-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": program.slug},
        )
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.RDI_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=program,
        )
        for _ in range(2):
            self._create_household(program)

        response = self.api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

    def test_household_list_with_admin_area_limits(
        self, create_user_role_with_permissions: Any, set_admin_area_limits_in_program: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.RDI_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )
        set_admin_area_limits_in_program(self.partner, self.program, [self.area1])

        household_without_areas, _ = create_household_and_individuals(
            household_data={
                "country_origin": self.country,
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        area_different = AreaFactory(parent=None, p_code="AF05", area_type=self.area1.area_type)
        household_different_areas = self._create_household(self.program)
        household_different_areas.admin1 = area_different
        household_different_areas.admin2 = area_different
        household_different_areas.save()

        response = self.api_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 3

        response_ids = [result["id"] for result in response_results]

        assert get_encoded_household_id(self.household1) in response_ids
        assert get_encoded_household_id(self.household2) in response_ids
        assert get_encoded_household_id(household_without_areas) in response_ids

        assert get_encoded_household_id(household_different_areas) not in response_ids

    def test_household_list_caching(
        self, create_user_role_with_permissions: Any, set_admin_area_limits_in_program: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.RDI_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )

        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(response.json()["results"]) == 2
            assert len(ctx.captured_queries) == 17

        # no change - use cache
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_second_call = response.headers["etag"]
            assert etag == etag_second_call
            assert len(ctx.captured_queries) == 10

        self.household1.children_count = 100
        self.household1.save()
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_third_call = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert etag_third_call not in [etag, etag_second_call]
            # 4 queries are saved because of cached permissions calculations
            assert len(ctx.captured_queries) == 12

        set_admin_area_limits_in_program(self.partner, self.program, [self.area1])
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_changed_areas = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert etag_changed_areas not in [etag, etag_second_call, etag_third_call]
            assert len(ctx.captured_queries) == 12

        self.household2.delete()
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_fourth_call = response.headers["etag"]
            assert len(response.json()["results"]) == 1
            assert etag_fourth_call not in [etag, etag_second_call, etag_third_call, etag_changed_areas]
            assert len(ctx.captured_queries) == 12

        # no change - use cache
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_fifth_call = response.headers["etag"]
            assert etag_fifth_call == etag_fourth_call
            assert len(ctx.captured_queries) == 10


class TestHouseholdDetail:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.detail_url_name = "api:households:households-detail"

        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.country = CountryFactory()
        admin_type_1 = AreaTypeFactory(country=self.country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=self.country, area_level=2, parent=admin_type_1)

        self.area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
        self.area2 = AreaFactory(parent=self.area1, p_code="AF0101", area_type=admin_type_2)
        self.area3 = AreaFactory(parent=self.area2, p_code="AF010101", area_type=admin_type_2)
        self.area4 = AreaFactory(parent=self.area3, p_code="AF01010101", area_type=admin_type_2)

        self.registration_data_import = RegistrationDataImportFactory(
            imported_by=self.user, business_area=self.afghanistan, program=self.program
        )
        self.geopoint = [51.107883, 17.038538]
        self.household, self.individuals = create_household_and_individuals(
            household_data={
                "admin_area": self.area1,
                "admin1": self.area1,
                "admin2": self.area2,
                "admin3": self.area3,
                "admin4": self.area4,
                "country": self.country,
                "country_origin": self.country,
                "program": self.program,
                "business_area": self.afghanistan,
                "registration_data_import": self.registration_data_import,
                "geopoint": Point(self.geopoint),
            },
            individuals_data=[{}, {}],
        )

        duplicated_individual = self.individuals[1]
        duplicated_individual.deduplication_golden_record_status = DUPLICATE
        duplicated_individual.duplicate = True
        duplicated_individual.save()

    @pytest.mark.parametrize(
        "permissions",
        [
            (Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS,),
            (Permissions.RDI_VIEW_DETAILS,),
        ],
    )
    def test_household_detail_with_permissions(self, permissions: list, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )
        encoded_household_id = encode_id_base64_required(self.household.id, "Household")
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "program_slug": self.program.slug,
                    "pk": encoded_household_id,
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data["id"] == encoded_household_id
        assert data["unicef_id"] == self.household.unicef_id
        assert data["head_of_household"] == {
            "id": encode_id_base64_required(self.individuals[0].id, "Individual"),
            "full_name": self.individuals[0].full_name,
        }
        assert data["admin1"] == self.household.admin1.name
        assert data["admin2"] == self.household.admin2.name
        assert data["admin3"] == self.household.admin3.name
        assert data["admin4"] == self.household.admin4.name
        assert data["program"] == self.household.program.name
        assert data["country"] == self.household.country.name
        assert data["country_origin"] == self.household.country_origin.name
        assert data["status"] == self.household.status
        assert data["total_cash_received"] == self.household.total_cash_received
        assert data["total_cash_received_usd"] == self.household.total_cash_received_usd
        assert data["has_duplicates"] is True
        assert data["registration_data_import"] == {
            "name": self.registration_data_import.name,
            "status": self.registration_data_import.status,
            "import_date": f"{self.registration_data_import.import_date:%Y-%m-%dT%H:%M:%S.%fZ}",
            "number_of_individuals": self.registration_data_import.number_of_individuals,
            "number_of_households": self.registration_data_import.number_of_households,
            "imported_by": {
                "first_name": self.registration_data_import.imported_by.first_name,
                "last_name": self.registration_data_import.imported_by.last_name,
                "email": self.registration_data_import.imported_by.email,
                "username": self.registration_data_import.imported_by.username,
            },
            "data_source": self.registration_data_import.data_source,
        }
        assert data["flex_fields"] == resolve_flex_fields_choices_to_string(self.household)
        assert data["admin_area_title"] == f"{self.household.admin_area.name} - {self.household.admin_area.p_code}"
        assert data["active_individuals_count"] == 1
        assert data["geopoint"] == (self.geopoint[0], self.geopoint[1])
        assert data["import_id"] == self.household.unicef_id
        assert data["admin_url"] == self.household.admin_url
        assert data["male_children_count"] == self.household.male_children_count
        assert data["female_children_count"] == self.household.female_children_count
        assert data["children_disabled_count"] == self.household.children_disabled_count
        assert data["currency"] == self.household.currency
        assert data["first_registration_date"] == f"{self.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}"
        assert data["last_registration_date"] == f"{self.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}"
        assert data["unhcr_id"] == self.household.unhcr_id
        assert data["village"] == self.household.village
        assert data["address"] == self.household.address
        assert data["zip_code"] == self.household.zip_code
        assert data["female_age_group_0_5_count"] == self.household.female_age_group_0_5_count
        assert data["female_age_group_6_11_count"] == self.household.female_age_group_6_11_count
        assert data["female_age_group_12_17_count"] == self.household.female_age_group_12_17_count
        assert data["female_age_group_18_59_count"] == self.household.female_age_group_18_59_count
        assert data["female_age_group_60_count"] == self.household.female_age_group_60_count
        assert data["pregnant_count"] == self.household.pregnant_count
        assert data["male_age_group_0_5_count"] == self.household.male_age_group_0_5_count
        assert data["male_age_group_6_11_count"] == self.household.male_age_group_6_11_count
        assert data["male_age_group_12_17_count"] == self.household.male_age_group_12_17_count
        assert data["male_age_group_18_59_count"] == self.household.male_age_group_18_59_count
        assert data["male_age_group_60_count"] == self.household.male_age_group_60_count
        assert data["female_age_group_0_5_disabled_count"] == self.household.female_age_group_0_5_disabled_count
        assert data["female_age_group_6_11_disabled_count"] == self.household.female_age_group_6_11_disabled_count
        assert data["female_age_group_12_17_disabled_count"] == self.household.female_age_group_12_17_disabled_count
        assert data["female_age_group_18_59_disabled_count"] == self.household.female_age_group_18_59_disabled_count
        assert data["female_age_group_60_disabled_count"] == self.household.female_age_group_60_disabled_count
        assert data["male_age_group_0_5_disabled_count"] == self.household.male_age_group_0_5_disabled_count
        assert data["male_age_group_6_11_disabled_count"] == self.household.male_age_group_6_11_disabled_count
        assert data["male_age_group_12_17_disabled_count"] == self.household.male_age_group_12_17_disabled_count
        assert data["male_age_group_18_59_disabled_count"] == self.household.male_age_group_18_59_disabled_count
        assert data["male_age_group_60_disabled_count"] == self.household.male_age_group_60_disabled_count
        assert data["start"] == f"{self.household.start:%Y-%m-%dT%H:%M:%SZ}"
        assert data["deviceid"] == self.household.deviceid
        assert data["fchild_hoh"] == self.household.fchild_hoh
        assert data["child_hoh"] == self.household.child_hoh
        assert data["returnee"] == self.household.returnee
        assert data["size"] == self.household.size
        assert data["residence_status"] == self.household.residence_status
        assert data["program_registration_id"] == self.household.program_registration_id

    @pytest.mark.parametrize(
        "permissions",
        [
            [],
            (Permissions.PROGRAMME_ACTIVATE,),
        ],
    )
    def test_household_detail_without_permissions(
        self, permissions: list, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )
        encoded_household_id = encode_id_base64_required(self.household.id, "Household")
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "program_slug": self.program.slug,
                    "pk": encoded_household_id,
                },
            )
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_household_detail_with_permissions_in_different_program(
        self, create_user_role_with_permissions: Any
    ) -> None:
        program_other = ProgramFactory(name="Program Other", business_area=self.afghanistan, status=Program.ACTIVE)
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
            business_area=self.afghanistan,
            program=program_other,
        )
        encoded_household_id = encode_id_base64_required(self.household.id, "Household")
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "program_slug": self.program.slug,
                    "pk": encoded_household_id,
                },
            )
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestHouseholdGlobalViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.global_url_name = "api:households:households-global-list"
        self.global_count_url = "api:households:households-global-count"
        self.afghanistan = create_afghanistan()
        self.ukraine = create_ukraine()
        self.program_afghanistan1 = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="program afghanistan 1",
        )
        self.program_afghanistan2 = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="program afghanistan 2",
        )
        self.program_ukraine = ProgramFactory(business_area=self.ukraine, status=Program.ACTIVE)

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.country = CountryFactory()
        self.admin_type_1 = AreaTypeFactory(country=self.country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=self.country, area_level=2, parent=self.admin_type_1)
        self.area1 = AreaFactory(parent=None, p_code="AF01", area_type=self.admin_type_1)
        self.area2 = AreaFactory(parent=self.area1, p_code="AF0101", area_type=admin_type_2)
        self.area3 = AreaFactory(parent=self.area2, p_code="AF010101", area_type=admin_type_2)
        self.area4 = AreaFactory(parent=self.area3, p_code="AF01010101", area_type=admin_type_2)

        self.household_afghanistan1, _ = create_household_and_individuals(
            household_data={
                "admin_area": self.area1,
                "admin1": self.area1,
                "admin2": self.area2,
                "admin3": self.area3,
                "admin4": self.area4,
                "country": self.country,
                "country_origin": self.country,
                "program": self.program_afghanistan1,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        self.household_afghanistan2, _ = create_household_and_individuals(
            household_data={
                "admin_area": self.area1,
                "admin1": self.area1,
                "admin2": self.area2,
                "admin3": self.area3,
                "admin4": self.area4,
                "country": self.country,
                "country_origin": self.country,
                "program": self.program_afghanistan2,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.household_ukraine, _ = create_household_and_individuals(
            household_data={
                "admin_area": self.area1,
                "admin1": self.area1,
                "admin2": self.area2,
                "admin3": self.area3,
                "admin4": self.area4,
                "country": self.country,
                "country_origin": self.country,
                "program": self.program_ukraine,
                "business_area": self.ukraine,
            },
            individuals_data=[{}, {}],
        )

    @pytest.mark.parametrize(
        "permissions",
        [
            (Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,),
            (Permissions.RDI_VIEW_DETAILS,),
        ],
    )
    def test_household_global_list_with_permissions(
        self, permissions: list, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )

        response = self.api_client.get(
            reverse(self.global_url_name, kwargs={"business_area_slug": self.afghanistan.slug})
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 2

        response_count = self.api_client.get(
            reverse(self.global_count_url, kwargs={"business_area_slug": self.afghanistan.slug})
        )
        assert response_count.status_code == status.HTTP_200_OK
        assert response_count.json()["count"] == 2

        result_ids = [result["id"] for result in response_results]
        assert encode_id_base64_required(self.household_afghanistan1.id, "Household") in result_ids
        assert encode_id_base64_required(self.household_afghanistan2.id, "Household") in result_ids
        assert encode_id_base64_required(self.household_ukraine.id, "Household") not in result_ids

        for i, household in enumerate([self.household_afghanistan1, self.household_afghanistan2]):
            household_result_first = response_results[i]
            assert household_result_first["id"] == encode_id_base64_required(household.id, "Household")
            assert household_result_first["unicef_id"] == household.unicef_id
            assert household_result_first["head_of_household"] == household.head_of_household.full_name
            assert household_result_first["admin1"] == household.admin1.name
            assert household_result_first["admin2"] == household.admin2.name
            assert household_result_first["program"] == household.program.name
            assert household_result_first["status"] == household.status
            assert household_result_first["size"] == household.size
            assert household_result_first["residence_status"] == household.residence_status
            assert household_result_first["total_cash_received"] == household.total_cash_received
            assert household_result_first["total_cash_received_usd"] == household.total_cash_received_usd
            assert (
                household_result_first["last_registration_date"]
                == f"{household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}"
            )

    def test_household_global_list_with_permissions_in_one_program(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
            business_area=self.afghanistan,
            program=self.program_afghanistan1,
        )

        response = self.api_client.get(
            reverse(self.global_url_name, kwargs={"business_area_slug": self.afghanistan.slug})
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 1

        result_ids = [result["id"] for result in response_results]
        assert encode_id_base64_required(self.household_afghanistan1.id, "Household") in result_ids
        assert encode_id_base64_required(self.household_afghanistan2.id, "Household") not in result_ids
        assert encode_id_base64_required(self.household_ukraine.id, "Household") not in result_ids

    @pytest.mark.parametrize(
        "permissions",
        [
            [],
            (Permissions.PROGRAMME_ACTIVATE,),
        ],
    )
    def test_household_global_list_without_permissions(
        self, permissions: list, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )

        response = self.api_client.get(
            reverse(self.global_url_name, kwargs={"business_area_slug": self.afghanistan.slug})
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_household_global_list_area_limits(
        self, create_user_role_with_permissions: Any, set_admin_area_limits_in_program: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        set_admin_area_limits_in_program(self.partner, self.program_afghanistan2, [self.area1, self.area2])
        household_afghanistan_without_areas, _ = create_household_and_individuals(
            household_data={
                "country": self.country,
                "country_origin": self.country,
                "program": self.program_afghanistan2,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        area_different = AreaFactory(parent=None, p_code="AF05", area_type=self.admin_type_1)
        household_afghanistan_different_areas, _ = create_household_and_individuals(
            household_data={
                "admin_area": area_different,
                "admin1": area_different,
                "admin2": area_different,
                "admin3": area_different,
                "admin4": area_different,
                "country": self.country,
                "country_origin": self.country,
                "program": self.program_afghanistan2,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        response = self.api_client.get(
            reverse(self.global_url_name, kwargs={"business_area_slug": self.afghanistan.slug})
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 3

        result_ids = [result["id"] for result in response_results]
        assert get_encoded_household_id(self.household_afghanistan1) in result_ids
        assert get_encoded_household_id(self.household_afghanistan2) in result_ids
        assert get_encoded_household_id(household_afghanistan_without_areas) in result_ids
        assert get_encoded_household_id(self.household_ukraine) not in result_ids
        assert get_encoded_household_id(household_afghanistan_different_areas) not in result_ids


class TestHouseholdFilter:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any, create_user_role_with_permissions: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.list_url = reverse(
            "api:households:households-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program.slug},
        )
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
<<<<<<< HEAD
        self.client = api_client(self.user)
=======
        self.api_client = api_client(self.user)
>>>>>>> e509e33f3be98f6d786746662626b55f342b0433

        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
            business_area=self.afghanistan,
            program=self.program,
        )

    def _create_test_households(
        self,
        household1_data: Optional[dict] = None,
        household2_data: Optional[dict] = None,
        hoh_1_data: Optional[dict] = None,
        hoh_2_data: Optional[dict] = None,
    ) -> Tuple[Household, Household]:
        if household2_data is None:
            household2_data = {}
        if household1_data is None:
            household1_data = {}
        if hoh_1_data is None:
            hoh_1_data = {}
        if hoh_2_data is None:
            hoh_2_data = {}
        household1, _ = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
                **household1_data,
            },
            individuals_data=[hoh_1_data, {}],
        )
        household2, _ = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
                **household2_data,
            },
            individuals_data=[hoh_2_data, {}],
        )
        return household1, household2

    def _test_filter_households_in_list(
        self,
        filters: dict,
        household1_data: Optional[dict] = None,
        household2_data: Optional[dict] = None,
        hoh_1_data: Optional[dict] = None,
        hoh_2_data: Optional[dict] = None,
    ) -> None:
        household1, household2 = self._create_test_households(
            household1_data=household1_data,
            household2_data=household2_data,
            hoh_1_data=hoh_1_data,
            hoh_2_data=hoh_2_data,
        )
<<<<<<< HEAD
        response = self.client.get(self.list_url, filters)
=======
        response = self.api_client.get(self.list_url, filters)
>>>>>>> e509e33f3be98f6d786746662626b55f342b0433
        assert response.status_code == status.HTTP_200_OK, response.json()
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == encode_id_base64_required(household1.id, "Household")
        return response_data

    def test_filter_by_rdi_id(self) -> None:
        registration_data_import_household1 = RegistrationDataImportFactory(
            imported_by=self.user, business_area=self.afghanistan, program=self.program
        )
        registration_data_import_household2 = RegistrationDataImportFactory(
            imported_by=self.user, business_area=self.afghanistan, program=self.program
        )
        self._test_filter_households_in_list(
            filters={
                "rdi_id": encode_id_base64_required(registration_data_import_household1.id, "RegistrationDataImport")
            },
            household1_data={
                "registration_data_import": registration_data_import_household1,
            },
            household2_data={
                "registration_data_import": registration_data_import_household2,
            },
        )

    def test_filter_by_size(self) -> None:
        self._test_filter_households_in_list(
            filters={"size_min": "5"},
            household1_data={"size": 6},
            household2_data={"size": 4},
        )

    def test_filter_by_document_number(self) -> None:
        document_passport = DocumentTypeFactory(key="passport")
        document_id_card = DocumentTypeFactory(key="id_card")
        household_passport1, individuals_passport1 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        hoh_household_passport1 = individuals_passport1[0]
        household_passport2, individuals_passport2 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        hoh_household_passport2 = individuals_passport2[0]
        household_id_card, individuals_id_card = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        hoh_household_id_card = individuals_id_card[0]
        DocumentFactory(individual=hoh_household_passport1, type=document_passport, document_number="123")
        DocumentFactory(individual=hoh_household_passport2, type=document_passport, document_number="456")
        DocumentFactory(individual=hoh_household_id_card, type=document_id_card, document_number="123")
<<<<<<< HEAD
        response = self.client.get(self.list_url, {"document_number": "123", "document_type": "passport"})
=======
        response = self.api_client.get(self.list_url, {"document_number": "123", "document_type": "passport"})
>>>>>>> e509e33f3be98f6d786746662626b55f342b0433
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == encode_id_base64_required(household_passport1.id, "Household")

    def test_filter_by_address(self) -> None:
        self._test_filter_households_in_list(
            filters={"address": "test address"},
            household1_data={"address": "test address"},
            household2_data={"address": "different address"},
        )

    def test_filter_by_head_of_household_full_name(self) -> None:
        self._test_filter_households_in_list(
            filters={"head_of_household__full_name": "John"},
            hoh_1_data={"full_name": "John Doe"},
            hoh_2_data={"full_name": "Jane Doe"},
        )

    def test_filter_by_head_of_household_phone_no_valid_true(self) -> None:
        invalid_phone_number = "12"
        valid_phone_number = "+48 609 456 789"
        self._test_filter_households_in_list(
            filters={"head_of_household__phone_no_valid": True},
            hoh_1_data={
                "phone_no": valid_phone_number,
                "phone_no_alternative": valid_phone_number,
            },
            hoh_2_data={
                "phone_no": invalid_phone_number,
                "phone_no_alternative": invalid_phone_number,
            },
        )

    def test_filter_by_head_of_household_phone_no_valid_false(self) -> None:
        invalid_phone_number = "12"
        valid_phone_number = "+48 609 456 789"
        self._test_filter_households_in_list(
            filters={"head_of_household__phone_no_valid": False},
            hoh_1_data={
                "phone_no": invalid_phone_number,
                "phone_no_alternative": invalid_phone_number,
            },
            hoh_2_data={
                "phone_no": invalid_phone_number,
                "phone_no_alternative": valid_phone_number,
            },
        )

    def test_filter_by_withdrawn(self) -> None:
        self._test_filter_households_in_list(
            filters={"withdrawn": True},
            household1_data={"withdrawn": True},
            household2_data={"withdrawn": False},
        )

    def test_filter_by_country_origin(self) -> None:
        afghanistan = CountryFactory()
        ukraine = CountryFactory(name="Ukraine", iso_code3="UKR", iso_code2="UK", iso_num="050")
        self._test_filter_households_in_list(
            filters={"country_origin": afghanistan.iso_code3},
            household1_data={"country_origin": afghanistan},
            household2_data={"country_origin": ukraine},
        )

    @pytest.mark.parametrize(
        "program_status,filter_value,expected_results",
        [
            (Program.ACTIVE, True, 2),
            (Program.FINISHED, True, 0),
            (Program.ACTIVE, False, 0),
            (Program.FINISHED, False, 2),
        ],
    )
    def test_filter_by_is_active_program(self, program_status: str, filter_value: bool, expected_results: int) -> None:
        self.program.status = program_status
        self.program.save()

        self._create_test_households()
<<<<<<< HEAD
        response = self.client.get(self.list_url, {"is_active_program": filter_value})
=======
        response = self.api_client.get(self.list_url, {"is_active_program": filter_value})
>>>>>>> e509e33f3be98f6d786746662626b55f342b0433
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == expected_results

    def test_filter_by_rdi_merge_status(self) -> None:
        self._test_filter_households_in_list(
            filters={"rdi_merge_status": MergeStatusModel.PENDING},
            household1_data={"rdi_merge_status": MergeStatusModel.PENDING},
            household2_data={"rdi_merge_status": MergeStatusModel.MERGED},
        )

    @pytest.mark.parametrize(
        "filter_by_field",
        [
            "admin_area",
            "admin1",
            "admin2",
        ],
    )
    def test_filter_by_area(self, filter_by_field: str) -> None:
        country = CountryFactory()
        admin_type_1 = AreaTypeFactory(country=country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
        area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
        area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
<<<<<<< HEAD

        self._test_filter_households_in_list(
            filters={filter_by_field: area1.id},
=======
        encoded_id = encode_id_base64_required(area1.id, "Area")
        self._test_filter_households_in_list(
            filters={filter_by_field: encoded_id},
>>>>>>> e509e33f3be98f6d786746662626b55f342b0433
            household1_data={filter_by_field: area1},
            household2_data={filter_by_field: area2},
        )

    def test_filter_by_residence_status(self) -> None:
        self._test_filter_households_in_list(
            filters={"residence_status": REFUGEE},
            household1_data={"residence_status": REFUGEE},
            household2_data={"residence_status": HOST},
        )

    def test_filter_by_last_registration_date(self) -> None:
        self._test_filter_households_in_list(
            filters={"last_registration_date_after": "2022-12-31"},
            household1_data={"last_registration_date": timezone.make_aware(timezone.datetime(2023, 1, 1))},
            household2_data={"last_registration_date": timezone.make_aware(timezone.datetime(2021, 1, 1))},
        )

    def test_filter_by_first_registration_date(self) -> None:
        self._test_filter_households_in_list(
            filters={"first_registration_date": "2022-12-31"},
            household1_data={"first_registration_date": timezone.make_aware(timezone.datetime(2022, 12, 31))},
            household2_data={"first_registration_date": timezone.make_aware(timezone.datetime(2022, 12, 30))},
        )

    @override_config(USE_ELASTICSEARCH_FOR_HOUSEHOLDS_SEARCH=True)
    @pytest.mark.parametrize(
        "filters,household1_data,household2_data,hoh_1_data,hoh_2_data",
        [
            ({"search": "HH-123"}, {"unicef_id": "HH-123"}, {"unicef_id": "HH-321"}, {}, {}),
            ({"search": "John"}, {}, {}, {"full_name": "John Doe"}, {"full_name": "Jane Doe"}),
            ({"search": "IND-123"}, {}, {}, {"unicef_id": "IND-123"}, {"unicef_id": "IND-321"}),
            ({"search": "123456789"}, {}, {}, {"phone_no": "123456789"}, {"phone_no": "987654321"}),
            (
                {"search": "123456789"},
                {},
                {},
                {"phone_no_alternative": "123 456 789"},
                {"phone_no_alternative": "987 654 321"},
            ),
            ({"search": "HOPE-123"}, {"detail_id": "HOPE-123"}, {"detail_id": "HOPE-321"}, {}, {}),
            ({"search": "456"}, {"program_registration_id": "456"}, {"program_registration_id": "123"}, {}, {}),
        ],
    )
<<<<<<< HEAD
    def test_search(self, filters, household1_data, household2_data, hoh_1_data, hoh_2_data):
=======
    def test_search(
        self, filters: Dict, household1_data: Dict, household2_data: Dict, hoh_1_data: Dict, hoh_2_data: Dict
    ) -> None:
>>>>>>> e509e33f3be98f6d786746662626b55f342b0433
        household1, household2 = self._create_test_households(
            household1_data=household1_data,
            household2_data=household2_data,
            hoh_1_data=hoh_1_data,
            hoh_2_data=hoh_2_data,
        )
        rebuild_search_index()
<<<<<<< HEAD
        response = self.client.get(self.list_url, filters)
=======
        response = self.api_client.get(self.list_url, filters)
>>>>>>> e509e33f3be98f6d786746662626b55f342b0433
        assert response.status_code == status.HTTP_200_OK, response.json()
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == encode_id_base64_required(household1.id, "Household")
        return response_data

    @override_config(USE_ELASTICSEARCH_FOR_HOUSEHOLDS_SEARCH=True)
<<<<<<< HEAD
    def test_search_by_bank_account_number(self):
=======
    def test_search_by_bank_account_number(self) -> None:
>>>>>>> e509e33f3be98f6d786746662626b55f342b0433
        household1, individuals1 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        household2, individuals2 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        BankAccountInfoFactory(bank_account_number="123456789", individual=individuals1[0])
        BankAccountInfoFactory(bank_account_number="987654321", individual=individuals2[0])
        rebuild_search_index()
<<<<<<< HEAD
        response = self.client.get(self.list_url, {"search": "123456789"})
=======
        response = self.api_client.get(self.list_url, {"search": "123456789"})
>>>>>>> e509e33f3be98f6d786746662626b55f342b0433
        assert response.status_code == status.HTTP_200_OK, response.json()
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == encode_id_base64_required(household1.id, "Household")
        return response_data
