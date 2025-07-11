from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketHouseholdDataUpdateDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.services.data_change.household_data_update_service import (
    HouseholdDataUpdateService,
)
from hct_mis_api.apps.household.fixtures import IndividualFactory, create_household
from hct_mis_api.apps.household.models import ROLE_ALTERNATE, IndividualRoleInHousehold
from hct_mis_api.apps.utils.models import MergeStatusModel
from tests.unit.api.test_area import id_to_base64


class TestHouseholdDataUpdateService(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()

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

    def test_update_roles_new_create_ticket(self) -> None:
        individual = IndividualFactory()
        household = individual.household
        IndividualRoleInHousehold.objects.create(
            household=household,
            individual=individual,
            role=ROLE_ALTERNATE,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        grievance_ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            business_area=self.business_area,
        )
        hh_id_decoded = id_to_base64(str(household.id), "HouseholdNode")
        ind_id_decoded = id_to_base64(str(individual.id), "IndividualNode")
        extras = {
            "issue_type": {
                "household_data_update_issue_type_extras": {
                    "household": hh_id_decoded,
                    "household_data": {
                        "country": "AGO",
                        "flex_fields": {},
                        "roles": [{"individual": ind_id_decoded, "new_role": "PRIMARY"}],
                    },
                }
            }
        }
        service = HouseholdDataUpdateService(grievance_ticket=grievance_ticket, extras=extras)
        ticket = service.save()[0]
        details = ticket.ticket_details
        expected_dict = {
            "roles": [
                {
                    "value": "PRIMARY",
                    "individual_id": ind_id_decoded,
                    "approve_status": False,
                    "previous_value": "ALTERNATE",
                }
            ],
            "country": {"value": "AGO", "approve_status": False, "previous_value": None},
            "flex_fields": {},
        }

        self.assertEqual(details.household_data, expected_dict)

    def test_update_roles_new_update_ticket(self) -> None:
        pass

    def test_update_roles_new_approve_ticket(self) -> None:
        pass

    def test_update_roles_new_close_ticket(self) -> None:
        pass
