import copy
from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import (
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from extras.test_utils.factories.core import (
    DataCollectingTypeFactory,
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
    create_ukraine,
)
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.program import (
    BeneficiaryGroupFactory,
    ProgramCycleFactory,
    ProgramFactory,
)
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.models import (
    DataCollectingType,
    FlexibleAttribute,
    PeriodicFieldData,
)
from hope.apps.program.models import Program, ProgramCycle

pytestmark = pytest.mark.django_db


class TestProgramUpdate:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()

        self.unicef_partner = PartnerFactory(name="UNICEF")
        self.unicef_hq = PartnerFactory(name="UNICEF HQ", parent=self.unicef_partner)
        self.unicef_partner_in_afghanistan = PartnerFactory(
            name="UNICEF Partner for afghanistan", parent=self.unicef_partner
        )

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

        self.country = CountryFactory()
        self.country.business_areas.set([self.afghanistan])
        admin_type = AreaTypeFactory(country=self.country, area_level=1)
        self.area1 = AreaFactory(parent=None, area_type=admin_type, p_code="AF01U", name="Area1")
        self.area2 = AreaFactory(parent=None, area_type=admin_type, p_code="AF02U", name="Area2")

        self.dct_standard = DataCollectingTypeFactory(label="Full", code="full", type=DataCollectingType.Type.STANDARD)
        self.dct_social = DataCollectingTypeFactory(
            label="SW Full", code="sw_full", type=DataCollectingType.Type.SOCIAL
        )

        self.bg_household = BeneficiaryGroupFactory(name="Household", master_detail=True)
        self.bg_sw = BeneficiaryGroupFactory(name="Social Worker", master_detail=False)

        self.initial_program_data = {
            "name": "Test Program To Update",
            "programme_code": "PROU",
            "description": "Initial description.",
            "start_date": "2030-01-01",
            "end_date": "2033-12-31",
            "sector": Program.CHILD_PROTECTION,
            "data_collecting_type": self.dct_standard,
            "beneficiary_group": self.bg_household,
            "budget": 100000,
            "population_goal": 100,
            "status": Program.DRAFT,
            "partner_access": Program.NONE_PARTNERS_ACCESS,
            "cash_plus": False,
            "frequency_of_payments": Program.REGULAR,
            "administrative_areas_of_implementation": "Areas of Implementation21",
        }
        self.program = ProgramFactory(**self.initial_program_data, business_area=self.afghanistan)
        role_with_all_permissions = RoleFactory(name="Role with all permissions")
        RoleAssignmentFactory(
            partner=self.partner,
            business_area=self.afghanistan,
            program=self.program,
            role=role_with_all_permissions,
        )

        self.update_url = reverse(
            "api:programs:programs-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "slug": self.program.slug,
            },
        )

        # pdu fields
        self.pdu_data_to_be_removed = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=3,
            rounds_names=[
                "Round 1 To Be Removed",
                "Round 2 To Be Removed",
                "Round 3 To Be Removed",
            ],
        )
        self.pdu_field_to_be_removed = FlexibleAttributeForPDUFactory(
            program=self.program,
            label="PDU Field To Be Removed",
            pdu_data=self.pdu_data_to_be_removed,
        )
        self.pdu_data_to_be_updated = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=2,
            rounds_names=["Round 1 To Be Updated", "Round 2 To Be Updated"],
        )
        self.pdu_field_to_be_updated = FlexibleAttributeForPDUFactory(
            program=self.program,
            label="PDU Field To Be Updated",
            pdu_data=self.pdu_data_to_be_updated,
        )
        self.pdu_data_to_be_preserved = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DATE,
            number_of_rounds=1,
            rounds_names=["Round To Be Preserved"],
        )
        self.pdu_field_to_be_preserved = FlexibleAttributeForPDUFactory(
            program=self.program,
            label="PDU Field To Be Preserved",
            pdu_data=self.pdu_data_to_be_preserved,
        )

        self.base_payload_for_update_without_changes = {
            **self.initial_program_data,
            "slug": self.program.slug,
            "version": self.program.version,
            "data_collecting_type": self.dct_standard.code,
            "beneficiary_group": str(self.bg_household.id),
            "pdu_fields": [
                {
                    "id": str(self.pdu_field_to_be_preserved.id),
                    "label": "PDU Field To Be Preserved",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_preserved.subtype,
                        "number_of_rounds": self.pdu_data_to_be_preserved.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_preserved.rounds_names,
                    },
                },
                {
                    "id": str(self.pdu_field_to_be_removed.id),
                    "label": "PDU Field To Be Removed",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_removed.subtype,
                        "number_of_rounds": self.pdu_data_to_be_removed.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_removed.rounds_names,
                    },
                },
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field To Be Updated",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_updated.subtype,
                        "number_of_rounds": self.pdu_data_to_be_updated.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_updated.rounds_names,
                    },
                },
            ],
        }

        self.base_expected_response_without_changes = {
            **self.base_payload_for_update_without_changes,
            "budget": f"{self.program.budget:.2f}",
            "pdu_fields": [
                {
                    **pdu_field_data,
                    "name": pdu_field.name,
                    "pdu_data": {**pdu_field_data["pdu_data"], "rounds_covered": 0},
                }
                for pdu_field_data, pdu_field in zip(
                    self.base_payload_for_update_without_changes["pdu_fields"],
                    [
                        self.pdu_field_to_be_preserved,
                        self.pdu_field_to_be_removed,
                        self.pdu_field_to_be_updated,
                    ],
                    strict=True,
                )
            ],
            "partners": [
                {
                    "id": self.partner.id,
                    "name": self.partner.name,
                    "areas": None,
                    "area_access": "BUSINESS_AREA",
                },
                {
                    "id": self.unicef_hq.id,
                    "name": self.unicef_hq.name,
                    "areas": None,
                    "area_access": "BUSINESS_AREA",
                },
                {
                    "id": self.unicef_partner_in_afghanistan.id,
                    "name": self.unicef_partner_in_afghanistan.name,
                    "areas": None,
                    "area_access": "BUSINESS_AREA",
                },
            ],
        }

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PROGRAMME_UPDATE], status.HTTP_200_OK),
            ([Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], status.HTTP_403_FORBIDDEN),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_update_program_permissions(
        self,
        permissions: list,
        expected_status: int,
        create_user_role_with_permissions: Callable,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, whole_business_area_access=True)

        payload = {
            **self.base_payload_for_update_without_changes,
            "name": "Test Program Updated",
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == expected_status

        if expected_status == status.HTTP_200_OK:
            self.program.refresh_from_db()
            assert self.program.name == "Test Program Updated"
            self.program.refresh_from_db()
            assert response.json() == {
                **self.base_expected_response_without_changes,
                "name": "Test Program Updated",
                "version": self.program.version,
            }

    def test_update_program_with_no_changes(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = copy.deepcopy(self.base_payload_for_update_without_changes)
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_200_OK

        old_program_instance = self.program
        self.program.refresh_from_db()
        assert self.program == old_program_instance
        assert response.json() == {
            **self.base_expected_response_without_changes,
            "version": self.program.version,
        }

    def test_update_programme_code(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_payload_for_update_without_changes,
            "programme_code": "NEWP",
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_200_OK

        self.program.refresh_from_db()
        assert self.program.programme_code == "NEWP"
        assert self.program.slug == "newp"
        assert response.json() == {
            **self.base_expected_response_without_changes,
            "programme_code": "NEWP",
            "slug": "newp",
            "version": self.program.version,
        }

    def test_update_programme_code_with_empty(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_payload_for_update_without_changes,
            "programme_code": None,
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_200_OK

        self.program.refresh_from_db()
        assert self.program.programme_code != self.initial_program_data["programme_code"]
        assert self.program.slug != self.initial_program_data["programme_code"]
        assert response.json() == {
            **self.base_expected_response_without_changes,
            "programme_code": self.program.programme_code,
            "slug": self.program.slug,
            "version": self.program.version,
        }

    def test_update_programme_code_invalid(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_payload_for_update_without_changes,
            "programme_code": " T#ST",
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "programme_code" in response.json()
        assert (
            "Programme code should be exactly 4 characters long and may only contain letters, digits and character: -"
            in response.json()["programme_code"][0]
        )

        self.program.refresh_from_db()
        assert self.program.programme_code == self.initial_program_data["programme_code"]

    def test_update_programme_code_existing(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        ProgramFactory(programme_code="T3ST", business_area=self.afghanistan)

        payload = {
            **self.base_payload_for_update_without_changes,
            "programme_code": " T3ST",
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "programme_code" in response.json()
        assert response.json()["programme_code"][0] == "Programme code is already used."

        self.program.refresh_from_db()
        assert self.program.programme_code == self.initial_program_data["programme_code"]

    def test_update_data_collecting_type(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        dct_2 = DataCollectingTypeFactory(label="DCT2", code="dct2", type=DataCollectingType.Type.STANDARD)

        payload = {
            **self.base_payload_for_update_without_changes,
            "data_collecting_type": dct_2.code,
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_200_OK

        self.program.refresh_from_db()
        assert self.program.data_collecting_type == dct_2
        assert response.json() == {
            **self.base_expected_response_without_changes,
            "data_collecting_type": dct_2.code,
            "version": self.program.version,
        }

    def test_update_data_collecting_type_invalid(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        dct_invalid = DataCollectingTypeFactory(
            label="DCT_INVALID",
            code="dct_invalid",
            type=DataCollectingType.Type.STANDARD,
        )
        payload = {
            **self.base_payload_for_update_without_changes,
            "data_collecting_type": dct_invalid.code,
        }

        # DCT inactive
        dct_invalid.active = False
        dct_invalid.save()
        response_for_inactive = self.client.put(self.update_url, payload)
        assert response_for_inactive.status_code == status.HTTP_400_BAD_REQUEST
        assert "data_collecting_type" in response_for_inactive.json()
        assert (
            response_for_inactive.json()["data_collecting_type"][0]
            == "Only active Data Collecting Type can be used in Program."
        )
        self.program.refresh_from_db()
        assert self.program.data_collecting_type == self.dct_standard

        # DCT deprecated
        dct_invalid.active = True
        dct_invalid.deprecated = True
        dct_invalid.save()
        response_for_deprecated = self.client.put(self.update_url, payload)
        assert response_for_deprecated.status_code == status.HTTP_400_BAD_REQUEST
        assert "data_collecting_type" in response_for_deprecated.json()
        assert (
            response_for_deprecated.json()["data_collecting_type"][0]
            == "Deprecated Data Collecting Type cannot be used in Program."
        )
        self.program.refresh_from_db()
        assert self.program.data_collecting_type == self.dct_standard

        # DCT limited to another BA
        dct_invalid.deprecated = False
        dct_invalid.save()
        ukraine = create_ukraine()
        dct_invalid.limit_to.add(ukraine)
        response_for_limited = self.client.put(self.update_url, payload)
        assert response_for_limited.status_code == status.HTTP_400_BAD_REQUEST
        assert "data_collecting_type" in response_for_limited.json()
        assert (
            response_for_limited.json()["data_collecting_type"][0]
            == "This Data Collecting Type is not available for this Business Area."
        )
        self.program.refresh_from_db()
        assert self.program.data_collecting_type == self.dct_standard

    def test_update_data_collecting_type_for_active_program(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        dct_2 = DataCollectingTypeFactory(label="DCT2", code="dct2", type=DataCollectingType.Type.STANDARD)

        self.program.status = Program.ACTIVE
        self.program.save()

        payload = {
            **self.base_payload_for_update_without_changes,
            "data_collecting_type": dct_2.code,
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "data_collecting_type" in response.json()
        assert (
            response.json()["data_collecting_type"][0] == "Data Collecting Type can be updated only for Draft Programs."
        )
        self.program.refresh_from_db()
        assert self.program.data_collecting_type == self.dct_standard

    def test_update_data_collecting_type_for_program_with_population(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        dct_2 = DataCollectingTypeFactory(label="DCT2", code="dct2", type=DataCollectingType.Type.STANDARD)

        create_household_and_individuals(
            household_data={
                "program": self.program,
            },
            individuals_data=[{}, {}],
        )

        payload = {
            **self.base_payload_for_update_without_changes,
            "data_collecting_type": dct_2.code,
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "data_collecting_type" in response.json()
        assert (
            response.json()["data_collecting_type"][0]
            == "Data Collecting Type can be updated only for Program without any households."
        )
        self.program.refresh_from_db()
        assert self.program.data_collecting_type == self.dct_standard

    def test_update_data_collecting_type_invalid_with_beneficiary_group(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        payload = {
            **self.base_payload_for_update_without_changes,
            "data_collecting_type": self.dct_social.code,
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "beneficiary_group" in response.json()
        assert (
            response.json()["beneficiary_group"][0]
            == "Selected combination of data collecting type and beneficiary group is invalid."
        )

        self.program.refresh_from_db()
        assert self.program.data_collecting_type == self.dct_standard

    def test_update_beneficiary_group(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        bg_2 = BeneficiaryGroupFactory(name="Beneficiary Group 2", master_detail=True)

        payload = {
            **self.base_payload_for_update_without_changes,
            "beneficiary_group": str(bg_2.id),
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_200_OK

        self.program.refresh_from_db()
        assert self.program.beneficiary_group == bg_2
        assert response.json() == {
            **self.base_expected_response_without_changes,
            "beneficiary_group": str(bg_2.id),
            "version": self.program.version,
        }

    def test_update_beneficiary_group_invalid_with_data_collecting_type(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_payload_for_update_without_changes,
            "beneficiary_group": str(self.bg_sw.id),
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "beneficiary_group" in response.json()
        assert (
            response.json()["beneficiary_group"][0]
            == "Selected combination of data collecting type and beneficiary group is invalid."
        )

        self.program.refresh_from_db()
        assert self.program.beneficiary_group == self.bg_household

    def test_update_beneficiary_group_invalid_with_population(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        bg_2 = BeneficiaryGroupFactory(name="Beneficiary Group 2", master_detail=True)

        RegistrationDataImportFactory(program=self.program, business_area=self.afghanistan)

        payload = {
            **self.base_payload_for_update_without_changes,
            "beneficiary_group": str(bg_2.id),
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "beneficiary_group" in response.json()
        assert (
            response.json()["beneficiary_group"][0] == "Beneficiary Group cannot be updated if Program has population."
        )

        self.program.refresh_from_db()
        assert self.program.beneficiary_group == self.bg_household

    def test_update_start_and_end_dates(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        program_cycle = ProgramCycle.objects.filter(program=self.program).first()
        program_cycle.start_date = "2030-06-01"
        program_cycle.end_date = "2030-06-20"

        payload = {
            **self.base_payload_for_update_without_changes,
            "start_date": "2030-01-01",
            "end_date": "2033-12-31",
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_200_OK

        self.program.refresh_from_db()
        assert self.program.start_date.strftime("%Y-%m-%d") == payload["start_date"]
        assert self.program.end_date.strftime("%Y-%m-%d") == payload["end_date"]
        assert response.json() == {
            **self.base_expected_response_without_changes,
            "start_date": payload["start_date"],
            "end_date": payload["end_date"],
            "version": self.program.version,
        }

    def test_update_end_date_and_start_date_invalid_end_date_before_start_date(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_payload_for_update_without_changes,
            "start_date": "2033-01-01",
            "end_date": "2032-12-31",
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "end_date" in response.json()
        assert "End date cannot be earlier than the start date." in response.json()["end_date"][0]

        self.program.refresh_from_db()
        assert self.program.start_date.strftime("%Y-%m-%d") == self.initial_program_data["start_date"]
        assert self.program.end_date.strftime("%Y-%m-%d") == self.initial_program_data["end_date"]

    def test_update_end_date_and_start_date_invalid_end_date_before_last_cycle(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        program_cycle = ProgramCycle.objects.filter(program=self.program).first()
        program_cycle.start_date = "2030-06-01"
        program_cycle.end_date = "2030-06-20"
        program_cycle.save()
        ProgramCycleFactory(program=self.program, start_date="2032-01-01", end_date="2033-12-31")

        payload = {
            **self.base_payload_for_update_without_changes,
            "start_date": "2030-01-01",  # Start date is valid
            "end_date": "2033-06-30",  # End date is before the latest cycle's end_date
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "end_date" in response.json()
        assert "End date must be the same as or after the latest cycle." in response.json()["end_date"][0]

        self.program.refresh_from_db()
        assert self.program.start_date.strftime("%Y-%m-%d") == self.initial_program_data["start_date"]
        assert self.program.end_date.strftime("%Y-%m-%d") == self.initial_program_data["end_date"]

    def test_update_end_date_and_start_date_invalid_start_date_after_first_cycle(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        program_cycle = ProgramCycle.objects.filter(program=self.program).first()
        program_cycle.start_date = "2030-06-01"
        program_cycle.end_date = "2030-06-20"
        program_cycle.save()
        ProgramCycleFactory(program=self.program, start_date="2032-01-01", end_date="2033-12-31")

        payload = {
            **self.base_payload_for_update_without_changes,
            "start_date": "2030-07-01",  # Start date is after the earliest cycle's start_date
            "end_date": "2034-12-31",  # End date is valid
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "start_date" in response.json()
        assert "Start date must be the same as or before the earliest cycle." in response.json()["start_date"][0]

        self.program.refresh_from_db()
        assert self.program.start_date.strftime("%Y-%m-%d") == self.initial_program_data["start_date"]
        assert self.program.end_date.strftime("%Y-%m-%d") == self.initial_program_data["end_date"]

    def test_update_multiple_fields(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_payload_for_update_without_changes,
            "name": "Test Program Updated Multiple Fields",
            "programme_code": "NEWP",
            "description": "Updated description.",
            "budget": 200000,
            "population_goal": 200,
            "cash_plus": True,
            "frequency_of_payments": Program.ONE_OFF,
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_200_OK

        self.program.refresh_from_db()
        assert self.program.name == "Test Program Updated Multiple Fields"
        assert self.program.programme_code == "NEWP"
        assert self.program.slug == "newp"
        assert self.program.description == "Updated description."
        assert self.program.budget == 200000
        assert self.program.population_goal == 200
        assert self.program.cash_plus is True
        assert self.program.frequency_of_payments == Program.ONE_OFF
        assert response.json() == {
            **self.base_expected_response_without_changes,
            "name": "Test Program Updated Multiple Fields",
            "programme_code": "NEWP",
            "slug": "newp",
            "description": "Updated description.",
            "budget": "200000.00",
            "population_goal": 200,
            "cash_plus": True,
            "frequency_of_payments": Program.ONE_OFF,
            "version": self.program.version,
        }

    def test_update_pdu_fields(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_payload_for_update_without_changes,
            "pdu_fields": [
                # "PDU Field To Be Preserved" remains unchanged
                {
                    "id": str(self.pdu_field_to_be_preserved.id),
                    "label": "PDU Field To Be Preserved",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_preserved.subtype,
                        "number_of_rounds": self.pdu_data_to_be_preserved.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_preserved.rounds_names,
                    },
                },
                # "PDU Field To Be Removed" is removed
                # "PDU Field To Be Updated" is updated
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field Updated",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 3,
                        "rounds_names": [
                            "Round 1 Updated",
                            "Round 2 Updated",
                            "Round 3 Updated",
                        ],
                    },
                },
            ],
        }
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 3  # Initial count of PDU fields
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_200_OK
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 2  # After update, one field is removed

        self.pdu_field_to_be_updated.refresh_from_db()
        assert self.pdu_field_to_be_updated.label["English(EN)"] == "PDU Field Updated"
        assert self.pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.BOOL
        assert self.pdu_field_to_be_updated.pdu_data.number_of_rounds == 3
        assert self.pdu_field_to_be_updated.pdu_data.rounds_names == [
            "Round 1 Updated",
            "Round 2 Updated",
            "Round 3 Updated",
        ]
        self.pdu_field_to_be_removed.refresh_from_db()
        assert self.pdu_field_to_be_removed.is_removed is True

        self.program.refresh_from_db()
        assert response.json() == {
            **self.base_expected_response_without_changes,
            "pdu_fields": [
                {
                    "id": str(self.pdu_field_to_be_preserved.id),
                    "label": "PDU Field To Be Preserved",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_preserved.subtype,
                        "number_of_rounds": self.pdu_data_to_be_preserved.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_preserved.rounds_names,
                        "rounds_covered": self.pdu_data_to_be_preserved.rounds_covered,
                    },
                    "name": self.pdu_field_to_be_preserved.name,
                },
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field Updated",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 3,
                        "rounds_names": [
                            "Round 1 Updated",
                            "Round 2 Updated",
                            "Round 3 Updated",
                        ],
                        "rounds_covered": self.pdu_data_to_be_updated.rounds_covered,
                    },
                    "name": self.pdu_field_to_be_updated.name,
                },
            ],
            "version": self.program.version,
        }

    def test_update_pdu_fields_and_add_new(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_payload_for_update_without_changes,
            "pdu_fields": [
                # "PDU Field To Be Preserved" remains unchanged
                {
                    "id": str(self.pdu_field_to_be_preserved.id),
                    "label": "PDU Field To Be Preserved",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_preserved.subtype,
                        "number_of_rounds": self.pdu_data_to_be_preserved.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_preserved.rounds_names,
                    },
                },
                # "PDU Field To Be Removed" is removed
                # "PDU Field To Be Updated" is updated
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field Updated",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 3,
                        "rounds_names": [
                            "Round 1 Updated",
                            "Round 2 Updated",
                            "Round 3 Updated",
                        ],
                    },
                },
                # New PDU field to be added
                {
                    "label": "New PDU Field",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.STRING,
                        "number_of_rounds": 2,
                        "rounds_names": ["Round 1 New", "Round 2 New"],
                    },
                },
            ],
        }
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 3  # Initial count of PDU fields
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_200_OK
        assert (
            FlexibleAttribute.objects.filter(program=self.program).count() == 3
        )  # After update, one field is removed, one is updated, and one new is added

        self.pdu_field_to_be_updated.refresh_from_db()
        assert self.pdu_field_to_be_updated.label["English(EN)"] == "PDU Field Updated"
        assert self.pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.BOOL
        assert self.pdu_field_to_be_updated.pdu_data.number_of_rounds == 3
        assert self.pdu_field_to_be_updated.pdu_data.rounds_names == [
            "Round 1 Updated",
            "Round 2 Updated",
            "Round 3 Updated",
        ]
        self.pdu_field_to_be_removed.refresh_from_db()
        assert self.pdu_field_to_be_removed.is_removed is True
        new_pdu_field = FlexibleAttribute.objects.filter(program=self.program, name="new_pdu_field").first()
        assert new_pdu_field.label["English(EN)"] == "New PDU Field"
        assert new_pdu_field.pdu_data.subtype == PeriodicFieldData.STRING
        assert new_pdu_field.pdu_data.number_of_rounds == 2
        assert new_pdu_field.pdu_data.rounds_names == ["Round 1 New", "Round 2 New"]

        self.program.refresh_from_db()
        assert response.json() == {
            **self.base_expected_response_without_changes,
            "pdu_fields": [
                {
                    "id": str(new_pdu_field.id),
                    "label": "New PDU Field",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.STRING,
                        "number_of_rounds": 2,
                        "rounds_names": ["Round 1 New", "Round 2 New"],
                        "rounds_covered": 0,
                    },
                    "name": new_pdu_field.name,
                },
                {
                    "id": str(self.pdu_field_to_be_preserved.id),
                    "label": "PDU Field To Be Preserved",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_preserved.subtype,
                        "number_of_rounds": self.pdu_data_to_be_preserved.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_preserved.rounds_names,
                        "rounds_covered": self.pdu_data_to_be_preserved.rounds_covered,
                    },
                    "name": self.pdu_field_to_be_preserved.name,
                },
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field Updated",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 3,
                        "rounds_names": [
                            "Round 1 Updated",
                            "Round 2 Updated",
                            "Round 3 Updated",
                        ],
                        "rounds_covered": self.pdu_data_to_be_updated.rounds_covered,
                    },
                    "name": self.pdu_field_to_be_updated.name,
                },
            ],
            "version": self.program.version,
        }

    def test_update_pdu_fields_invalid_data(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_payload_for_update_without_changes,
            "pdu_fields": [
                {
                    "id": str(self.pdu_field_to_be_preserved.id),
                    "label": "PDU Field To Be Preserved",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_preserved.subtype,
                        "number_of_rounds": self.pdu_data_to_be_preserved.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_preserved.rounds_names,
                    },
                },
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field Updated",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 3,
                        "rounds_names": [
                            "Round 1 Updated",
                            "Round 2 Updated",
                            "Round 3 Updated",
                        ],
                    },
                },
                {
                    "label": "New PDU Field",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.STRING,
                        "number_of_rounds": 1,
                        "rounds_names": ["Round 1 New", "Round 2 New"],
                    },
                },
            ],
        }
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 3  # Initial count of PDU fields
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Number of rounds does not match the number of round names." in response.json()
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 3  # No change

        # Check that the fields are not updated
        self.pdu_field_to_be_updated.refresh_from_db()
        assert self.pdu_field_to_be_updated.label["English(EN)"] == "PDU Field To Be Updated"
        assert self.pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.STRING
        assert self.pdu_field_to_be_updated.pdu_data.number_of_rounds == 2
        assert self.pdu_field_to_be_updated.pdu_data.rounds_names == [
            "Round 1 To Be Updated",
            "Round 2 To Be Updated",
        ]
        self.pdu_field_to_be_removed.refresh_from_db()
        assert self.pdu_field_to_be_removed.is_removed is False
        assert FlexibleAttribute.objects.filter(program=self.program, name="new_pdu_field").exists() is False

    def test_update_pdu_fields_invalid_data_duplicated_field_names_in_input(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_payload_for_update_without_changes,
            "pdu_fields": [
                {
                    "id": str(self.pdu_field_to_be_preserved.id),
                    "label": "PDU Field To Be Preserved",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_preserved.subtype,
                        "number_of_rounds": self.pdu_data_to_be_preserved.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_preserved.rounds_names,
                    },
                },
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field Updated",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 3,
                        "rounds_names": [
                            "Round 1 Updated",
                            "Round 2 Updated",
                            "Round 3 Updated",
                        ],
                    },
                },
                {
                    "label": "PDU Field Updated",  # Duplicate label
                    "pdu_data": {
                        "subtype": PeriodicFieldData.STRING,
                        "number_of_rounds": 2,
                        "rounds_names": ["Round 1 New", "Round 2 New"],
                    },
                },
            ],
        }
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 3
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Time Series Field names must be unique." in response.json()
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 3

        # Check that the fields are not updated
        self.pdu_field_to_be_updated.refresh_from_db()
        assert self.pdu_field_to_be_updated.label["English(EN)"] == "PDU Field To Be Updated"
        self.pdu_field_to_be_removed.refresh_from_db()
        assert self.pdu_field_to_be_removed.is_removed is False
        assert FlexibleAttribute.objects.filter(program=self.program, name="new_pdu_field").exists() is False

    def test_update_pdu_fields_add_field_with_same_field_name_in_different_program(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        # pdu data with NEW field with name that already exists in the database but in different program -> no fail
        program2 = ProgramFactory(name="TestProgram2", business_area=self.afghanistan)
        pdu_data_existing = PeriodicFieldDataFactory()
        FlexibleAttributeForPDUFactory(
            program=program2,
            label="PDU Field Existing",
            pdu_data=pdu_data_existing,
        )

        payload = {
            **self.base_payload_for_update_without_changes,
            "pdu_fields": [
                {
                    "id": str(self.pdu_field_to_be_preserved.id),
                    "label": "PDU Field To Be Preserved",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_preserved.subtype,
                        "number_of_rounds": self.pdu_data_to_be_preserved.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_preserved.rounds_names,
                    },
                },
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field Updated",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 3,
                        "rounds_names": [
                            "Round 1 Updated",
                            "Round 2 Updated",
                            "Round 3 Updated",
                        ],
                    },
                },
                {
                    "label": "PDU Field Existing",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.STRING,
                        "number_of_rounds": 2,
                        "rounds_names": ["Round 1 New", "Round 2 New"],
                    },
                },
            ],
        }
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 3  # Initial count of PDU fields
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_200_OK
        assert (
            FlexibleAttribute.objects.filter(program=self.program).count() == 3
        )  # After update, one field is removed, one is updated, and one new is added

        self.pdu_field_to_be_updated.refresh_from_db()
        assert self.pdu_field_to_be_updated.label["English(EN)"] == "PDU Field Updated"
        assert self.pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.BOOL
        assert self.pdu_field_to_be_updated.pdu_data.number_of_rounds == 3
        assert self.pdu_field_to_be_updated.pdu_data.rounds_names == [
            "Round 1 Updated",
            "Round 2 Updated",
            "Round 3 Updated",
        ]
        self.pdu_field_to_be_removed.refresh_from_db()
        assert self.pdu_field_to_be_removed.is_removed is True
        new_pdu_field = FlexibleAttribute.objects.filter(program=self.program, name="pdu_field_existing").first()
        assert FlexibleAttribute.objects.filter(name="pdu_field_existing").count() == 2

        assert new_pdu_field.label["English(EN)"] == "PDU Field Existing"
        assert new_pdu_field.pdu_data.subtype == PeriodicFieldData.STRING
        assert new_pdu_field.pdu_data.number_of_rounds == 2
        assert new_pdu_field.pdu_data.rounds_names == ["Round 1 New", "Round 2 New"]

        self.program.refresh_from_db()
        assert response.json() == {
            **self.base_expected_response_without_changes,
            "pdu_fields": [
                {
                    "id": str(new_pdu_field.id),
                    "label": "PDU Field Existing",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.STRING,
                        "number_of_rounds": 2,
                        "rounds_names": ["Round 1 New", "Round 2 New"],
                        "rounds_covered": 0,
                    },
                    "name": new_pdu_field.name,
                },
                {
                    "id": str(self.pdu_field_to_be_preserved.id),
                    "label": "PDU Field To Be Preserved",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_preserved.subtype,
                        "number_of_rounds": self.pdu_data_to_be_preserved.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_preserved.rounds_names,
                        "rounds_covered": self.pdu_data_to_be_preserved.rounds_covered,
                    },
                    "name": self.pdu_field_to_be_preserved.name,
                },
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field Updated",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 3,
                        "rounds_names": [
                            "Round 1 Updated",
                            "Round 2 Updated",
                            "Round 3 Updated",
                        ],
                        "rounds_covered": self.pdu_data_to_be_updated.rounds_covered,
                    },
                    "name": self.pdu_field_to_be_updated.name,
                },
            ],
            "version": self.program.version,
        }

    def test_update_pdu_fields_with_same_name_in_different_program(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        # pdu data with NEW field with name that already exists in the database but in different program -> no fail
        program2 = ProgramFactory(name="TestProgram2", business_area=self.afghanistan)
        pdu_data_existing = PeriodicFieldDataFactory()
        FlexibleAttributeForPDUFactory(
            program=program2,
            label="PDU Field Existing",
            pdu_data=pdu_data_existing,
        )

        payload = {
            **self.base_payload_for_update_without_changes,
            "pdu_fields": [
                {
                    "id": str(self.pdu_field_to_be_preserved.id),
                    "label": "PDU Field To Be Preserved",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_preserved.subtype,
                        "number_of_rounds": self.pdu_data_to_be_preserved.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_preserved.rounds_names,
                        "rounds_covered": self.pdu_data_to_be_preserved.rounds_covered,
                    },
                },
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field Existing",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 3,
                        "rounds_names": [
                            "Round 1 Updated",
                            "Round 2 Updated",
                            "Round 3 Updated",
                        ],
                        "rounds_covered": self.pdu_data_to_be_updated.rounds_covered,
                    },
                },
            ],
        }
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 3  # Initial count of PDU fields
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_200_OK
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 2  # After update, one field is removed

        self.pdu_field_to_be_updated.refresh_from_db()
        assert self.pdu_field_to_be_updated.label["English(EN)"] == "PDU Field Existing"
        assert self.pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.BOOL
        assert self.pdu_field_to_be_updated.pdu_data.number_of_rounds == 3
        assert self.pdu_field_to_be_updated.pdu_data.rounds_names == [
            "Round 1 Updated",
            "Round 2 Updated",
            "Round 3 Updated",
        ]
        self.pdu_field_to_be_removed.refresh_from_db()
        assert self.pdu_field_to_be_removed.is_removed is True

        self.program.refresh_from_db()
        assert response.json() == {
            **self.base_expected_response_without_changes,
            "pdu_fields": [
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field Existing",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 3,
                        "rounds_names": [
                            "Round 1 Updated",
                            "Round 2 Updated",
                            "Round 3 Updated",
                        ],
                        "rounds_covered": self.pdu_data_to_be_updated.rounds_covered,
                    },
                    "name": self.pdu_field_to_be_updated.name,
                },
                {
                    "id": str(self.pdu_field_to_be_preserved.id),
                    "label": "PDU Field To Be Preserved",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_preserved.subtype,
                        "number_of_rounds": self.pdu_data_to_be_preserved.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_preserved.rounds_names,
                        "rounds_covered": self.pdu_data_to_be_preserved.rounds_covered,
                    },
                    "name": self.pdu_field_to_be_preserved.name,
                },
            ],
            "version": self.program.version,
        }

    def test_update_pdu_fields_when_program_has_rdi(self, create_user_role_with_permissions: Callable) -> None:
        # if program has RDI, it is not possible to remove or add PDU fields or update existing PDU fields -
        # only possible to increase number of rounds and add names for new rounds
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        RegistrationDataImportFactory(program=self.program, business_area=self.afghanistan)

        payload = {
            **self.base_payload_for_update_without_changes,
            "pdu_fields": [
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field - NAME WILL NOT BE UPDATED",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,  # subtype will NOT be updated
                        "number_of_rounds": 4,  # number of rounds will be increased
                        "rounds_names": [
                            "Round 1 To Be Updated",
                            "Round 2 To Be Updated",
                            "Round 3 New",
                            "Round 4 New",
                        ],  # can only add new rounds, cannot change existing names
                    },
                },
                {
                    "label": "New PDU Field",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.STRING,
                        "number_of_rounds": 2,
                        "rounds_names": ["Round 1 New", "Round 2 New"],
                    },
                },
            ],
        }
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 3
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_200_OK
        assert (
            FlexibleAttribute.objects.filter(program=self.program).count() == 3
        )  # no field can be removed or added for program with RDI

        self.pdu_field_to_be_updated.refresh_from_db()
        assert self.pdu_field_to_be_updated.label["English(EN)"] == "PDU Field To Be Updated"  # not updated
        assert self.pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.STRING  # not updated
        assert self.pdu_field_to_be_updated.pdu_data.number_of_rounds == 4  # updated
        assert self.pdu_field_to_be_updated.pdu_data.rounds_names == [
            "Round 1 To Be Updated",
            "Round 2 To Be Updated",
            "Round 3 New",
            "Round 4 New",
        ]  # updated
        self.pdu_field_to_be_removed.refresh_from_db()
        assert self.pdu_field_to_be_removed.is_removed is False  # not removed
        assert (
            FlexibleAttribute.objects.filter(program=self.program, name="new_pdu_field").exists() is False
        )  # new field not added

        self.program.refresh_from_db()
        assert response.json() == {
            **self.base_expected_response_without_changes,
            "pdu_fields": [
                {
                    "id": str(self.pdu_field_to_be_preserved.id),
                    "label": "PDU Field To Be Preserved",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_preserved.subtype,
                        "number_of_rounds": self.pdu_data_to_be_preserved.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_preserved.rounds_names,
                        "rounds_covered": self.pdu_data_to_be_preserved.rounds_covered,
                    },
                    "name": self.pdu_field_to_be_preserved.name,
                },
                {
                    "id": str(self.pdu_field_to_be_removed.id),
                    "label": "PDU Field To Be Removed",
                    "pdu_data": {
                        "subtype": self.pdu_data_to_be_removed.subtype,
                        "number_of_rounds": self.pdu_data_to_be_removed.number_of_rounds,
                        "rounds_names": self.pdu_data_to_be_removed.rounds_names,
                        "rounds_covered": self.pdu_data_to_be_removed.rounds_covered,
                    },
                    "name": self.pdu_field_to_be_removed.name,
                },
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field To Be Updated",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.STRING,
                        "number_of_rounds": 4,
                        "rounds_names": [
                            "Round 1 To Be Updated",
                            "Round 2 To Be Updated",
                            "Round 3 New",
                            "Round 4 New",
                        ],
                        "rounds_covered": self.pdu_data_to_be_updated.rounds_covered,
                    },
                    "name": self.pdu_field_to_be_updated.name,
                },
            ],
            "version": self.program.version,
        }

    def test_update_pdu_fields_invalid_when_program_has_rdi_decrease_rounds(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        # round number CANNOT be decreased for Program with RDI
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        RegistrationDataImportFactory(program=self.program, business_area=self.afghanistan)

        payload = {
            **self.base_payload_for_update_without_changes,
            "pdu_fields": [
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field - NAME WILL NOT BE UPDATED",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,  # subtype will NOT be updated
                        "number_of_rounds": 1,  # number of rounds will NOT be decreased
                        "rounds_names": ["Round 1 To Be Updated"],
                    },
                },
            ],
        }
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 3
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "It is not possible to decrease the number of rounds for a Program with RDI or TP." in response.json()
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 3

        # Check that the fields are not updated
        self.pdu_field_to_be_updated.refresh_from_db()
        assert self.pdu_field_to_be_updated.label["English(EN)"] == "PDU Field To Be Updated"
        assert self.pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.STRING
        assert self.pdu_field_to_be_updated.pdu_data.number_of_rounds == 2
        assert self.pdu_field_to_be_updated.pdu_data.rounds_names == [
            "Round 1 To Be Updated",
            "Round 2 To Be Updated",
        ]
        self.pdu_field_to_be_removed.refresh_from_db()
        assert self.pdu_field_to_be_removed.is_removed is False

    def test_update_pdu_fields_invalid_when_program_has_rdi_change_rounds_names(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        # names for existing rounds cannot be changed for Program with RDI
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        RegistrationDataImportFactory(program=self.program, business_area=self.afghanistan)

        payload = {
            **self.base_payload_for_update_without_changes,
            "pdu_fields": [
                {
                    "id": str(self.pdu_field_to_be_updated.id),
                    "label": "PDU Field - NAME WILL NOT BE UPDATED",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,  # subtype will NOT be updated
                        "number_of_rounds": 3,
                        "rounds_names": [
                            "Round 1 Updated",
                            "Round 2 Updated",
                            "Round 3 Updated",
                        ],  # cannot change existing names
                    },
                },
            ],
        }
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 3
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "It is not possible to change the names of existing rounds for a Program with RDI or TP." in response.json()
        )
        assert FlexibleAttribute.objects.filter(program=self.program).count() == 3

        # Check that the fields are not updated
        self.pdu_field_to_be_updated.refresh_from_db()
        assert self.pdu_field_to_be_updated.label["English(EN)"] == "PDU Field To Be Updated"
        assert self.pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.STRING
        assert self.pdu_field_to_be_updated.pdu_data.number_of_rounds == 2
        assert self.pdu_field_to_be_updated.pdu_data.rounds_names == [
            "Round 1 To Be Updated",
            "Round 2 To Be Updated",
        ]
        self.pdu_field_to_be_removed.refresh_from_db()
        assert self.pdu_field_to_be_removed.is_removed is False
