from typing import Any

import pytest
from extras.test_utils.factories.account import (
    PartnerFactory,
    RoleAssignmentFactory,
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
from extras.test_utils.factories.program import BeneficiaryGroupFactory, ProgramFactory
from rest_framework import status
from rest_framework.reverse import reverse

from hope.apps.account.permissions import Permissions
from hope.apps.core.models import (
    DataCollectingType,
    FlexibleAttribute,
    PeriodicFieldData,
)
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db


class TestProgramCreate:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.list_url = reverse(
            "api:programs:programs-list",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )

        self.partner = PartnerFactory(name="TestPartner")
        self.partner2 = PartnerFactory(name="TestPartner2")
        self.unicef_partner = PartnerFactory(name="UNICEF")
        self.unicef_hq = PartnerFactory(name="UNICEF HQ", parent=self.unicef_partner)
        self.unicef_partner_in_afghanistan = PartnerFactory(
            name="UNICEF Partner for afghanistan", parent=self.unicef_partner
        )

        self.partner.allowed_business_areas.add(self.afghanistan)
        self.partner2.allowed_business_areas.add(self.afghanistan)

        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

        country = CountryFactory()
        country.business_areas.set([self.afghanistan])
        admin_type = AreaTypeFactory(country=country, area_level=1)
        self.area1 = AreaFactory(parent=None, area_type=admin_type, p_code="AF01", name="Area1")
        self.area2 = AreaFactory(parent=None, area_type=admin_type, p_code="AF02", name="Area2")

        self.dct_standard = DataCollectingTypeFactory(label="Full", code="full", type=DataCollectingType.Type.STANDARD)
        self.dct_social = DataCollectingTypeFactory(
            label="SW Full", code="sw_full", type=DataCollectingType.Type.SOCIAL
        )

        self.bg_household = BeneficiaryGroupFactory(name="Household", master_detail=True)
        self.bg_sw = BeneficiaryGroupFactory(name="Social Worker", master_detail=False)

        self.valid_input_data_standard = {
            "name": "Test Program",
            "programme_code": None,
            "start_date": "2030-01-01",
            "end_date": "2033-12-31",
            "sector": Program.CHILD_PROTECTION,
            "data_collecting_type": self.dct_standard.code,
            "beneficiary_group": str(self.bg_household.id),
            "budget": 1000000,
            "population_goal": 1000,
            "cash_plus": False,
            "frequency_of_payments": Program.REGULAR,
            "administrative_areas_of_implementation": "",
            "partner_access": Program.ALL_PARTNERS_ACCESS,
            "partners": [],
            "pdu_fields": [],
        }
        self.expected_response_standard = {
            **self.valid_input_data_standard,
            "description": "",
            "status": Program.DRAFT,
            "budget": "1000000.00",  # budget is formatted as a string
            "partners": [
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
        ("permissions", "expected_status"),
        [
            ([Permissions.PROGRAMME_CREATE], status.HTTP_201_CREATED),
            ([Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], status.HTTP_403_FORBIDDEN),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_program_permissions(
        self, permissions: list, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, whole_business_area_access=True)

        response = self.client.post(self.list_url, self.valid_input_data_standard)
        assert response.status_code == expected_status

        if expected_status == status.HTTP_201_CREATED:
            program = Program.objects.get(pk=response.json()["id"])
            expected_response = {
                **self.expected_response_standard,
                "id": str(program.id),
                "programme_code": program.programme_code,  # programme_code is auto-generated
                "slug": program.slug,  # slug is auto-generated
                "version": program.version,
            }
            assert response.json() == expected_response

    def test_create_program_with_programme_code(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        input_data_with_program_code = {
            **self.valid_input_data_standard,
            "programme_code": "T3st",
        }
        response = self.client.post(self.list_url, input_data_with_program_code)
        assert response.status_code == status.HTTP_201_CREATED
        program = Program.objects.get(pk=response.json()["id"])
        expected_response = {
            **self.expected_response_standard,
            "id": str(program.id),
            "programme_code": "T3ST",  # programme_code is uppercased
            "slug": "t3st",  # slug is a slugified version of program_code
            "version": program.version,
        }
        assert response.json() == expected_response

    def test_create_program_with_programme_code_invalid(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        input_data_with_program_code = {
            **self.valid_input_data_standard,
            "programme_code": "T#ST",  # Invalid program code
        }
        response = self.client.post(self.list_url, input_data_with_program_code)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "programme_code" in response.json()
        assert (
            "Programme code should be exactly 4 characters long and may only contain letters, digits and character: -"
            in response.json()["programme_code"][0]
        )

    def test_create_program_with_programme_code_existing(self, create_user_role_with_permissions: Any) -> None:
        ProgramFactory(programme_code="T3ST", business_area=self.afghanistan)
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        input_data_with_program_code = {
            **self.valid_input_data_standard,
            "programme_code": "T3st",
        }
        response = self.client.post(self.list_url, input_data_with_program_code)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "programme_code" in response.json()
        assert response.json()["programme_code"][0] == "Programme code is already used."

    def test_create_program_with_missing_data(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        missing_input_data = {
            **self.valid_input_data_standard,
        }
        missing_input_data.pop("name")
        response = self.client.post(
            self.list_url,
            missing_input_data,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.json()
        assert response.json()["name"][0] == "This field is required."

    def test_create_program_with_invalid_data_collecting_type(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        dct_invalid = DataCollectingTypeFactory(label="Invalid", code="invalid", type=DataCollectingType.Type.STANDARD)
        invalid_input_data = {
            **self.valid_input_data_standard,
            "data_collecting_type": dct_invalid.code,  # Using an inactive DCT
        }

        # DCT inactive
        dct_invalid.active = False
        dct_invalid.save()
        response_for_inactive = self.client.post(self.list_url, invalid_input_data)
        assert response_for_inactive.status_code == status.HTTP_400_BAD_REQUEST
        assert "data_collecting_type" in response_for_inactive.json()
        assert (
            response_for_inactive.json()["data_collecting_type"][0]
            == "Only active Data Collecting Type can be used in Program."
        )

        # DCT deprecated
        dct_invalid.active = True
        dct_invalid.deprecated = True
        dct_invalid.save()
        response_for_deprecated = self.client.post(self.list_url, invalid_input_data)
        assert response_for_deprecated.status_code == status.HTTP_400_BAD_REQUEST
        assert "data_collecting_type" in response_for_deprecated.json()
        assert (
            response_for_deprecated.json()["data_collecting_type"][0]
            == "Deprecated Data Collecting Type cannot be used in Program."
        )

        # DCT limited to another BA
        dct_invalid.deprecated = False
        dct_invalid.save()
        ukraine = create_ukraine()
        dct_invalid.limit_to.add(ukraine)
        response_for_limited = self.client.post(self.list_url, invalid_input_data)
        assert response_for_limited.status_code == status.HTTP_400_BAD_REQUEST
        assert "data_collecting_type" in response_for_limited.json()
        assert (
            response_for_limited.json()["data_collecting_type"][0]
            == "This Data Collecting Type is not available for this Business Area."
        )

        # DCT valid
        dct_invalid.limit_to.add(self.afghanistan)
        response_for_valid = self.client.post(self.list_url, invalid_input_data)
        assert response_for_valid.status_code == status.HTTP_201_CREATED

    def test_create_program_with_invalid_beneficiary_group(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        invalid_input_data = {
            **self.valid_input_data_standard,
            "beneficiary_group": str(self.bg_sw.id),  # Invalid DCT and BG combination
        }
        response = self.client.post(self.list_url, invalid_input_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "beneficiary_group" in response.json()
        assert (
            response.json()["beneficiary_group"][0]
            == "Selected combination of data collecting type and beneficiary group is invalid."
        )

    def test_create_program_with_invalid_dates(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        invalid_input_data = {
            **self.valid_input_data_standard,
            "start_date": "2033-01-01",  # Start date after end date
            "end_date": "2030-12-31",
        }
        response = self.client.post(self.list_url, invalid_input_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "end_date" in response.json()
        assert response.json()["end_date"][0] == "End date cannot be earlier than the start date."

    def test_create_program_without_end_date(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        invalid_input_data = {
            **self.valid_input_data_standard,
            "end_date": None,
        }
        response = self.client.post(self.list_url, invalid_input_data)
        assert response.status_code == status.HTTP_201_CREATED
        program = Program.objects.get(pk=response.json()["id"])
        expected_response = {
            **self.expected_response_standard,
            "id": str(program.id),
            "programme_code": program.programme_code,
            "slug": program.slug,
            "end_date": None,
            "version": program.version,
        }
        assert response.json() == expected_response

    def test_create_program_with_partners_data(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        input_data_with_partners_data = {
            **self.valid_input_data_standard,
            "partner_access": Program.SELECTED_PARTNERS_ACCESS,
            "partners": [
                {
                    "partner": str(self.partner.id),
                    "areas": [str(self.area1.id)],
                },
                {
                    "partner": str(self.partner2.id),
                    "areas": [],
                },
            ],
        }

        # TODO: the below code is needed due to the temporary solution on the partners access in program actions
        RoleAssignmentFactory(partner=self.partner, business_area=self.afghanistan, program=None)
        RoleAssignmentFactory(partner=self.partner2, business_area=self.afghanistan, program=None)
        # TODO: remove the above code when the partners access in program actions is implemented properly

        response = self.client.post(self.list_url, input_data_with_partners_data)
        assert response.status_code == status.HTTP_201_CREATED
        program = Program.objects.get(pk=response.json()["id"])
        assert response.json() == {
            **self.expected_response_standard,
            "id": str(program.id),
            "programme_code": program.programme_code,
            "slug": program.slug,
            "version": program.version,
            "partners": [
                {
                    "id": self.partner.id,
                    "name": self.partner.name,
                    "areas": [
                        {
                            "id": str(self.area1.id),
                            "level": self.area1.level,
                        },
                    ],
                    "area_access": "ADMIN_AREA",
                },
                {
                    "id": self.partner2.id,
                    "name": self.partner2.name,
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
                *self.expected_response_standard["partners"],
            ],
            "partner_access": Program.SELECTED_PARTNERS_ACCESS,
        }

    def test_create_program_with_invalid_partners_data(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        input_data_with_partners_data = {
            **self.valid_input_data_standard,
            "partner_access": Program.SELECTED_PARTNERS_ACCESS,
            "partners": [  # missing user's partner on the list
                {
                    "partner": str(self.partner2.id),
                    "areas": [],
                },
            ],
        }

        response = self.client.post(self.list_url, input_data_with_partners_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "partners" in response.json()
        assert response.json()["partners"][0] == "Please assign access to your partner before saving the Program."

    def test_create_program_with_invalid_partners_data_and_partner_access(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        input_data_with_partners_data = {
            **self.valid_input_data_standard,
            "partner_access": Program.ALL_PARTNERS_ACCESS,  # cannot specify partners_data with ALL_PARTNERS_ACCESS
            "partners": [
                {
                    "partner": str(self.partner.id),
                    "areas": [str(self.area1.id)],
                },
                {
                    "partner": str(self.partner2.id),
                    "areas": [],
                },
            ],
        }

        response = self.client.post(self.list_url, input_data_with_partners_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "partners" in response.json()
        assert response.json()["partners"][0] == "You cannot specify partners for the chosen access type."

    def test_create_program_with_pdu_fields(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        input_data_with_pdu_fields = {
            **self.valid_input_data_standard,
            "pdu_fields": [
                {
                    "label": "PDU Field 1",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.STRING,
                        "number_of_rounds": 3,
                        "rounds_names": ["Round 1", "", "Round 2"],
                    },
                },
                {
                    "label": "PDU Field 2",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 2,
                        "rounds_names": ["", ""],
                    },
                },
            ],
        }
        response = self.client.post(self.list_url, input_data_with_pdu_fields)
        assert response.status_code == status.HTTP_201_CREATED
        program = Program.objects.get(pk=response.json()["id"])
        assert FlexibleAttribute.objects.filter(type=FlexibleAttribute.PDU, program=program).count() == 2
        pdu_field_1 = FlexibleAttribute.objects.get(
            type=FlexibleAttribute.PDU,
            program=program,
            name="pdu_field_1",
        )
        pdu_field_2 = FlexibleAttribute.objects.get(
            type=FlexibleAttribute.PDU,
            program=program,
            name="pdu_field_2",
        )
        assert response.json() == {
            **self.expected_response_standard,
            "pdu_fields": [
                {
                    "id": str(pdu_field_1.id),
                    "label": "PDU Field 1",
                    "name": "pdu_field_1",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.STRING,
                        "number_of_rounds": 3,
                        "rounds_names": ["Round 1", "", "Round 2"],
                    },
                },
                {
                    "id": str(pdu_field_2.id),
                    "label": "PDU Field 2",
                    "name": "pdu_field_2",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 2,
                        "rounds_names": ["", ""],
                    },
                },
            ],
            "id": str(program.id),
            "programme_code": program.programme_code,
            "slug": program.slug,
            "version": program.version,
        }

    def test_create_program_with_invalid_pdu_fields(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        input_data_with_invalid_pdu_fields = {
            **self.valid_input_data_standard,
            "pdu_fields": [
                {
                    "label": "PDU Field 1",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.STRING,
                        "number_of_rounds": 2,
                        "rounds_names": [
                            "Round 1",
                            "",
                            "Round 2",
                        ],  # Number of rounds does not match rounds_names length
                    },
                },
                {
                    "label": "PDU Field 2",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 2,
                        "rounds_names": ["", ""],
                    },
                },
            ],
        }
        response = self.client.post(self.list_url, input_data_with_invalid_pdu_fields)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert FlexibleAttribute.objects.filter(type=FlexibleAttribute.PDU).count() == 0
        assert "Number of rounds does not match the number of round names." in response.json()

    def test_create_program_with_invalid_pdu_fields_duplicated_names(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        input_data_with_invalid_pdu_fields = {
            **self.valid_input_data_standard,
            "pdu_fields": [
                {
                    "label": "PDU Field 1",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.STRING,
                        "number_of_rounds": 3,
                        "rounds_names": ["Round 1", "", "Round 2"],
                    },
                },
                {
                    "label": "PDU Field 1",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 2,
                        "rounds_names": ["", ""],
                    },
                },
            ],
        }
        response = self.client.post(self.list_url, input_data_with_invalid_pdu_fields)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert FlexibleAttribute.objects.filter(type=FlexibleAttribute.PDU).count() == 0
        assert "Time Series Field names must be unique." in response.json()

    def test_create_program_with_valid_pdu_fields_existing_field_name_in_different_program(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_CREATE], self.afghanistan, whole_business_area_access=True
        )
        # pdu data with field name that already exists in the database but in different program -> no fail
        pdu_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DATE,
            number_of_rounds=1,
            rounds_names=["Round 1"],
        )
        program = ProgramFactory(business_area=self.afghanistan, name="Test Program 1")
        FlexibleAttributeForPDUFactory(
            program=program,
            label="PDU Field 1",
            pdu_data=pdu_data,
        )
        input_data_with_valid_pdu_fields = {
            **self.valid_input_data_standard,
            "pdu_fields": [
                {
                    "label": "PDU Field 1",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.STRING,
                        "number_of_rounds": 3,
                        "rounds_names": ["Round 1", "", "Round 2"],
                    },
                },
                {
                    "label": "PDU Field 2",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 2,
                        "rounds_names": ["", ""],
                    },
                },
            ],
        }
        response = self.client.post(self.list_url, input_data_with_valid_pdu_fields)
        assert response.status_code == status.HTTP_201_CREATED
        program = Program.objects.get(pk=response.json()["id"])
        assert FlexibleAttribute.objects.filter(type=FlexibleAttribute.PDU, program=program).count() == 2
        pdu_field_1 = FlexibleAttribute.objects.get(
            type=FlexibleAttribute.PDU,
            program=program,
            name="pdu_field_1",
        )
        pdu_field_2 = FlexibleAttribute.objects.get(
            type=FlexibleAttribute.PDU,
            program=program,
            name="pdu_field_2",
        )
        assert response.json() == {
            **self.expected_response_standard,
            "pdu_fields": [
                {
                    "id": str(pdu_field_1.id),
                    "label": "PDU Field 1",
                    "name": "pdu_field_1",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.STRING,
                        "number_of_rounds": 3,
                        "rounds_names": ["Round 1", "", "Round 2"],
                    },
                },
                {
                    "id": str(pdu_field_2.id),
                    "label": "PDU Field 2",
                    "name": "pdu_field_2",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 2,
                        "rounds_names": ["", ""],
                    },
                },
            ],
            "id": str(program.id),
            "programme_code": program.programme_code,
            "slug": program.slug,
            "version": program.version,
        }
