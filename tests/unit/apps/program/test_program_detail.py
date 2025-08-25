from typing import Any

import pytest
from extras.test_utils.factories.account import (
    AdminAreaLimitedToFactory,
    PartnerFactory,
    UserFactory,
)
from extras.test_utils.factories.core import (
    FlexibleAttributeForPDUFactory,
    create_afghanistan,
)
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from rest_framework import status
from rest_framework.reverse import reverse

from models.account import Partner
from hope.apps.account.permissions import Permissions
from hope.apps.payment.models import PaymentPlan
from models.program import Program

pytestmark = pytest.mark.django_db


class TestProgramDetail:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any, create_partner_role_with_permissions: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            partner_access=Program.SELECTED_PARTNERS_ACCESS,
        )
        self.detail_url_name = "api:programs:programs-detail"

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

        self.pdu_field1 = FlexibleAttributeForPDUFactory(program=self.program)
        self.pdu_field2 = FlexibleAttributeForPDUFactory(program=self.program)

        # partner with all area access
        self.partner_with_all_area_access = PartnerFactory(name="PartnerWithAllAreaAccess")
        create_partner_role_with_permissions(
            self.partner_with_all_area_access,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.afghanistan,
            self.program,
        )

        # partner with area limits
        self.partner_with_area_limits = PartnerFactory(name="PartnerWithAreaLimits")
        create_partner_role_with_permissions(
            self.partner_with_area_limits,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.afghanistan,
            self.program,
        )

        country = CountryFactory()
        country.business_areas.set([self.afghanistan])
        admin_type = AreaTypeFactory(country=country, area_level=1)
        self.area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type, name="Area1")
        self.area2 = AreaFactory(parent=None, p_code="AF0101", area_type=admin_type, name="Area2")

        admin_area_limits = AdminAreaLimitedToFactory(partner=self.partner_with_area_limits, program=self.program)
        admin_area_limits.areas.set([self.area1])

        # partner without access to program
        PartnerFactory(name="PartnerWithoutAccess")

        RegistrationDataImportFactory(program=self.program)

        program_cycle = ProgramCycleFactory(program=self.program)
        PaymentPlanFactory(program_cycle=program_cycle)

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_program_detail_permissions(
        self,
        permissions: list,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program)
        response = self.client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "slug": self.program.slug,
                },
            )
        )
        assert response.status_code == expected_status

    def test_program_detail(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.afghanistan,
            self.program,
        )

        response = self.client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "slug": self.program.slug,
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        partner_unicef_hq = Partner.objects.get(name="UNICEF HQ")
        partner_unicef_in_afg = Partner.objects.get(name="UNICEF Partner for afghanistan")

        assert response_data["id"] == str(self.program.id)
        assert response_data["version"] == self.program.version
        assert response_data["programme_code"] == self.program.programme_code
        assert response_data["slug"] == self.program.slug
        assert response_data["name"] == self.program.name
        assert response_data["start_date"] == self.program.start_date.strftime("%Y-%m-%d")
        assert response_data["end_date"] == self.program.end_date.strftime("%Y-%m-%d")
        assert response_data["budget"] == str(self.program.budget)
        assert response_data["frequency_of_payments"] == self.program.frequency_of_payments
        assert response_data["sector"] == self.program.sector
        assert response_data["cash_plus"] == self.program.cash_plus
        assert response_data["population_goal"] == self.program.population_goal
        assert response_data["screen_beneficiary"] == self.program.screen_beneficiary
        assert response_data["data_collecting_type"] == {
            "id": self.program.data_collecting_type.id,
            "label": self.program.data_collecting_type.label,
            "code": self.program.data_collecting_type.code,
            "type": self.program.data_collecting_type.type,
            "type_display": self.program.data_collecting_type.get_type_display(),
            "household_filters_available": self.program.data_collecting_type.household_filters_available,
            "individual_filters_available": self.program.data_collecting_type.individual_filters_available,
        }
        assert response_data["beneficiary_group"] == {
            "id": str(self.program.beneficiary_group.id),
            "name": self.program.beneficiary_group.name,
            "group_label": self.program.beneficiary_group.group_label,
            "group_label_plural": self.program.beneficiary_group.group_label_plural,
            "member_label": self.program.beneficiary_group.member_label,
            "member_label_plural": self.program.beneficiary_group.member_label_plural,
            "master_detail": self.program.beneficiary_group.master_detail,
        }
        assert response_data["status"] == self.program.status
        assert response_data["pdu_fields"] == [
            {
                "id": str(self.pdu_field1.id),
                "label": self.pdu_field1.label["English(EN)"],
                "name": self.pdu_field1.name,
                "pdu_data": {
                    "subtype": self.pdu_field1.pdu_data.subtype,
                    "number_of_rounds": self.pdu_field1.pdu_data.number_of_rounds,
                    "rounds_names": self.pdu_field1.pdu_data.rounds_names,
                },
            },
            {
                "id": str(self.pdu_field2.id),
                "label": self.pdu_field2.label["English(EN)"],
                "name": self.pdu_field2.name,
                "pdu_data": {
                    "subtype": self.pdu_field2.pdu_data.subtype,
                    "number_of_rounds": self.pdu_field2.pdu_data.number_of_rounds,
                    "rounds_names": self.pdu_field2.pdu_data.rounds_names,
                },
            },
        ]
        assert response_data["household_count"] == self.program.household_count

        assert response_data["description"] == self.program.description
        assert (
            response_data["administrative_areas_of_implementation"]
            == self.program.administrative_areas_of_implementation
        )
        assert response_data["version"] == self.program.version
        assert response_data["partners"] == [
            {
                "id": self.partner_with_all_area_access.id,
                "name": self.partner_with_all_area_access.name,
                "area_access": "BUSINESS_AREA",
                "areas": [
                    {
                        "id": str(self.area1.id),
                        "level": self.area1.area_type.level,
                    },
                    {
                        "id": str(self.area2.id),
                        "level": self.area2.area_type.level,
                    },
                ],
            },
            {
                "id": self.partner_with_area_limits.id,
                "name": self.partner_with_area_limits.name,
                "area_access": "ADMIN_AREA",
                "areas": [
                    {
                        "id": str(self.area1.id),
                        "level": self.area1.area_type.level,
                    }
                ],
            },
            {
                "id": partner_unicef_hq.id,
                "name": partner_unicef_hq.name,
                "area_access": "BUSINESS_AREA",
                "areas": [
                    {
                        "id": str(self.area1.id),
                        "level": self.area1.area_type.level,
                    },
                    {
                        "id": str(self.area2.id),
                        "level": self.area2.area_type.level,
                    },
                ],
            },
            {
                "id": partner_unicef_in_afg.id,
                "name": partner_unicef_in_afg.name,
                "area_access": "BUSINESS_AREA",
                "areas": [
                    {
                        "id": str(self.area1.id),
                        "level": self.area1.area_type.level,
                    },
                    {
                        "id": str(self.area2.id),
                        "level": self.area2.area_type.level,
                    },
                ],
            },
        ]
        assert response_data["partner_access"] == self.program.partner_access
        assert response_data["registration_imports_total_count"] == self.program.registration_imports.count()
        assert (
            response_data["target_populations_count"]
            == PaymentPlan.objects.filter(program_cycle__program=self.program).count()
        )
        assert response_data["population_goal"] == self.program.population_goal
