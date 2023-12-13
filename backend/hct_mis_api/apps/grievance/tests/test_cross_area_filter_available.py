from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
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

    def test_cross_area_filter_available_for_unicef_partner(self) -> None:
        partner_unicef = PartnerFactory(name="UNICEF")
        partner_unicef.permissions = {}
        user = UserFactory(partner=partner_unicef)

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
        partner_without_area_restrictions = PartnerFactory(name="Partner without area restrictions")
        partner_without_area_restrictions.permissions = {
            str(self.business_area.id): {"programs": {str(self.program.id): []}}
        }
        user = UserFactory(partner=partner_without_area_restrictions)

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

    def test_cross_area_filter_not_available(self) -> None:
        partner_with_area_restrictions = PartnerFactory(name="Partner with area restrictions")
        partner_with_area_restrictions.permissions = {
            str(self.business_area.id): {"programs": {str(self.program.id): [str(self.area.id)]}}
        }
        user = UserFactory(partner=partner_with_area_restrictions)

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
