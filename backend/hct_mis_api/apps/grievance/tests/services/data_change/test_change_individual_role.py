from django.test import TestCase

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.core.base_test_case import BaseElasticSearchTestCase
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketIndividualDataUpdateDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.services.data_change.individual_data_update_service import (
    IndividualDataUpdateService,
)
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import (
    ROLE_NO_ROLE,
    ROLE_PRIMARY,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestChangeIndividualRole(BaseElasticSearchTestCase, TestCase):
    databases = {"default", "registration_datahub"}

    @classmethod
    def setUpTestData(cls) -> None:
        business_area = BusinessAreaFactory()
        program = ProgramFactory()

        household = HouseholdFactory.build(business_area=business_area, program=program)
        household.household_collection.save()
        household.registration_data_import.imported_by.save()
        household.registration_data_import.program = household.program
        household.registration_data_import.save()

        individual = IndividualFactory(household=household, business_area=business_area, program=program)
        household.head_of_household = individual
        household.save()
        IndividualRoleInHousehold.objects.create(
            role=ROLE_PRIMARY,
            individual=individual,
            household=household,
        )

        cls.individual = IndividualFactory(household=household, business_area=business_area, program=program)

        cls.ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            business_area=business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )

        TicketIndividualDataUpdateDetailsFactory(
            ticket=cls.ticket,
            individual=cls.individual,
            individual_data={"role": {"value": ROLE_PRIMARY, "approve_status": True}},
        )
        super().setUpTestData()

    def test_change_role_from_none_to_alternate(self) -> None:
        IndividualRoleInHousehold.objects.create(
            role=ROLE_NO_ROLE,
            individual=self.individual,
            household=self.individual.household,
        )

        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
        service.close(UserFactory())

        role = IndividualRoleInHousehold.objects.get(household=self.individual.household, individual=self.individual)
        self.assertEqual(role.role, ROLE_PRIMARY)

    def test_change_role_to_alternate(self) -> None:
        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
        service.close(UserFactory())

        role = IndividualRoleInHousehold.objects.get(household=self.individual.household, individual=self.individual)
        self.assertEqual(role.role, ROLE_PRIMARY)
