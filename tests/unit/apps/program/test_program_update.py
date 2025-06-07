from typing import Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
import copy

from hct_mis_api.apps.account.fixtures import (
    UserFactory,
    PartnerFactory,
    RoleAssignmentFactory, RoleFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import (
    DataCollectingTypeFactory,
    create_afghanistan,
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory, create_ukraine,
)
from hct_mis_api.apps.core.models import DataCollectingType, FlexibleAttribute, PeriodicFieldData
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.fixtures import (
    ProgramFactory,
    BeneficiaryGroupFactory,
    ProgramCycleFactory,
)
from hct_mis_api.apps.program.models import Program, BeneficiaryGroup, ProgramCycle
from hct_mis_api.apps.household.fixtures import HouseholdFactory, create_household_and_individuals
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from tests.selenium.conftest import business_area

pytestmark = pytest.mark.django_db


class TestProgramUpdate:
    @pytest.fixture(autouse=True)
    def setup(self, api_client, create_user_role_with_permissions) -> None:
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
        self.dct_social = DataCollectingTypeFactory(label="SW Full", code="sw_full", type=DataCollectingType.Type.SOCIAL)

        self.bg_household = BeneficiaryGroupFactory(name="Household", master_detail=True)
        self.bg_sw= BeneficiaryGroupFactory(name="Social Worker", master_detail=False)


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
            role=role_with_all_permissions
        )

        self.update_url = reverse(
            "api:programs:programs-detail",
            kwargs={"business_area_slug": self.afghanistan.slug, "slug": self.program.slug},
        )
        
        # pdu fields
        self.pdu_data_to_be_removed = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=3,
            rounds_names=["Round 1 To Be Removed", "Round 2 To Be Removed", "Round 3 To Be Removed"],
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
                } for pdu_field_data, pdu_field in zip(self.base_payload_for_update_without_changes["pdu_fields"], [self.pdu_field_to_be_preserved, self.pdu_field_to_be_removed, self.pdu_field_to_be_updated])
            ],
            "partners": [
                {
                    "id": self.partner.id,
                    "name": self.partner.name,
                    "areas": [
                        {
                            "id": str(self.area1.id),
                            "level": self.area1.level,
                        },
                        {
                            "id": str(self.area2.id),
                            "level": self.area2.level,
                        },
                    ],
                    "area_access": "BUSINESS_AREA",
                },
                {
                    "id": self.unicef_hq.id,
                    "name": self.unicef_hq.name,
                    "areas": [
                        {
                            "id": str(self.area1.id),
                            "level": self.area1.level,
                        },
                        {
                            "id": str(self.area2.id),
                            "level": self.area2.level,
                        },
                    ],
                    "area_access": "BUSINESS_AREA",
                },
                {
                    "id": self.unicef_partner_in_afghanistan.id,
                    "name": self.unicef_partner_in_afghanistan.name,
                    "areas": [
                        {
                            "id": str(self.area1.id),
                            "level": self.area1.level,
                        },
                        {
                            "id": str(self.area2.id),
                            "level": self.area2.level,
                        },
                    ],
                    "area_access": "BUSINESS_AREA",
                },
            ],
        }


    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PROGRAMME_UPDATE], status.HTTP_200_OK),
            ([Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], status.HTTP_403_FORBIDDEN),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_update_program_permissions(self, permissions: list, expected_status: int, create_user_role_with_permissions: Callable) -> None:
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
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.afghanistan, whole_business_area_access=True)

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
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.afghanistan, whole_business_area_access=True)

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
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.afghanistan, whole_business_area_access=True)

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
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.afghanistan, whole_business_area_access=True)

        payload = {
            **self.base_payload_for_update_without_changes,
            "programme_code":" T#ST",
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "programme_code" in response.json()
        assert "Programme code should be exactly 4 characters long and may only contain letters, digits and character: -" in response.json()["programme_code"][0]

        self.program.refresh_from_db()
        assert self.program.programme_code == self.initial_program_data["programme_code"]

    def test_update_programme_code_existing(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.afghanistan, whole_business_area_access=True)
        ProgramFactory(programme_code="T3ST", business_area=self.afghanistan)

        payload = {
            **self.base_payload_for_update_without_changes,
            "programme_code":" T3ST",
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "programme_code" in response.json()
        assert response.json()["programme_code"][0] == "Programme code is already used."

        self.program.refresh_from_db()
        assert self.program.programme_code == self.initial_program_data["programme_code"]

    def test_update_data_collecting_type(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.afghanistan, whole_business_area_access=True)
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
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.afghanistan, whole_business_area_access=True)
        dct_invalid = DataCollectingTypeFactory(label="DCT_INVALID", code="dct_invalid", type=DataCollectingType.Type.STANDARD)
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
        assert response_for_inactive.json()["data_collecting_type"][0] == "Only active Data Collecting Type can be used in Program."
        self.program.refresh_from_db()
        assert self.program.data_collecting_type == self.dct_standard

        # DCT deprecated
        dct_invalid.active = True
        dct_invalid.deprecated = True
        dct_invalid.save()
        response_for_deprecated = self.client.put(self.update_url, payload)
        assert response_for_deprecated.status_code == status.HTTP_400_BAD_REQUEST
        assert "data_collecting_type" in response_for_deprecated.json()
        assert response_for_deprecated.json()["data_collecting_type"][0] == "Deprecated Data Collecting Type cannot be used in Program."
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
        assert response_for_limited.json()["data_collecting_type"][0] == "This Data Collecting Type is not available for this Business Area."
        self.program.refresh_from_db()
        assert self.program.data_collecting_type == self.dct_standard

    def test_update_data_collecting_type_for_active_program(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.afghanistan, whole_business_area_access=True)
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
        assert response.json()["data_collecting_type"][0] == "Data Collecting Type can be updated only for Draft Programs."
        self.program.refresh_from_db()
        assert self.program.data_collecting_type == self.dct_standard

    def test_update_data_collecting_type_for_program_with_population(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.afghanistan, whole_business_area_access=True)
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
        assert response.json()["data_collecting_type"][0] == "Data Collecting Type can be updated only for Program without any households."
        self.program.refresh_from_db()
        assert self.program.data_collecting_type == self.dct_standard

    def test_update_data_collecting_type_invalid_with_beneficiary_group(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.afghanistan, whole_business_area_access=True)
        payload = {
            **self.base_payload_for_update_without_changes,
            "data_collecting_type": self.dct_social.code,
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "beneficiary_group" in response.json()
        assert response.json()["beneficiary_group"][0] == "Selected combination of data collecting type and beneficiary group is invalid."

        self.program.refresh_from_db()
        assert self.program.data_collecting_type == self.dct_standard

    def test_update_beneficiary_group(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.afghanistan, whole_business_area_access=True)
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

    def test_update_beneficiary_group_invalid_with_data_collecting_type(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.afghanistan, whole_business_area_access=True)

        payload = {
            **self.base_payload_for_update_without_changes,
            "beneficiary_group": str(self.bg_sw.id),
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "beneficiary_group" in response.json()
        assert response.json()["beneficiary_group"][0] == "Selected combination of data collecting type and beneficiary group is invalid."

        self.program.refresh_from_db()
        assert self.program.beneficiary_group == self.bg_household

    def test_update_beneficiary_group_invalid_with_population(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_UPDATE], self.afghanistan, whole_business_area_access=True)
        bg_2 = BeneficiaryGroupFactory(name="Beneficiary Group 2", master_detail=True)

        RegistrationDataImportFactory(program=self.program, business_area=self.afghanistan)

        payload = {
            **self.base_payload_for_update_without_changes,
            "beneficiary_group": str(bg_2.id),
        }
        response = self.client.put(self.update_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "beneficiary_group" in response.json()
        assert response.json()["beneficiary_group"][0] == "Beneficiary Group cannot be updated if Program has population."

        self.program.refresh_from_db()
        assert self.program.beneficiary_group == self.bg_household
