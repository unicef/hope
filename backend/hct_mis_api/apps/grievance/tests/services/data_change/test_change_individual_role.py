from django.core.exceptions import ValidationError
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
    ROLE_ALTERNATE,
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
        household.registration_data_import.save()

        cls.individual_hoh = IndividualFactory(household=household, business_area=business_area, program=program)
        household.head_of_household = cls.individual_hoh
        household.save()
        IndividualRoleInHousehold.objects.create(
            role=ROLE_PRIMARY,
            individual=cls.individual_hoh,
            household=household,
        )

        cls.individual = IndividualFactory(household=household, business_area=business_area, program=program)

        cls.ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            business_area=business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        super().setUpTestData()

    def test_change_role_from_none_to_alternate(self) -> None:
        IndividualRoleInHousehold.objects.create(
            role=ROLE_NO_ROLE,
            individual=self.individual,
            household=self.individual.household,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.ticket,
            individual=self.individual,
            individual_data={"role": {"value": ROLE_ALTERNATE, "approve_status": True}},
        )

        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
        service.close(UserFactory())

        role = IndividualRoleInHousehold.objects.get(household=self.individual.household, individual=self.individual)
        self.assertEqual(role.role, ROLE_ALTERNATE)

    def test_change_role_to_alternate(self) -> None:
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.ticket,
            individual=self.individual,
            individual_data={"role": {"value": ROLE_ALTERNATE, "approve_status": True}},
        )
        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
        service.close(UserFactory())

        role = IndividualRoleInHousehold.objects.get(household=self.individual.household, individual=self.individual)
        self.assertEqual(role.role, ROLE_ALTERNATE)

    def test_change_role_from_alternate_to_none(self) -> None:
        IndividualRoleInHousehold.objects.create(
            role=ROLE_ALTERNATE,
            individual=self.individual,
            household=self.individual.household,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.ticket,
            individual=self.individual,
            individual_data={"role": {"value": ROLE_NO_ROLE, "approve_status": True}},
        )

        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
        service.close(UserFactory())

        role = IndividualRoleInHousehold.objects.filter(
            household=self.individual.household, individual=self.individual
        ).first()
        self.assertIsNone(role)

    def test_change_role_from_none_to_primary(self) -> None:
        IndividualRoleInHousehold.objects.create(
            role=ROLE_NO_ROLE,
            individual=self.individual,
            household=self.individual.household,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.ticket,
            individual=self.individual,
            individual_data={"role": {"value": ROLE_PRIMARY, "approve_status": True}},
        )

        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
        service.close(UserFactory())

        role = IndividualRoleInHousehold.objects.get(household=self.individual.household, individual=self.individual)
        self.assertEqual(role.role, ROLE_PRIMARY)

        previous_role = IndividualRoleInHousehold.objects.filter(
            household=self.individual.household, individual=self.individual_hoh
        ).first()
        self.assertIsNone(previous_role)  # previous primary collector does not have a role anymore

    def test_change_role_to_primary(self) -> None:
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.ticket,
            individual=self.individual,
            individual_data={"role": {"value": ROLE_PRIMARY, "approve_status": True}},
        )

        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
        service.close(UserFactory())

        role = IndividualRoleInHousehold.objects.get(household=self.individual.household, individual=self.individual)
        self.assertEqual(role.role, ROLE_PRIMARY)

        previous_role = IndividualRoleInHousehold.objects.filter(
            household=self.individual.household, individual=self.individual_hoh
        ).first()
        self.assertIsNone(previous_role)  # previous primary collector does not have a role anymore

    def test_change_role_from_alternate_to_primary(self) -> None:
        IndividualRoleInHousehold.objects.create(
            role=ROLE_ALTERNATE,
            individual=self.individual,
            household=self.individual.household,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.ticket,
            individual=self.individual,
            individual_data={"role": {"value": ROLE_PRIMARY, "approve_status": True}},
        )

        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
        service.close(UserFactory())

        role = IndividualRoleInHousehold.objects.get(household=self.individual.household, individual=self.individual)
        self.assertEqual(role.role, ROLE_PRIMARY)

        previous_role = IndividualRoleInHousehold.objects.filter(
            household=self.individual.household, individual=self.individual_hoh
        ).first()
        self.assertIsNone(previous_role)

    def test_change_role_from_primary_to_alternate(self) -> None:
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.ticket,
            individual=self.individual_hoh,
            individual_data={"role": {"value": ROLE_ALTERNATE, "approve_status": True}},
        )
        with self.assertRaises(ValidationError) as e:
            service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
            service.close(UserFactory())
        self.assertEqual(
            e.exception.messages[0], "Ticket cannot be closed, primary collector role has to be reassigned"
        )

        role = IndividualRoleInHousehold.objects.get(
            household=self.individual.household, individual=self.individual_hoh
        )
        self.assertEqual(role.role, ROLE_PRIMARY)  # still with primary role

    def test_change_role_from_primary_to_none(self) -> None:
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.ticket,
            individual=self.individual_hoh,
            individual_data={"role": {"value": ROLE_NO_ROLE, "approve_status": True}},
        )
        with self.assertRaises(ValidationError) as e:
            service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
            service.close(UserFactory())
        self.assertEqual(
            e.exception.messages[0], "Ticket cannot be closed, primary collector role has to be reassigned"
        )

        role = IndividualRoleInHousehold.objects.get(
            household=self.individual.household, individual=self.individual_hoh
        )
        self.assertEqual(role.role, ROLE_PRIMARY)  # still with primary role
