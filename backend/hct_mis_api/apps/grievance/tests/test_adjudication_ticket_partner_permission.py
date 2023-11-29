from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
)


class TestAdjudicationTicketPartnerPermission(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = BusinessAreaFactory(slug="afghanistan")
        cls.grievance = GrievanceTicketFactory()
        cls.ticket_details = TicketNeedsAdjudicationDetailsFactory(ticket=cls.grievance)

    def test_select_individual_when_partner_is_unicef(self) -> None:
        pass

    def test_close_ticket_when_partner_is_unicef(self) -> None:
        pass

    def test_select_individual_when_partner_with_permission(self) -> None:
        pass

    def test_close_ticket_when_partner_with_permission(self) -> None:
        pass

    def test_select_individual_when_partner_does_not_have_permission(self) -> None:
        pass

    def test_close_ticket_when_partner_does_not_have_permission(self) -> None:
        pass
