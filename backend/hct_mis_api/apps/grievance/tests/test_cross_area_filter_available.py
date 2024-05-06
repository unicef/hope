from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

CROSS_AREA_FILTER_AVAILABLE_QUERY = """
    query GrievanceTicketAreaScope {
      crossAreaFilterAvailable
    }
"""


class TestCrossAreaFilterAvailable(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = BusinessAreaFactory()
        cls.program = ProgramFactory(business_area=cls.business_area, status=Program.ACTIVE)
        cls.area = AreaFactory()

        cls.partner_without_area_restrictions = PartnerFactory(name="Partner without area restrictions")
        cls.partner_without_area_restrictions.permissions = {
            str(cls.business_area.id): {"programs": {str(cls.program.id): []}}
        }
        cls.partner_without_area_restrictions.save()

        cls.partner_with_area_restrictions = PartnerFactory(name="Partner with area restrictions")
        cls.partner_with_area_restrictions.permissions = {
            str(cls.business_area.id): {"programs": {str(cls.program.id): [str(cls.area.id)]}}
        }
        cls.partner_with_area_restrictions.save()

        cls.partner_unicef = PartnerFactory(name="UNICEF")
        cls.partner_unicef.permissions = {}

    def test_cross_area_filter_available_for_unicef_partner(self) -> None:
        user = UserFactory(partner=self.partner_unicef)
        self.create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CROSS_AREA_FILTER], self.business_area)

        self.snapshot_graphql_request(
            request_string=CROSS_AREA_FILTER_AVAILABLE_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
        )

    def test_cross_area_filter_available(self) -> None:
        user = UserFactory(partner=self.partner_without_area_restrictions)
        self.create_user_role_with_permissions(
            user,
            [
                Permissions.GRIEVANCES_CROSS_AREA_FILTER,
            ],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=CROSS_AREA_FILTER_AVAILABLE_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
        )

    def test_cross_area_filter_not_available_no_permission(self) -> None:
        user = UserFactory(partner=self.partner_without_area_restrictions)

        self.snapshot_graphql_request(
            request_string=CROSS_AREA_FILTER_AVAILABLE_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
        )

    def test_cross_area_filter_not_available_area_restrictions(self) -> None:
        user = UserFactory(partner=self.partner_with_area_restrictions)
        self.create_user_role_with_permissions(
            user,
            [
                Permissions.GRIEVANCES_CROSS_AREA_FILTER,
            ],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=CROSS_AREA_FILTER_AVAILABLE_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
        )

    def test_cross_area_filter_not_available_no_permission_and_area_restrictions(self) -> None:
        user = UserFactory(partner=self.partner_with_area_restrictions)

        self.snapshot_graphql_request(
            request_string=CROSS_AREA_FILTER_AVAILABLE_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
        )
