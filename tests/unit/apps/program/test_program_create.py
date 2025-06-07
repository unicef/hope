from typing import Any

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import (
    AdminAreaLimitedToFactory,
    PartnerFactory,
    UserFactory, RoleAssignmentFactory,
)
from hct_mis_api.apps.account.models import Partner, RoleAssignment
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import (
    FlexibleAttributeForPDUFactory,
    create_afghanistan, DataCollectingTypeFactory, create_ukraine, PeriodicFieldDataFactory,
)
from hct_mis_api.apps.core.models import DataCollectingType, PeriodicFieldData, FlexibleAttribute
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.fixtures import (
    ProgramCycleFactory,
    ProgramFactory, BeneficiaryGroupFactory,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory

pytestmark = pytest.mark.django_db

class TestProgramCreate:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any, create_partner_role_with_permissions: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.list_url = reverse(
            "api:programs:programs-list",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )

        self.partner = PartnerFactory(name="TestPartner")
        self.partner2 = PartnerFactory(name="TestPartner2")
        self.unicef_partner = PartnerFactory(name="UNICEF")
        self.unicef_hq = PartnerFactory(name="UNICEF HQ", parent=self.unicef_partner)
        self.unicef_partner_in_afghanistan = PartnerFactory(name="UNICEF Partner for afghanistan", parent=self.unicef_partner)

        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

        country = CountryFactory()
        country.business_areas.set([self.afghanistan])
        admin_type = AreaTypeFactory(country=country, area_level=1)
        self.area1 = AreaFactory(parent=None, area_type=admin_type, p_code="AF01", name="Area1")
        self.area2 = AreaFactory(parent=None, area_type=admin_type, p_code="AF02", name="Area2")

        self.dct_standard = DataCollectingTypeFactory(label="Full", code="full", type=DataCollectingType.Type.STANDARD)
        self.dct_social = DataCollectingTypeFactory(label="SW Full", code="sw_full", type=DataCollectingType.Type.SOCIAL)

        self.bg_household = BeneficiaryGroupFactory(name="Household", master_detail=True)
        self.bg_sw= BeneficiaryGroupFactory(name="Social Worker", master_detail=False)

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
            "partner_access": Program.ALL_PARTNERS_ACCESS,
            "partners": [],
            "pdu_fields": [],
        }
        self.expected_response_standard = {
            **self.valid_input_data_standard,
            "administrative_areas_of_implementation": "",
            "description": "",
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
        "permissions, expected_status",
        [
            ([Permissions.PROGRAMME_CREATE], status.HTTP_201_CREATED),
            ([Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], status.HTTP_403_FORBIDDEN),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_program_permissions(self, permissions: list, expected_status: int, create_user_role_with_permissions: Any) -> None:
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
            }
            assert response.json() == expected_response
