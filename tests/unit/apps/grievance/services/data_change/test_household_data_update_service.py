from django.test import TestCase

from hope.apps.program.models import Program
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.models import IndividualRoleInHousehold, ROLE_ALTERNATE
from hope.apps.utils.models import MergeStatusModel
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.grievance import (
    TicketHouseholdDataUpdateDetailsFactory,
    GrievanceTicketFactory,
)
from extras.test_utils.factories.household import create_household, IndividualFactory

from hope.apps.grievance.services.data_change.household_data_update_service import (
    HouseholdDataUpdateService,
)


class TestHouseholdDataUpdateService(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(
            business_area=cls.business_area,
            status=Program.ACTIVE,
            name="program afghanistan 1",
        )
        cls.user = UserFactory()

    def test_propagate_admin_areas_on_close_ticket(self) -> None:
        # Given
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
        assert household.admin_area.p_code == "AF010101"
        assert household.admin1.p_code == "AF01"
        assert household.admin2.p_code == "AF0101"
        assert household.admin3.p_code == "AF010101"

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
        extras = {
            "issue_type": {
                "household_data_update_issue_type_extras": {
                    "household": household,
                    "household_data": {
                        "country": "AGO",
                        "flex_fields": {},
                        "roles": [{"individual": individual, "new_role": "PRIMARY"}],
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
                    "individual_id": str(individual.id),
                    "full_name": individual.full_name,
                    "unicef_id": individual.unicef_id,
                    "approve_status": False,
                    "previous_value": "ALTERNATE",
                }
            ],
            "country": {"value": "AGO", "approve_status": False, "previous_value": None},
            "flex_fields": {},
        }

        self.assertEqual(details.household_data, expected_dict)

    def test_update_roles_new_update_ticket_add_new_role(self) -> None:
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
        extras = {
            "issue_type": {
                "household_data_update_issue_type_extras": {
                    "household": household,
                    "household_data": {
                        "country": "AGO",
                        "flex_fields": {},
                        "roles": [],
                    },
                }
            }
        }
        # create ticket without Roles
        service = HouseholdDataUpdateService(grievance_ticket=grievance_ticket, extras=extras)
        ticket = service.save()[0]
        details = ticket.ticket_details
        expected_dict = {
            "country": {"value": "AGO", "approve_status": False, "previous_value": None},
            "flex_fields": {},
        }
        self.assertEqual(details.household_data, expected_dict)

        # update ticket details and add new Role
        extras = {
            "household_data_update_issue_type_extras": {
                "household": household,  # type: ignore
                "household_data": {
                    "country": "AGO",
                    "flex_fields": {},
                    "roles": [{"new_role": "ALTERNATE", "individual": individual}],  # type: ignore
                },
            }
        }
        service = HouseholdDataUpdateService(grievance_ticket=grievance_ticket, extras=extras)
        ticket = service.update()
        details = ticket.ticket_details
        expected_dict = {
            "roles": [
                {
                    "value": "ALTERNATE",
                    "individual_id": str(individual.id),
                    "full_name": individual.full_name,
                    "unicef_id": individual.unicef_id,
                    "approve_status": False,
                    "previous_value": "ALTERNATE",
                }
            ],
            "country": {"value": "AGO", "approve_status": False, "previous_value": None},
            "flex_fields": {},
        }
        self.assertEqual(details.household_data, expected_dict)

    def test_update_roles_new_update_ticket_update_role(self) -> None:
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
        extras = {
            "issue_type": {
                "household_data_update_issue_type_extras": {
                    "household": household,
                    "household_data": {
                        "country": "AGO",
                        "flex_fields": {},
                        "roles": [{"individual": individual, "new_role": "ALTERNATE"}],
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
                    "value": "ALTERNATE",
                    "individual_id": str(individual.id),
                    "full_name": individual.full_name,
                    "unicef_id": individual.unicef_id,
                    "approve_status": False,
                    "previous_value": "ALTERNATE",
                }
            ],
            "country": {"value": "AGO", "approve_status": False, "previous_value": None},
            "flex_fields": {},
        }
        self.assertEqual(details.household_data, expected_dict)

        # update Role to PRIMARY
        extras = {
            "household_data_update_issue_type_extras": {
                "household": household,  # type: ignore
                "household_data": {
                    "country": "AGO",
                    "flex_fields": {},
                    "roles": [{"new_role": "PRIMARY", "individual": individual}],  # type: ignore
                },
            }
        }
        service = HouseholdDataUpdateService(grievance_ticket=grievance_ticket, extras=extras)
        ticket = service.update()
        details = ticket.ticket_details
        expected_dict = {
            "roles": [
                {
                    "value": "PRIMARY",
                    "individual_id": str(individual.id),
                    "full_name": individual.full_name,
                    "unicef_id": individual.unicef_id,
                    "approve_status": False,
                    "previous_value": "ALTERNATE",
                }
            ],
            "country": {"value": "AGO", "approve_status": False, "previous_value": None},
            "flex_fields": {},
        }
        self.assertEqual(details.household_data, expected_dict)

    def test_update_roles_new_approve_ticket(self) -> None:
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
        extras = {
            "issue_type": {
                "household_data_update_issue_type_extras": {
                    "household": household,
                    "household_data": {
                        "country": "AGO",
                        "flex_fields": {},
                        "roles": [{"individual": individual, "new_role": "PRIMARY"}],
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
                    "individual_id": str(individual.id),
                    "full_name": individual.full_name,
                    "unicef_id": individual.unicef_id,
                    "approve_status": False,
                    "previous_value": "ALTERNATE",
                }
            ],
            "country": {"value": "AGO", "approve_status": False, "previous_value": None},
            "flex_fields": {},
        }
        self.assertEqual(details.household_data, expected_dict)

    def test_close_household_update_new_roles(self) -> None:
        first_individual = IndividualFactory(program=self.program)
        household = first_individual.household
        second_individual = IndividualFactory(program=self.program, household=household)
        # add ALTERNATE role for first_individual
        IndividualRoleInHousehold.objects.create(
            household=household,
            individual=first_individual,
            role=ROLE_ALTERNATE,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        household_data_change_grv_new = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        details = TicketHouseholdDataUpdateDetailsFactory(
            ticket=household_data_change_grv_new,
            household=household,
            household_data={
                "village": {
                    "value": "Test new",
                    "approve_status": True,
                },
                "flex_fields": {},
                "roles": [
                    {
                        "value": "PRIMARY",
                        "individual_id": str(first_individual.id),
                        "approve_status": True,
                        "full_name": first_individual.full_name,
                        "unicef_id": first_individual.unicef_id,
                        "previous_value": "ALTERNATE",
                    },
                    {
                        "value": "ALTERNATE",
                        "individual_id": str(second_individual.id),
                        "approve_status": True,
                        "full_name": second_individual.full_name,
                        "unicef_id": second_individual.unicef_id,
                        "previous_value": "-",
                    },
                ],
            },
        )
        self.assertEqual(IndividualRoleInHousehold.objects.filter(household=household).count(), 1)
        self.assertEqual(IndividualRoleInHousehold.objects.get(individual=first_individual).role, "ALTERNATE")

        service = HouseholdDataUpdateService(
            grievance_ticket=household_data_change_grv_new, extras=details.household_data
        )
        service.close(self.user)

        # check if role updated and new one created for second_individual
        self.assertEqual(IndividualRoleInHousehold.objects.filter(household=household).count(), 2)
        self.assertEqual(IndividualRoleInHousehold.objects.get(individual=first_individual).role, "PRIMARY")
        self.assertEqual(IndividualRoleInHousehold.objects.get(individual=second_individual).role, "ALTERNATE")
