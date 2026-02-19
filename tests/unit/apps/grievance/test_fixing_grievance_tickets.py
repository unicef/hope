from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    IndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    TicketIndividualDataUpdateDetailsFactory,
)
from hope.apps.grievance.management.commands.fix_grievance_tickets import fix_disability_fields
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.const import DISABLED, NOT_DISABLED
from hope.models import BusinessArea, Individual, Program, RegistrationDataImport

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
        region_code="64",
        region_name="SAR",
        slug="afghanistan",
    )


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def registration_data_import(business_area: BusinessArea, program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(business_area=business_area, program=program)


@pytest.fixture
def individual(
    business_area: BusinessArea,
    program: Program,
    registration_data_import: RegistrationDataImport,
) -> Individual:
    return IndividualFactory(
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import,
        given_name="Test",
        full_name="Test Testowski",
        middle_name="",
        family_name="Testowski",
        phone_no="123-123-123",
        phone_no_alternative="",
    )


@pytest.mark.parametrize(
    ("previous_value", "new_value"),
    [
        (True, DISABLED),
        (False, NOT_DISABLED),
    ],
)
def test_wrong_value_in_disability_field(
    previous_value: Any,
    new_value: str,
    business_area: BusinessArea,
    individual: Individual,
) -> None:
    assert GrievanceTicket.objects.count() == 0
    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
    )
    assert GrievanceTicket.objects.count() == 1
    TicketIndividualDataUpdateDetailsFactory(
        ticket=ticket,
        individual=individual,
        individual_data={
            "disability": {
                "value": previous_value,
            }
        },
    )
    assert ticket.individual_data_update_ticket_details.individual_data["disability"]["value"] == previous_value

    fix_disability_fields()

    ticket.refresh_from_db()
    assert ticket.individual_data_update_ticket_details.individual_data["disability"]["value"] == new_value


def test_skipping_when_ind_data_update_ticket_details_does_not_exist(
    business_area: BusinessArea,
) -> None:
    assert GrievanceTicket.objects.count() == 0
    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
    )
    assert GrievanceTicket.objects.count() == 1

    fix_disability_fields()
    ticket.refresh_from_db()
    assert GrievanceTicket.objects.filter(id=ticket.id).exists()
    with pytest.raises(GrievanceTicket.individual_data_update_ticket_details.RelatedObjectDoesNotExist):
        _ = ticket.individual_data_update_ticket_details
