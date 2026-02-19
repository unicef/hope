from datetime import date
from typing import Any

from django.core.exceptions import ValidationError
import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from extras.test_utils.factories import (
    CountryFactory,
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    TicketAddIndividualDetailsFactory,
    UserFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.data_change.add_individual_service import AddIndividualService
from hope.apps.grievance.services.data_change.utils import handle_add_identity
from hope.apps.household.const import SINGLE
from hope.models import Document, Individual, IndividualIdentity, Program

pytestmark = [
    pytest.mark.usefixtures("mock_elasticsearch"),
    pytest.mark.django_db,
]


@pytest.fixture
def program() -> Program:
    return ProgramFactory()


@pytest.fixture
def add_individual_context(program: Program) -> dict[str, Any]:
    household = HouseholdFactory(program=program, business_area=program.business_area, create_role=False)
    ticket_details = TicketAddIndividualDetailsFactory(
        household=household,
        ticket__business_area=program.business_area,
        ticket__issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        individual_data={
            "given_name": "Test",
            "full_name": "Test Example",
            "family_name": "Example",
            "sex": "MALE",
            "birth_date": date(year=1980, month=2, day=1).isoformat(),
            "marital_status": SINGLE,
            "documents": [],
        },
        approve_status=True,
    )
    ticket = ticket_details.ticket
    ticket.save()
    return {"household": household, "ticket": ticket, "ticket_details": ticket_details}


def test_increase_household_size_on_close_ticket(add_individual_context: dict[str, Any]) -> None:
    household = add_individual_context["household"]
    ticket = add_individual_context["ticket"]
    household.size = 3
    household.save(update_fields=("size",))

    service = AddIndividualService(ticket, {})
    service.close(UserFactory())

    household.refresh_from_db()
    assert household.size == 4


def test_increase_household_size_when_size_is_none_on_close_ticket(add_individual_context: dict[str, Any]) -> None:
    household = add_individual_context["household"]
    ticket = add_individual_context["ticket"]
    household.size = None
    household.save(update_fields=("size",))

    service = AddIndividualService(ticket, {})
    service.close(UserFactory())

    household.refresh_from_db()
    household_size = Individual.objects.filter(household=household).count()
    assert household.size == household_size


def test_add_individual_with_document_that_already_exists(
    add_individual_context: dict[str, Any],
    program: Program,
) -> None:
    household = add_individual_context["household"]
    ticket = add_individual_context["ticket"]
    ticket_details = add_individual_context["ticket_details"]
    individual = IndividualFactory(program=program, household=household, business_area=program.business_area)
    afg_country = CountryFactory(iso_code3="AFG")
    document_type = DocumentTypeFactory(unique_for_individual=True)
    DocumentFactory(
        status=Document.STATUS_VALID,
        program=program,
        type=document_type,
        document_number="123456",
        individual=individual,
        country=afg_country,
    )
    ticket_details.individual_data["documents"] = [
        {
            "key": document_type.key,
            "country": "AFG",
            "number": "123456",
        }
    ]
    ticket_details.save()

    service = AddIndividualService(ticket, {})
    with pytest.raises(DRFValidationError):
        service.close(UserFactory())
    assert Document.objects.filter(document_number="123456").count() == 1


def test_add_individual_with_document_that_exists_in_pending_status(
    add_individual_context: dict[str, Any],
    program: Program,
) -> None:
    household = add_individual_context["household"]
    ticket = add_individual_context["ticket"]
    ticket_details = add_individual_context["ticket_details"]
    individual = IndividualFactory(program=program, household=household, business_area=program.business_area)
    afg_country = CountryFactory(iso_code3="AFG")
    document_type = DocumentTypeFactory(unique_for_individual=True)
    DocumentFactory(
        status=Document.STATUS_PENDING,
        program=program,
        type=document_type,
        document_number="123456",
        individual=individual,
        country=afg_country,
    )
    ticket_details.individual_data["documents"] = [
        {
            "key": document_type.key,
            "country": "AFG",
            "number": "123456",
        }
    ]
    ticket_details.save()

    service = AddIndividualService(ticket, {})
    try:
        service.close(UserFactory())
    except ValidationError:
        pytest.fail("ValidationError should not be raised")
    assert Document.objects.filter(document_number="123456", status=Document.STATUS_VALID).count() == 0
    assert Document.objects.filter(document_number="123456").count() == 2


def test_handle_add_identity(add_individual_context: dict[str, Any], program: Program) -> None:
    household = add_individual_context["household"]
    poland = CountryFactory(iso_code3="PLN")
    individual = IndividualFactory(program=program, household=household, business_area=program.business_area)
    identity_data = {
        "partner": "UNICEF",
        "country": "PLN",
        "number": "A123456A",
    }
    identity_obj = handle_add_identity(identity_data, individual)

    assert isinstance(identity_obj, IndividualIdentity)
    assert identity_obj.partner.name == "UNICEF"
    assert identity_obj.number == "A123456A"
    assert identity_obj.country == poland
