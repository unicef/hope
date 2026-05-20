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
from hope.apps.grievance.management.commands.fix_grievance_tickets import (
    _fix_disability_fields_for_ba,
    _map_disability_value,
    fix_disability_fields,
)
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


@pytest.fixture
def grievance_ticket(business_area: BusinessArea) -> GrievanceTicket:
    return GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
    )


@pytest.fixture
def make_ticket_with_details(business_area, individual):
    def _make(individual_data):
        ticket = GrievanceTicketFactory(
            business_area=business_area,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=ticket,
            individual=individual,
            individual_data=individual_data,
        )
        return ticket

    return _make


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
    make_ticket_with_details,
) -> None:
    assert GrievanceTicket.objects.count() == 0
    ticket = make_ticket_with_details({"disability": {"value": previous_value}})
    assert GrievanceTicket.objects.count() == 1
    assert ticket.individual_data_update_ticket_details.individual_data["disability"]["value"] == previous_value

    fix_disability_fields()

    ticket.refresh_from_db()
    assert ticket.individual_data_update_ticket_details.individual_data["disability"]["value"] == new_value


def test_skipping_when_ind_data_update_ticket_details_does_not_exist(
    grievance_ticket: GrievanceTicket,
) -> None:
    assert GrievanceTicket.objects.count() == 1

    fix_disability_fields()
    grievance_ticket.refresh_from_db()
    assert GrievanceTicket.objects.filter(id=grievance_ticket.id).exists()
    with pytest.raises(GrievanceTicket.individual_data_update_ticket_details.RelatedObjectDoesNotExist):
        _ = grievance_ticket.individual_data_update_ticket_details


@pytest.mark.parametrize(
    "value",
    ["some_string", 42, None, 0, 1, "", [], {}],
)
def test_map_disability_value_none_for_non_boolean(value: Any) -> None:
    assert _map_disability_value(value) is None


def test_map_disability_value_returns_disabled_for_true() -> None:
    assert _map_disability_value(True) == DISABLED


def test_map_disability_value_returns_not_disabled_for_false() -> None:
    assert _map_disability_value(False) == NOT_DISABLED


def test_skip_when_individual_data_is_empty(
    make_ticket_with_details,
) -> None:
    ticket = make_ticket_with_details({})

    fix_disability_fields()

    ticket.refresh_from_db()
    assert ticket.individual_data_update_ticket_details.individual_data == {}


def test_skip_when_individual_data_is_none(
    make_ticket_with_details,
) -> None:
    ticket = make_ticket_with_details(None)

    fix_disability_fields()

    ticket.refresh_from_db()
    assert ticket.individual_data_update_ticket_details.individual_data is None


def test_skip_when_disability_key_missing(
    make_ticket_with_details,
) -> None:
    ticket = make_ticket_with_details({"other_field": "value"})

    fix_disability_fields()

    ticket.refresh_from_db()
    assert ticket.individual_data_update_ticket_details.individual_data == {"other_field": "value"}


def test_skip_when_disability_value_is_none(
    make_ticket_with_details,
) -> None:
    ticket = make_ticket_with_details({"disability": {"value": None}})

    fix_disability_fields()

    ticket.refresh_from_db()
    assert ticket.individual_data_update_ticket_details.individual_data["disability"]["value"] is None


def test_skip_when_disability_has_non_boolean_value(
    make_ticket_with_details,
) -> None:
    ticket = make_ticket_with_details({"disability": {"value": "some_string"}})

    fix_disability_fields()

    ticket.refresh_from_db()
    assert ticket.individual_data_update_ticket_details.individual_data["disability"]["value"] == "some_string"


def test_fix_disability_fields_for_specific_business_area(
    business_area: BusinessArea,
    make_ticket_with_details,
) -> None:
    ticket = make_ticket_with_details({"disability": {"value": True}})

    _fix_disability_fields_for_ba(business_area)

    ticket.refresh_from_db()
    assert ticket.individual_data_update_ticket_details.individual_data["disability"]["value"] == DISABLED
