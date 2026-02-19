from typing import Any

import pytest

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    CountryFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    TicketHouseholdDataUpdateDetailsFactory,
    UserFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.data_change.household_data_update_service import HouseholdDataUpdateService
from hope.apps.household.const import ROLE_ALTERNATE
from hope.models import IndividualRoleInHousehold, Program, User
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def program() -> Program:
    return ProgramFactory(status=Program.ACTIVE, name="program afghanistan 1")


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def role_context(program: Program) -> dict[str, Any]:
    household = HouseholdFactory(program=program, business_area=program.business_area, create_role=False)
    individual = IndividualFactory(
        household=household,
        program=program,
        business_area=program.business_area,
        registration_data_import=household.registration_data_import,
    )
    household.head_of_household = individual
    household.save(update_fields=["head_of_household"])
    IndividualRoleInHousehold.objects.create(
        household=household,
        individual=individual,
        role=ROLE_ALTERNATE,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    grievance_ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
        business_area=program.business_area,
    )
    return {"individual": individual, "household": household, "grievance_ticket": grievance_ticket}


def test_propagate_admin_areas_on_close_ticket() -> None:
    household = HouseholdFactory(create_role=False)
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
    service.close(UserFactory())
    household.refresh_from_db()

    assert household.admin_area.p_code == "AF010101"
    assert household.admin1.p_code == "AF01"
    assert household.admin2.p_code == "AF0101"
    assert household.admin3.p_code == "AF010101"


def test_update_roles_new_create_ticket(role_context: dict[str, Any]) -> None:
    individual = role_context["individual"]
    household = role_context["household"]
    grievance_ticket = role_context["grievance_ticket"]
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
    assert details.household_data == expected_dict


def test_update_roles_new_update_ticket_add_new_role(role_context: dict[str, Any]) -> None:
    individual = role_context["individual"]
    household = role_context["household"]
    grievance_ticket = role_context["grievance_ticket"]
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
    service = HouseholdDataUpdateService(grievance_ticket=grievance_ticket, extras=extras)
    ticket = service.save()[0]
    details = ticket.ticket_details
    expected_dict = {
        "country": {"value": "AGO", "approve_status": False, "previous_value": None},
        "flex_fields": {},
    }
    assert details.household_data == expected_dict

    update_extras = {
        "household_data_update_issue_type_extras": {
            "household": household,
            "household_data": {
                "country": "AGO",
                "flex_fields": {},
                "roles": [{"new_role": "ALTERNATE", "individual": individual}],
            },
        }
    }
    service = HouseholdDataUpdateService(grievance_ticket=grievance_ticket, extras=update_extras)
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
    assert details.household_data == expected_dict


def test_update_roles_new_update_ticket_update_role(role_context: dict[str, Any]) -> None:
    individual = role_context["individual"]
    household = role_context["household"]
    grievance_ticket = role_context["grievance_ticket"]
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
    assert details.household_data == expected_dict

    update_extras = {
        "household_data_update_issue_type_extras": {
            "household": household,
            "household_data": {
                "country": "AGO",
                "flex_fields": {},
                "roles": [{"new_role": "PRIMARY", "individual": individual}],
            },
        }
    }
    service = HouseholdDataUpdateService(grievance_ticket=grievance_ticket, extras=update_extras)
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
    assert details.household_data == expected_dict


def test_update_roles_new_approve_ticket(role_context: dict[str, Any]) -> None:
    individual = role_context["individual"]
    household = role_context["household"]
    grievance_ticket = role_context["grievance_ticket"]
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
    assert details.household_data == expected_dict


def test_close_household_update_new_roles(program: Program, user: User) -> None:
    household = HouseholdFactory(program=program, business_area=program.business_area, create_role=False)
    first_individual = IndividualFactory(
        household=household,
        program=program,
        business_area=program.business_area,
        registration_data_import=household.registration_data_import,
    )
    household.head_of_household = first_individual
    household.save(update_fields=["head_of_household"])
    second_individual = IndividualFactory(
        program=program,
        household=household,
        business_area=program.business_area,
        registration_data_import=household.registration_data_import,
    )
    IndividualRoleInHousehold.objects.create(
        household=household,
        individual=first_individual,
        role=ROLE_ALTERNATE,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    household_data_change_grv_new = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
        business_area=program.business_area,
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
    assert IndividualRoleInHousehold.objects.filter(household=household).count() == 1
    assert IndividualRoleInHousehold.objects.get(individual=first_individual).role == "ALTERNATE"

    service = HouseholdDataUpdateService(grievance_ticket=household_data_change_grv_new, extras=details.household_data)
    service.close(user)

    assert IndividualRoleInHousehold.objects.filter(household=household).count() == 2
    assert IndividualRoleInHousehold.objects.get(individual=first_individual).role == "PRIMARY"
    assert IndividualRoleInHousehold.objects.get(individual=second_individual).role == "ALTERNATE"
