from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import (
    HouseholdFactory,
    IndividualFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.core.base_test_case import BaseTestCase
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketIndividualDataUpdateDetails,
)
from hope.one_time_scripts.clean_role_field_from_tickets import (
    clean_role_field_from_tickets,
)


class TestCleanRoleFieldFromTickets(BaseTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(name="Test program", business_area=cls.business_area)
        cls.user = UserFactory()

        cls.household = HouseholdFactory.build(program=cls.program)
        cls.household.household_collection.save()
        cls.household.registration_data_import.imported_by.save()
        cls.household.registration_data_import.program = cls.program
        cls.household.registration_data_import.save()
        cls.household.save()

        cls.individual = IndividualFactory(household=cls.household, program=cls.program)

    def test_clean_role_field_from_add_individual_ticket(self) -> None:
        """Test that role field is removed from Add Individual tickets"""
        ticket = GrievanceTicket.objects.create(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            status=GrievanceTicket.STATUS_NEW,
            created_by=self.user,
            assigned_to=self.user,
        )
        ticket.programs.set([self.program])

        individual_data_with_role = {
            "full_name": "Test Individual",
            "role": "PRIMARY",  # This should be removed
            "relationship": "HEAD",
        }

        ticket_details = TicketAddIndividualDetails.objects.create(
            ticket=ticket,
            household=self.household,
            individual_data=individual_data_with_role,
        )

        # Run the cleanup script
        clean_role_field_from_tickets()

        # Verify role field was removed
        ticket_details.refresh_from_db()
        assert "role" not in ticket_details.individual_data
        assert "full_name" in ticket_details.individual_data
        assert "relationship" in ticket_details.individual_data

    def test_clean_role_field_from_individual_data_update_ticket(self) -> None:
        """Test that role field is removed from Individual Data Update tickets"""
        ticket = GrievanceTicket.objects.create(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            status=GrievanceTicket.STATUS_IN_PROGRESS,
            created_by=self.user,
            assigned_to=self.user,
        )
        ticket.programs.set([self.program])

        individual_data_with_role = {
            "full_name": {"value": "Updated Name", "approve_status": False},
            "role": {"value": "ALTERNATE", "approve_status": False},  # This should be removed
        }

        ticket_details = TicketIndividualDataUpdateDetails.objects.create(
            ticket=ticket,
            individual=self.individual,
            individual_data=individual_data_with_role,
        )

        # Run the cleanup script
        clean_role_field_from_tickets()

        # Verify role field was removed
        ticket_details.refresh_from_db()
        assert "role" not in ticket_details.individual_data
        assert "full_name" in ticket_details.individual_data

    def test_clean_role_field_from_multiple_tickets(self) -> None:
        """Test cleaning role field from multiple tickets"""
        tickets_data = []

        for i in range(3):
            ticket = GrievanceTicket.objects.create(
                business_area=self.business_area,
                category=GrievanceTicket.CATEGORY_DATA_CHANGE,
                issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
                status=GrievanceTicket.STATUS_NEW,
                created_by=self.user,
                assigned_to=self.user,
            )
            ticket.programs.set([self.program])

            ticket_details = TicketAddIndividualDetails.objects.create(
                ticket=ticket,
                household=self.household,
                individual_data={"full_name": f"Test {i}", "role": "PRIMARY"},
            )
            tickets_data.append((ticket, ticket_details))

        for _i in range(2):
            ticket = GrievanceTicket.objects.create(
                business_area=self.business_area,
                category=GrievanceTicket.CATEGORY_DATA_CHANGE,
                issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
                status=GrievanceTicket.STATUS_NEW,
                created_by=self.user,
                assigned_to=self.user,
            )
            ticket.programs.set([self.program])

            ticket_details = TicketIndividualDataUpdateDetails.objects.create(
                ticket=ticket,
                individual=self.individual,
                individual_data={"role": {"value": "ALTERNATE", "approve_status": False}},
            )
            tickets_data.append((ticket, ticket_details))

        # Run the cleanup script
        clean_role_field_from_tickets()

        # Verify role field was removed from all tickets
        for _ticket, ticket_details in tickets_data:
            ticket_details.refresh_from_db()
            assert "role" not in ticket_details.individual_data

    def test_skip_closed_tickets(self) -> None:
        """Test that closed tickets are not processed"""
        ticket = GrievanceTicket.objects.create(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            status=GrievanceTicket.STATUS_CLOSED,  # Closed ticket
            created_by=self.user,
            assigned_to=self.user,
        )
        ticket.programs.set([self.program])

        ticket_details = TicketAddIndividualDetails.objects.create(
            ticket=ticket,
            household=self.household,
            individual_data={"full_name": "Test", "role": "PRIMARY"},
        )

        # Run the cleanup script
        clean_role_field_from_tickets()

        # Verify closed ticket was not processed
        ticket_details.refresh_from_db()
        assert "role" in ticket_details.individual_data  # Still present

    def test_skip_tickets_without_role_field(self) -> None:
        """Test that tickets without role field are not affected"""
        ticket = GrievanceTicket.objects.create(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            status=GrievanceTicket.STATUS_NEW,
            created_by=self.user,
            assigned_to=self.user,
        )
        ticket.programs.set([self.program])

        individual_data_without_role = {
            "full_name": "Test Individual",
            "relationship": "HEAD",
        }

        ticket_details = TicketAddIndividualDetails.objects.create(
            ticket=ticket,
            household=self.household,
            individual_data=individual_data_without_role,
        )

        # Run the cleanup script
        clean_role_field_from_tickets()

        # Verify ticket was not modified
        ticket_details.refresh_from_db()
        assert ticket_details.individual_data == individual_data_without_role
