from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.grievance.fixtures import TicketHouseholdDataUpdateDetailsFactory
from hct_mis_api.apps.grievance.services.data_change.household_data_update_service import (
    HouseholdDataUpdateService,
)
from hct_mis_api.apps.household.fixtures import create_household


class TestHouseholdDataUpdateService(TestCase):
    databases = {"default"}

    def test_propagate_admin_areas_on_close_ticket(self) -> None:
        # Given
        create_afghanistan()
        household, _ = create_household()
        ticket_details = TicketHouseholdDataUpdateDetailsFactory(
            household=household,
            household_data={
                "admin_area_title": {
                    "value": "AF010101",
                    "approve_status": True,
                }
            },
        )
        ticket = ticket_details.ticket
        ticket.save()

        country = CountryFactory()
        admin_type_1 = AreaTypeFactory(country=country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
        admin_type_3 = AreaTypeFactory(country=country, area_level=3, parent=admin_type_2)

        area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
        area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
        AreaFactory(parent=area2, p_code="AF010101", area_type=admin_type_3)

        service = HouseholdDataUpdateService(ticket, {})

        # When
        service.close(UserFactory())
        household.refresh_from_db()

        # Then
        self.assertEqual(household.admin_area.p_code, "AF010101")
        self.assertEqual(household.admin1.p_code, "AF01")
        self.assertEqual(household.admin2.p_code, "AF0101")
        self.assertEqual(household.admin3.p_code, "AF010101")
