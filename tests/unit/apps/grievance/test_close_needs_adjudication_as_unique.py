"""Tests for closing a Unique Identifiers Similarity needs-adjudication ticket as unique.

Covers Document.dedup_signature, TicketNeedsAdjudicationDetails.documents_no_longer_conflict,
the can_close_as_unique / mark_unique_and_close / find_open_unique_identifiers_ticket_for_individual
services, the close-as-unique API action, and the Data Change ticket's link to its Needs
Adjudication counterpart (IndividualDataUpdateTicketDetailsSerializer.linked_needs_adjudication_ticket_id).
"""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    AdminAreaLimitedToFactory,
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DocumentFactory,
    DocumentTypeFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    PartnerFactory,
    ProgramFactory,
    TicketIndividualDataUpdateDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails
from hope.apps.grievance.services.needs_adjudication_ticket_services import (
    can_close_as_unique,
    find_open_unique_identifiers_ticket_for_individual,
    mark_unique_and_close,
)
from hope.apps.household.const import NEEDS_ADJUDICATION, UNIQUE
from hope.models import Document

pytestmark = [
    pytest.mark.usefixtures("mock_elasticsearch"),
    pytest.mark.django_db,
]


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def program(business_area: Any) -> Any:
    return ProgramFactory(business_area=business_area, name="program afghanistan 1")


@pytest.fixture
def partner() -> Any:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Any) -> Any:
    return UserFactory(partner=partner)


@pytest.fixture
def country() -> Any:
    return CountryFactory(name="Poland", short_name="Poland", iso_code2="PL", iso_code3="POL", iso_num="0616")


@pytest.fixture
def national_id_type() -> Any:
    return DocumentTypeFactory(key="national_id", valid_for_deduplication=True)


@pytest.fixture
def receipt_type() -> Any:
    return DocumentTypeFactory(key="receipt", valid_for_deduplication=False)


def _build_individual(program: Any, business_area: Any) -> Any:
    household = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    return household.head_of_household


def _add_national_id(
    individual: Any,
    national_id_type: Any,
    country: Any,
    program: Any,
    number: str,
    doc_status: str = Document.STATUS_VALID,
) -> Document:
    return DocumentFactory(
        type=national_id_type,
        document_number=number,
        individual=individual,
        country=country,
        program=program,
        status=doc_status,
    )


def _build_ticket(
    business_area: Any,
    program: Any,
    golden: Any,
    duplicates: list,
    issue_type: int = GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
    ticket_status: int = GrievanceTicket.STATUS_FOR_APPROVAL,
) -> TicketNeedsAdjudicationDetails:
    grievance = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=issue_type,
        business_area=business_area,
        status=ticket_status,
    )
    grievance.programs.set([program])
    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance,
        golden_records_individual=golden,
        is_multiple_duplicates_version=True,
        selected_individual=None,
    )
    ticket_details.possible_duplicates.add(*duplicates)
    return ticket_details


# --------------------------------------------------------------------------- #
# Document.dedup_signature
# --------------------------------------------------------------------------- #
def test_dedup_signature_includes_type_and_country_when_valid_for_deduplication(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    individual = _build_individual(program, business_area)
    document = _add_national_id(individual, national_id_type, country, program, "ID-1")

    assert document.dedup_signature == f"{document.type_id}--ID-1--{country.id}"


def test_dedup_signature_excludes_type_when_not_valid_for_deduplication(
    business_area: Any, program: Any, receipt_type: Any, country: Any
) -> None:
    individual = _build_individual(program, business_area)
    document = DocumentFactory(
        type=receipt_type,
        document_number="R-1",
        individual=individual,
        country=country,
        program=program,
        status=Document.STATUS_VALID,
    )

    assert document.dedup_signature == f"R-1--{country.id}"


# --------------------------------------------------------------------------- #
# TicketNeedsAdjudicationDetails.documents_no_longer_conflict
# --------------------------------------------------------------------------- #
def test_documents_no_longer_conflict_true_when_numbers_differ(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-AAA")
    _add_national_id(duplicate, national_id_type, country, program, "ID-BBB")
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])

    assert ticket_details.documents_no_longer_conflict() is True


def test_documents_no_longer_conflict_false_when_numbers_match(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-SAME")
    _add_national_id(
        duplicate, national_id_type, country, program, "ID-SAME", doc_status=Document.STATUS_NEED_INVESTIGATION
    )
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])

    assert ticket_details.documents_no_longer_conflict() is False


def test_documents_no_longer_conflict_true_for_single_individual(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-ONLY")
    ticket_details = _build_ticket(business_area, program, golden, [])

    assert ticket_details.documents_no_longer_conflict() is True


def test_documents_no_longer_conflict_false_on_partial_resolution(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    fixed = _build_individual(program, business_area)
    still_sharing = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-SHARED")
    _add_national_id(fixed, national_id_type, country, program, "ID-FIXED")
    _add_national_id(
        still_sharing, national_id_type, country, program, "ID-SHARED", doc_status=Document.STATUS_NEED_INVESTIGATION
    )
    ticket_details = _build_ticket(business_area, program, golden, [fixed, still_sharing])

    assert ticket_details.documents_no_longer_conflict() is False


def test_documents_no_longer_conflict_ignores_selected_duplicates(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    removed_duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-SHARED")
    _add_national_id(
        removed_duplicate,
        national_id_type,
        country,
        program,
        "ID-SHARED",
        doc_status=Document.STATUS_NEED_INVESTIGATION,
    )
    ticket_details = _build_ticket(business_area, program, golden, [removed_duplicate])
    ticket_details.selected_individuals.add(removed_duplicate)

    assert ticket_details.documents_no_longer_conflict() is True


def test_documents_no_longer_conflict_ignores_invalid_documents(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-SHARED")
    _add_national_id(duplicate, national_id_type, country, program, "ID-SHARED", doc_status=Document.STATUS_INVALID)
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])

    assert ticket_details.documents_no_longer_conflict() is True


# --------------------------------------------------------------------------- #
# can_close_as_unique
# --------------------------------------------------------------------------- #
def test_can_close_as_unique_true_when_resolved(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])

    assert can_close_as_unique(ticket_details) is True


def test_can_close_as_unique_false_for_biographical_issue_type(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    ticket_details = _build_ticket(
        business_area,
        program,
        golden,
        [duplicate],
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
    )

    assert can_close_as_unique(ticket_details) is False


def test_can_close_as_unique_false_when_conflict_remains(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-SAME")
    _add_national_id(
        duplicate, national_id_type, country, program, "ID-SAME", doc_status=Document.STATUS_NEED_INVESTIGATION
    )
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])

    assert can_close_as_unique(ticket_details) is False


def test_can_close_as_unique_false_when_other_open_ticket(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])
    _build_ticket(business_area, program, golden, [duplicate])  # second open ticket for the same individuals

    assert can_close_as_unique(ticket_details) is False


# --------------------------------------------------------------------------- #
# mark_unique_and_close
# --------------------------------------------------------------------------- #
def test_mark_unique_and_close_marks_all_distinct_and_closes(
    user: Any, business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    golden.deduplication_golden_record_status = NEEDS_ADJUDICATION
    golden.save()
    duplicate.deduplication_golden_record_status = NEEDS_ADJUDICATION
    duplicate.save()
    doc_golden = _add_national_id(golden, national_id_type, country, program, "ID-1")
    doc_duplicate = _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])

    mark_unique_and_close(ticket_details, user)

    ticket_details.ticket.refresh_from_db()
    golden.refresh_from_db()
    duplicate.refresh_from_db()
    doc_golden.refresh_from_db()
    doc_duplicate.refresh_from_db()
    assert ticket_details.ticket.status == GrievanceTicket.STATUS_CLOSED
    assert golden.duplicate is False
    assert duplicate.duplicate is False
    assert golden.deduplication_golden_record_status == UNIQUE
    assert duplicate.deduplication_golden_record_status == UNIQUE
    assert doc_golden.status == Document.STATUS_VALID
    assert doc_duplicate.status == Document.STATUS_VALID
    assert set(ticket_details.selected_distinct.all()) == {golden, duplicate}


@pytest.mark.parametrize(
    "issue_type",
    [
        GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY,
    ],
)
def test_mark_unique_and_close_raises_for_non_unique_identifiers_issue_type(
    user: Any, business_area: Any, program: Any, national_id_type: Any, country: Any, issue_type: int
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    ticket_details = _build_ticket(business_area, program, golden, [duplicate], issue_type=issue_type)

    with pytest.raises(DRFValidationError):
        mark_unique_and_close(ticket_details, user)


def test_mark_unique_and_close_raises_when_already_closed(
    user: Any, business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    ticket_details = _build_ticket(
        business_area, program, golden, [duplicate], ticket_status=GrievanceTicket.STATUS_CLOSED
    )

    with pytest.raises(DRFValidationError):
        mark_unique_and_close(ticket_details, user)


def test_mark_unique_and_close_raises_when_documents_still_conflict(
    user: Any, business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-SAME")
    _add_national_id(
        duplicate, national_id_type, country, program, "ID-SAME", doc_status=Document.STATUS_NEED_INVESTIGATION
    )
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])

    with pytest.raises(DRFValidationError):
        mark_unique_and_close(ticket_details, user)


def test_mark_unique_and_close_raises_when_other_open_ticket(
    user: Any, business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])
    _build_ticket(business_area, program, golden, [duplicate])

    with pytest.raises(DRFValidationError):
        mark_unique_and_close(ticket_details, user)


# --------------------------------------------------------------------------- #
# close-as-unique API action
# --------------------------------------------------------------------------- #
def _close_as_unique_url(business_area: Any, ticket_details: TicketNeedsAdjudicationDetails) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-close-as-unique",
        kwargs={
            "business_area_slug": business_area.slug,
            "pk": str(ticket_details.ticket.pk),
        },
    )


def test_close_as_unique_endpoint_success(
    api_client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    national_id_type: Any,
    country: Any,
    create_user_role_with_permissions: Callable,
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])
    create_user_role_with_permissions(
        user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], business_area, program
    )

    client = api_client(user)
    response = client.post(_close_as_unique_url(business_area, ticket_details), {}, format="json")

    assert response.status_code == status.HTTP_202_ACCEPTED
    ticket_details.ticket.refresh_from_db()
    golden.refresh_from_db()
    assert ticket_details.ticket.status == GrievanceTicket.STATUS_CLOSED
    assert golden.duplicate is False


def test_close_as_unique_endpoint_rejects_when_conflict_remains(
    api_client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    national_id_type: Any,
    country: Any,
    create_user_role_with_permissions: Callable,
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-SAME")
    _add_national_id(
        duplicate, national_id_type, country, program, "ID-SAME", doc_status=Document.STATUS_NEED_INVESTIGATION
    )
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])
    create_user_role_with_permissions(
        user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], business_area, program
    )

    client = api_client(user)
    response = client.post(_close_as_unique_url(business_area, ticket_details), {}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    ticket_details.ticket.refresh_from_db()
    assert ticket_details.ticket.status == GrievanceTicket.STATUS_FOR_APPROVAL


def test_close_as_unique_endpoint_forbidden_without_permission(
    api_client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    national_id_type: Any,
    country: Any,
    create_user_role_with_permissions: Callable,
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_UPDATE], business_area, program)

    client = api_client(user)
    response = client.post(_close_as_unique_url(business_area, ticket_details), {}, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_close_as_unique_endpoint_forbidden_without_area_access(
    api_client: Any,
    user: Any,
    partner: Any,
    business_area: Any,
    program: Any,
    national_id_type: Any,
    country: Any,
    create_user_role_with_permissions: Callable,
) -> None:
    area_type = AreaTypeFactory(name="District", country=country, area_level=2)
    ticket_area = AreaFactory(name="Ticket Area", area_type=area_type, p_code="ticket-area")
    other_area = AreaFactory(name="Other Area", area_type=area_type, p_code="other-area")
    golden_household = HouseholdFactory(
        program=program, business_area=business_area, create_role=False, admin2=ticket_area
    )
    golden = golden_household.head_of_household
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])
    create_user_role_with_permissions(
        user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], business_area, program
    )
    AdminAreaLimitedToFactory(partner=partner, program=program, areas=[other_area])

    client = api_client(user)
    response = client.post(_close_as_unique_url(business_area, ticket_details), {}, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_close_as_unique_endpoint_rejects_non_needs_adjudication_ticket(
    api_client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_REFERRAL,
        issue_type=None,
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
    )
    grievance.programs.set([program])
    create_user_role_with_permissions(
        user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], business_area, program
    )

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-close-as-unique",
        kwargs={"business_area_slug": business_area.slug, "pk": str(grievance.pk)},
    )
    client = api_client(user)
    response = client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# --------------------------------------------------------------------------- #
# find_open_unique_identifiers_ticket_for_individual
# --------------------------------------------------------------------------- #
def test_find_open_unique_identifiers_ticket_for_individual_finds_golden(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])

    assert find_open_unique_identifiers_ticket_for_individual(golden) == ticket_details


def test_find_open_unique_identifiers_ticket_for_individual_finds_possible_duplicate(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    ticket_details = _build_ticket(business_area, program, golden, [duplicate])

    assert find_open_unique_identifiers_ticket_for_individual(duplicate) == ticket_details


def test_find_open_unique_identifiers_ticket_for_individual_none_when_ticket_closed(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    _build_ticket(business_area, program, golden, [duplicate], ticket_status=GrievanceTicket.STATUS_CLOSED)

    assert find_open_unique_identifiers_ticket_for_individual(golden) is None


def test_find_open_unique_identifiers_ticket_for_individual_none_for_other_issue_type(
    business_area: Any, program: Any, national_id_type: Any, country: Any
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    _build_ticket(
        business_area,
        program,
        golden,
        [duplicate],
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
    )

    assert find_open_unique_identifiers_ticket_for_individual(golden) is None


def test_find_open_unique_identifiers_ticket_for_individual_none_when_no_ticket(
    business_area: Any, program: Any
) -> None:
    unrelated = _build_individual(program, business_area)

    assert find_open_unique_identifiers_ticket_for_individual(unrelated) is None


def test_find_open_unique_identifiers_ticket_for_individual_single_query(
    business_area: Any, program: Any, national_id_type: Any, country: Any, django_assert_num_queries: Callable
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    _build_ticket(business_area, program, golden, [duplicate])

    with django_assert_num_queries(1):
        find_open_unique_identifiers_ticket_for_individual(golden)


# --------------------------------------------------------------------------- #
# Data Change ticket detail exposes linked_needs_adjudication_ticket_id
# --------------------------------------------------------------------------- #
def _data_change_ticket_detail_url(business_area: Any, grievance_ticket: GrievanceTicket) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-detail",
        kwargs={"business_area_slug": business_area.slug, "pk": str(grievance_ticket.id)},
    )


def test_data_change_ticket_exposes_linked_ticket_id_when_present(
    api_client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    national_id_type: Any,
    country: Any,
    create_user_role_with_permissions: Callable,
) -> None:
    golden = _build_individual(program, business_area)
    duplicate = _build_individual(program, business_area)
    _add_national_id(golden, national_id_type, country, program, "ID-1")
    _add_national_id(duplicate, national_id_type, country, program, "ID-2")
    na_ticket_details = _build_ticket(business_area, program, golden, [duplicate])
    data_change_ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        business_area=business_area,
    )
    data_change_ticket.programs.set([program])
    data_update_details = TicketIndividualDataUpdateDetailsFactory(ticket=data_change_ticket, individual=golden)
    create_user_role_with_permissions(
        user, [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE], business_area, program
    )

    client = api_client(user)
    response = client.get(_data_change_ticket_detail_url(business_area, data_update_details.ticket))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["ticket_details"]["linked_needs_adjudication_ticket_id"] == str(na_ticket_details.ticket_id)


def test_data_change_ticket_linked_ticket_id_none_when_absent(
    api_client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    create_user_role_with_permissions: Callable,
) -> None:
    unrelated = _build_individual(program, business_area)
    data_change_ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        business_area=business_area,
    )
    data_change_ticket.programs.set([program])
    data_update_details = TicketIndividualDataUpdateDetailsFactory(ticket=data_change_ticket, individual=unrelated)
    create_user_role_with_permissions(
        user, [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE], business_area, program
    )

    client = api_client(user)
    response = client.get(_data_change_ticket_detail_url(business_area, data_update_details.ticket))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["ticket_details"]["linked_needs_adjudication_ticket_id"] is None
