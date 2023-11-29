from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, PartnerFactory, UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestAdjudicationTicketPartnerPermission(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()

        cls.business_area = BusinessAreaFactory(slug="afghanistan")
        cls.program = ProgramFactory(business_area=cls.business_area)

        cls.grievance = GrievanceTicketFactory()
        cls.grievance.programs.add(cls.program)
        cls.ticket_details = TicketNeedsAdjudicationDetailsFactory(ticket=cls.grievance)

        cls.household_1, cls.individuals_2 = create_household(
            {"size": 1, "business_area": cls.business_area},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )

        cls.household_2, cls.individuals_2 = create_household(
            {"size": 1, "business_area": cls.business_area},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )

    def test_select_individual_when_partner_is_unicef(self) -> None:
        partner = PartnerFactory()

    def test_close_ticket_when_partner_is_unicef(self) -> None:
        partner = PartnerFactory()

    def test_select_individual_when_partner_with_permission(self) -> None:
        pass

    def test_close_ticket_when_partner_with_permission(self) -> None:
        pass

    def test_select_individual_when_partner_does_not_have_permission(self) -> None:
        pass

    def test_close_ticket_when_partner_does_not_have_permission(self) -> None:
        pass
