from datetime import date
from io import BytesIO
from typing import Any
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from extras.test_utils.factories import (
    CountryFactory,
    DocumentFactory,
    DocumentTypeFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    TicketAddIndividualDetailsFactory,
    UserFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.data_change.add_individual_service import AddIndividualService
from hope.apps.grievance.services.data_change.utils import handle_add_identity
from hope.apps.household.const import HEAD, RELATIONSHIP_UNKNOWN, SINGLE
from hope.models import Document, Individual, IndividualIdentity, Program, User

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


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def unapproved_add_individual_context(program: Program) -> dict[str, Any]:
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
        approve_status=False,
    )
    ticket = ticket_details.ticket
    ticket.save()
    return {"household": household, "ticket": ticket, "ticket_details": ticket_details}


@pytest.fixture
def photo_upload() -> InMemoryUploadedFile:
    return InMemoryUploadedFile(
        file=BytesIO(b"123"),
        field_name="photo",
        name="test123.jpg",
        content_type="image/jpeg",
        size=3,
        charset=None,
    )


@pytest.fixture
def ticket_without_details(program: Program) -> GrievanceTicket:
    return GrievanceTicketFactory(
        business_area=program.business_area,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
    )


@pytest.fixture
def save_extras_with_photo(program: Program, photo_upload: InMemoryUploadedFile) -> dict[str, Any]:
    household = HouseholdFactory(program=program, business_area=program.business_area, create_role=False)
    return {
        "issue_type": {
            "add_individual_issue_type_extras": {
                "household": household,
                "individual_data": {"photo": photo_upload},
            }
        }
    }


@pytest.fixture
def update_extras_with_photo(photo_upload: InMemoryUploadedFile) -> dict[str, Any]:
    return {"add_individual_issue_type_extras": {"individual_data": {"photo": photo_upload}}}


@pytest.fixture
def head_add_individual_context(program: Program) -> dict[str, Any]:
    household = HouseholdFactory(program=program, business_area=program.business_area, create_role=False)
    ticket_details = TicketAddIndividualDetailsFactory(
        household=household,
        ticket__business_area=program.business_area,
        ticket__issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        individual_data={
            "given_name": "Head",
            "full_name": "Head Example",
            "family_name": "Example",
            "sex": "MALE",
            "birth_date": date(year=1980, month=2, day=1).isoformat(),
            "marital_status": SINGLE,
            "relationship": HEAD,
            "documents": [],
        },
        approve_status=True,
    )
    ticket = ticket_details.ticket
    ticket.save()
    return {
        "household": household,
        "ticket": ticket,
        "ticket_details": ticket_details,
        "previous_head": household.head_of_household,
    }


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


def test_add_individual_as_head_reassigns_existing_relationships_on_close_ticket(
    add_individual_context: dict[str, Any],
) -> None:
    household = add_individual_context["household"]
    ticket = add_individual_context["ticket"]
    ticket_details = add_individual_context["ticket_details"]
    previous_head = household.head_of_household
    ticket_details.individual_data["relationship"] = HEAD
    ticket_details.save()

    service = AddIndividualService(ticket, {})
    service.close(UserFactory())

    household.refresh_from_db()
    previous_head.refresh_from_db()
    new_head = Individual.objects.get(household=household, full_name="Test Example")
    assert household.head_of_household == new_head
    assert previous_head.relationship == RELATIONSHIP_UNKNOWN


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


def test_close_without_approval_creates_no_individual(
    unapproved_add_individual_context: dict[str, Any], user: User
) -> None:
    ticket = unapproved_add_individual_context["ticket"]
    individuals_before = Individual.objects.count()

    service = AddIndividualService(ticket, {})
    service.close(user)

    assert Individual.objects.count() == individuals_before


def test_close_with_head_relationship_replaces_head_of_household(
    head_add_individual_context: dict[str, Any], user: User
) -> None:
    household = head_add_individual_context["household"]
    previous_head = head_add_individual_context["previous_head"]
    ticket = head_add_individual_context["ticket"]

    service = AddIndividualService(ticket, {})
    service.close(user)

    household.refresh_from_db()
    new_head = Individual.objects.get(full_name="Head Example")
    assert household.head_of_household == new_head
    previous_head.refresh_from_db()
    assert previous_head.relationship == RELATIONSHIP_UNKNOWN


@patch("hope.apps.grievance.services.data_change.add_individual_service.handle_photo")
def test_save_stores_the_photo_under_the_individual_photo_field(
    mock_handle_photo: Any,
    ticket_without_details: GrievanceTicket,
    save_extras_with_photo: dict[str, Any],
    photo_upload: InMemoryUploadedFile,
) -> None:
    mock_handle_photo.return_value = "photo.jpg"

    AddIndividualService(ticket_without_details, save_extras_with_photo).save()

    mock_handle_photo.assert_called_once_with(photo_upload, None, Individual._meta.get_field("photo"))


@patch("hope.apps.grievance.services.data_change.add_individual_service.handle_photo")
def test_update_stores_the_photo_under_the_individual_photo_field(
    mock_handle_photo: Any,
    add_individual_context: dict[str, Any],
    update_extras_with_photo: dict[str, Any],
    photo_upload: InMemoryUploadedFile,
) -> None:
    mock_handle_photo.return_value = "photo.jpg"

    AddIndividualService(add_individual_context["ticket"], update_extras_with_photo).update()

    mock_handle_photo.assert_called_once_with(photo_upload, None, Individual._meta.get_field("photo"))
