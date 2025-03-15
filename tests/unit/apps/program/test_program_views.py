import datetime
from enum import Enum
from typing import Any

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import (
    DataCollectingTypeFactory,
    FlexibleAttributeForPDUFactory,
    create_afghanistan,
    create_ukraine,
)
from hct_mis_api.apps.core.utils import encode_id_base64_required
from hct_mis_api.apps.household.fixtures import HouseholdFactory
from hct_mis_api.apps.program.fixtures import BeneficiaryGroupFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db


class TestProgramListViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.list_url = reverse(
            "api:programs:programs-list",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

        self.pdu_field1 = FlexibleAttributeForPDUFactory(program=self.program)
        self.pdu_field2 = FlexibleAttributeForPDUFactory(program=self.program)

        # programs that should not be on the list
        ukraine = create_ukraine()
        self.program_in_ukraine = ProgramFactory(business_area=ukraine)

        deprecated_dct = DataCollectingTypeFactory(deprecated=True)
        self.program_with_dct_deprecated = ProgramFactory(
            business_area=self.afghanistan, name="Deprecated DCT Program", data_collecting_type=deprecated_dct
        )

        unknown_dct = DataCollectingTypeFactory(code="unknown")
        self.program_with_unknown_dct = ProgramFactory(
            business_area=self.afghanistan,
            name="Unknown DCT Program",
            data_collecting_type=unknown_dct,
        )

        self.program_not_allowed = ProgramFactory(business_area=self.afghanistan, name="Not Allowed Program")

    @pytest.mark.parametrize(
        "permissions",
        [
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            [Permissions.GRIEVANCES_CREATE],
            [Permissions.GRIEVANCES_UPDATE],
            [Permissions.GRIEVANCES_UPDATE_AS_CREATOR],
            [Permissions.GRIEVANCES_UPDATE_AS_OWNER],
            [Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE],
            [Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR],
            [Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER],
        ],
    )
    def test_program_list_with_permissions(
        self,
        permissions: list,
        create_user_role_with_permissions: Any,
    ) -> None:
        for program in [
            self.program,
            self.program_in_ukraine,
            self.program_with_dct_deprecated,
            self.program_with_unknown_dct,
        ]:
            create_user_role_with_permissions(
                self.user,
                permissions,
                self.afghanistan,
                program,
            )
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        program_ids = [program["id"] for program in response_data]
        assert encode_id_base64_required(self.program.id, "Program") in program_ids
        assert encode_id_base64_required(self.program_in_ukraine.id, "Program") not in program_ids
        assert encode_id_base64_required(self.program_with_dct_deprecated.id, "Program") not in program_ids
        assert encode_id_base64_required(self.program_with_unknown_dct.id, "Program") not in program_ids
        assert encode_id_base64_required(self.program_not_allowed.id, "Program") not in program_ids

        program_data1 = response_data[0]
        assert program_data1["id"] == encode_id_base64_required(self.program.id, "Program")
        assert program_data1["programme_code"] == self.program.programme_code
        assert program_data1["slug"] == self.program.slug
        assert program_data1["name"] == self.program.name
        assert program_data1["start_date"] == self.program.start_date.strftime("%Y-%m-%d")
        assert program_data1["end_date"] == self.program.end_date.strftime("%Y-%m-%d")
        assert program_data1["budget"] == str(self.program.budget)
        assert program_data1["frequency_of_payments"] == self.program.frequency_of_payments
        assert program_data1["sector"] == self.program.sector
        assert program_data1["cash_plus"] == self.program.cash_plus
        assert program_data1["population_goal"] == self.program.population_goal
        assert program_data1["status"] == self.program.status
        assert program_data1["household_count"] == self.program.household_count

        data_collecting_type_program_data1 = program_data1["data_collecting_type"]
        assert data_collecting_type_program_data1["id"] == self.program.data_collecting_type.id
        assert data_collecting_type_program_data1["label"] == self.program.data_collecting_type.label
        assert data_collecting_type_program_data1["code"] == self.program.data_collecting_type.code
        assert data_collecting_type_program_data1["type"] == self.program.data_collecting_type.get_type_display()
        assert (
            data_collecting_type_program_data1["household_filters_available"]
            == self.program.data_collecting_type.household_filters_available
        )
        assert (
            data_collecting_type_program_data1["individual_filters_available"]
            == self.program.data_collecting_type.individual_filters_available
        )

        beneficiary_group_program_data1 = program_data1["beneficiary_group"]
        assert beneficiary_group_program_data1["id"] == str(self.program.beneficiary_group.id)
        assert beneficiary_group_program_data1["name"] == self.program.beneficiary_group.name
        assert beneficiary_group_program_data1["group_label"] == self.program.beneficiary_group.group_label
        assert (
            beneficiary_group_program_data1["group_label_plural"] == self.program.beneficiary_group.group_label_plural
        )
        assert beneficiary_group_program_data1["member_label"] == self.program.beneficiary_group.member_label
        assert (
            beneficiary_group_program_data1["member_label_plural"] == self.program.beneficiary_group.member_label_plural
        )
        assert beneficiary_group_program_data1["master_detail"] == self.program.beneficiary_group.master_detail

        assert encode_id_base64_required(self.pdu_field1, "FlexibleAttribute") in program_data1["pdu_fields"]
        assert encode_id_base64_required(self.pdu_field2, "FlexibleAttribute") in program_data1["pdu_fields"]

    @pytest.mark.parametrize(
        "permissions",
        [
            [],
            [Permissions.PM_SEND_XLSX_PASSWORD],
        ],
    )
    def test_program_list_without_permissions(
        self,
        permissions: Enum,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            permissions,
            self.afghanistan,
            self.program,
        )
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_program_list_ordering(self, create_user_role_with_permissions: Any) -> None:
        program_finished = ProgramFactory(business_area=self.afghanistan, status=Program.FINISHED)
        program_draft_first = ProgramFactory(
            business_area=self.afghanistan, status=Program.DRAFT, start_date=datetime.datetime(2000, 1, 1)
        )
        program_draft_second = ProgramFactory(
            business_area=self.afghanistan, status=Program.DRAFT, start_date=datetime.datetime(2001, 1, 1)
        )
        for program in [
            self.program,
            program_finished,
            program_draft_first,
            program_draft_second,
        ]:
            create_user_role_with_permissions(
                self.user,
                [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
                self.afghanistan,
                program,
            )
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 4

        assert response_data[0]["id"] == encode_id_base64_required(program_draft_first.id, "Program")
        assert response_data[1]["id"] == encode_id_base64_required(program_draft_second.id, "Program")
        assert response_data[2]["id"] == encode_id_base64_required(self.program.id, "Program")
        assert response_data[3]["id"] == encode_id_base64_required(program_finished.id, "Program")


class TestProgramFilter:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any, create_user_role_with_permissions: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.list_url = reverse("api:programs:programs-list", kwargs={"business_area_slug": self.afghanistan.slug})
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)
        self.create_user_role_with_permissions = create_user_role_with_permissions

    def _test_two_programs_in_list(
        self,
        program1_data: dict,
        program2_data: dict,
        filters: dict,
    ) -> dict:
        program1 = ProgramFactory(business_area=self.afghanistan, **program1_data)
        program2 = ProgramFactory(business_area=self.afghanistan, **program2_data)
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.afghanistan, program1
        )
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.afghanistan, program2
        )

        response = self.client.get(self.list_url, filters)
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == encode_id_base64_required(program1.id, "Program")
        return response_data

    def test_filter_by_status(self) -> None:
        response_data = self._test_two_programs_in_list(
            {"status": Program.ACTIVE}, {"status": Program.FINISHED}, {"status": Program.ACTIVE}
        )
        assert response_data[0]["status"] == Program.ACTIVE

    def test_filter_by_sector(self) -> None:
        response_data = self._test_two_programs_in_list(
            {"sector": Program.HEALTH}, {"sector": Program.EDUCATION}, {"sector": Program.HEALTH}
        )
        assert response_data[0]["sector"] == Program.HEALTH

    def test_filter_by_budget(self) -> None:
        response_data = self._test_two_programs_in_list({"budget": 2000}, {"budget": 1000}, {"budget_min": 1500})
        assert response_data[0]["budget"] == "2000.00"

    def test_filter_by_start_date(self) -> None:
        response_data = self._test_two_programs_in_list(
            {"start_date": datetime.datetime(2023, 1, 1)},
            {"start_date": datetime.datetime(2022, 1, 1)},
            {"start_date": "2022-12-31"},
        )
        assert response_data[0]["start_date"] == "2023-01-01"

    def test_filter_by_end_date(self) -> None:
        response_data = self._test_two_programs_in_list(
            {"start_date": datetime.datetime(2020, 1, 1), "end_date": datetime.datetime(2022, 1, 1)},
            {"start_date": datetime.datetime(2020, 1, 1), "end_date": datetime.datetime(2023, 1, 1)},
            {"end_date": "2022-12-31"},
        )
        assert response_data[0]["end_date"] == "2022-01-01"

    def test_filter_by_name(self) -> None:
        self._test_two_programs_in_list({"name": "Health Program"}, {"name": "Education Program"}, {"name": "Health"})

    def test_filter_by_compatible_dct(self) -> None:
        dct1 = DataCollectingTypeFactory(code="type1")
        dct2 = DataCollectingTypeFactory(code="type2")
        dct2.compatible_types.add(dct1)
        program1 = ProgramFactory(business_area=self.afghanistan, data_collecting_type=dct1)
        program2 = ProgramFactory(business_area=self.afghanistan, data_collecting_type=dct2)
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.afghanistan, program1
        )
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.afghanistan, program2
        )

        response = self.client.get(self.list_url, {"compatible_dct": program1.slug})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == encode_id_base64_required(program2.id, "Program")

    def test_filter_by_beneficiary_group_match(self) -> None:
        beneficiary_group1 = BeneficiaryGroupFactory(name="Group1")
        beneficiary_group2 = BeneficiaryGroupFactory(name="Group2")
        program1 = ProgramFactory(business_area=self.afghanistan, beneficiary_group=beneficiary_group1)
        program2 = ProgramFactory(business_area=self.afghanistan, beneficiary_group=beneficiary_group2)
        program3 = ProgramFactory(business_area=self.afghanistan, beneficiary_group=beneficiary_group1)
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.afghanistan, program1
        )
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.afghanistan, program2
        )

        # additional check to test filter doesn't break allowed_programs constraints
        response = self.client.get(self.list_url, {"beneficiary_group_match": program1.slug})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 0

        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.afghanistan, program3
        )
        response = self.client.get(self.list_url, {"beneficiary_group_match": program1.slug})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == encode_id_base64_required(program3.id, "Program")

    def test_filter_by_search(self) -> None:
        program1 = ProgramFactory(business_area=self.afghanistan, name="Health Program")
        program2 = ProgramFactory(business_area=self.afghanistan, name="Education Program")
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.afghanistan, program1
        )
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.afghanistan, program2
        )

        response = self.client.get(self.list_url, {"search": "Health"})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == encode_id_base64_required(program1.id, "Program")

    def test_filter_number_of_households(self) -> None:
        program1 = ProgramFactory(business_area=self.afghanistan)
        program2 = ProgramFactory(business_area=self.afghanistan)
        HouseholdFactory.create_batch(5, business_area=self.afghanistan, program=program1)
        HouseholdFactory.create_batch(3, business_area=self.afghanistan, program=program2)
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.afghanistan, program1
        )
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.afghanistan, program2
        )

        response = self.client.get(self.list_url, {"number_of_households_min": 4})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == encode_id_base64_required(program1.id, "Program")
