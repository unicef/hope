from typing import Any
from uuid import uuid4

import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    ProgramFactory,
    UserFactory,
)
from extras.test_utils.factories.grievance import TicketComplaintDetailsFactory
from hope.api.caches import get_or_create_cache_key
from hope.apps.activity_log.utils import create_diff
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.bulk_action_service import (
    _ACTIVITY_LOG_SELECT_RELATED,
    BulkActionService,
)
from hope.models import BusinessArea, LogEntry, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def user() -> User:
    return UserFactory(first_name="user")


@pytest.fixture
def business_area_other() -> BusinessArea:
    return BusinessAreaFactory(name="Ukraine", slug="ukraine", code="4410")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def complaint_for_approval(business_area: BusinessArea, user: User) -> GrievanceTicket:
    return TicketComplaintDetailsFactory(
        ticket__business_area=business_area,
        ticket__created_by=user,
        ticket__status=GrievanceTicket.STATUS_FOR_APPROVAL,
    ).ticket


@pytest.fixture
def another_complaint_for_approval(business_area: BusinessArea, user: User) -> GrievanceTicket:
    return TicketComplaintDetailsFactory(
        ticket__business_area=business_area,
        ticket__created_by=user,
        ticket__status=GrievanceTicket.STATUS_FOR_APPROVAL,
    ).ticket


@pytest.fixture
def complaint_for_approval_with_program(business_area: BusinessArea, user: User, program: Program) -> GrievanceTicket:
    ticket = TicketComplaintDetailsFactory(
        ticket__business_area=business_area,
        ticket__created_by=user,
        ticket__status=GrievanceTicket.STATUS_FOR_APPROVAL,
    ).ticket
    ticket.programs.add(program)
    return ticket


@pytest.fixture
def complaint_new(business_area: BusinessArea, user: User) -> GrievanceTicket:
    return TicketComplaintDetailsFactory(
        ticket__business_area=business_area,
        ticket__created_by=user,
        ticket__status=GrievanceTicket.STATUS_NEW,
    ).ticket


@pytest.fixture
def complaint_closed(business_area: BusinessArea, user: User) -> GrievanceTicket:
    return TicketComplaintDetailsFactory(
        ticket__business_area=business_area,
        ticket__created_by=user,
        ticket__status=GrievanceTicket.STATUS_CLOSED,
    ).ticket


@pytest.fixture
def complaint_in_other_business_area(business_area_other: BusinessArea, user: User) -> GrievanceTicket:
    return TicketComplaintDetailsFactory(
        ticket__business_area=business_area_other,
        ticket__created_by=user,
        ticket__status=GrievanceTicket.STATUS_FOR_APPROVAL,
    ).ticket


@pytest.fixture
def needs_adjudication_for_approval(business_area: BusinessArea, user: User) -> GrievanceTicket:
    return GrievanceTicketFactory(
        business_area=business_area,
        created_by=user,
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
    )


def test_bulk_close_closes_complaint_ticket_in_for_approval(
    business_area: BusinessArea, user: User, complaint_for_approval: GrievanceTicket
) -> None:
    BulkActionService().bulk_close(user, [complaint_for_approval.id], business_area.slug)

    complaint_for_approval.refresh_from_db()

    assert complaint_for_approval.status == GrievanceTicket.STATUS_CLOSED


def test_bulk_close_rejects_non_complaint_ticket(
    business_area: BusinessArea, user: User, needs_adjudication_for_approval: GrievanceTicket
) -> None:
    with pytest.raises(ValidationError):
        BulkActionService().bulk_close(user, [needs_adjudication_for_approval.id], business_area.slug)

    needs_adjudication_for_approval.refresh_from_db()

    assert needs_adjudication_for_approval.status == GrievanceTicket.STATUS_FOR_APPROVAL


def test_bulk_close_rejects_complaint_ticket_in_wrong_status(
    business_area: BusinessArea, user: User, complaint_new: GrievanceTicket
) -> None:
    with pytest.raises(ValidationError):
        BulkActionService().bulk_close(user, [complaint_new.id], business_area.slug)

    complaint_new.refresh_from_db()

    assert complaint_new.status == GrievanceTicket.STATUS_NEW


def test_bulk_close_error_message(business_area: BusinessArea, user: User, complaint_new: GrievanceTicket) -> None:
    with pytest.raises(ValidationError) as exc_info:
        BulkActionService().bulk_close(user, [complaint_new.id], business_area.slug)

    assert str(exc_info.value.detail[0]) == (
        "Some selected tickets cannot be closed. Only Grievance Complaint tickets in status For Approval can be closed."
    )


def test_bulk_close_closes_nothing_when_a_ticket_is_wrong_type(
    business_area: BusinessArea,
    user: User,
    complaint_for_approval: GrievanceTicket,
    needs_adjudication_for_approval: GrievanceTicket,
) -> None:
    with pytest.raises(ValidationError):
        BulkActionService().bulk_close(
            user,
            [complaint_for_approval.id, needs_adjudication_for_approval.id],
            business_area.slug,
        )

    complaint_for_approval.refresh_from_db()
    needs_adjudication_for_approval.refresh_from_db()

    assert complaint_for_approval.status == GrievanceTicket.STATUS_FOR_APPROVAL
    assert needs_adjudication_for_approval.status == GrievanceTicket.STATUS_FOR_APPROVAL


def test_bulk_close_closes_nothing_when_a_complaint_is_wrong_status(
    business_area: BusinessArea,
    user: User,
    complaint_for_approval: GrievanceTicket,
    complaint_new: GrievanceTicket,
) -> None:
    with pytest.raises(ValidationError):
        BulkActionService().bulk_close(
            user,
            [complaint_for_approval.id, complaint_new.id],
            business_area.slug,
        )

    complaint_for_approval.refresh_from_db()
    complaint_new.refresh_from_db()

    assert complaint_for_approval.status == GrievanceTicket.STATUS_FOR_APPROVAL
    assert complaint_new.status == GrievanceTicket.STATUS_NEW


def test_bulk_close_bumps_grievance_version_cache(
    business_area: BusinessArea,
    user: User,
    program: Program,
    complaint_for_approval_with_program: GrievanceTicket,
) -> None:
    business_area_version = get_or_create_cache_key(f"{business_area.slug}:version", 1)
    version_key = f"{business_area.slug}:{business_area_version}:{program.code}:grievance_ticket_list"
    version_before = get_or_create_cache_key(version_key, 1)

    BulkActionService().bulk_close(user, [complaint_for_approval_with_program.id], business_area.slug)

    assert get_or_create_cache_key(version_key, 1) == version_before + 1


def test_bulk_close_writes_activity_log(
    business_area: BusinessArea, user: User, complaint_for_approval: GrievanceTicket
) -> None:
    BulkActionService().bulk_close(user, [complaint_for_approval.id], business_area.slug)

    assert LogEntry.objects.filter(object_id=complaint_for_approval.id, action=LogEntry.UPDATE).exists()


def test_bulk_close_select_related_covers_activity_log_diff(
    complaint_for_approval: GrievanceTicket,
    django_assert_num_queries: Any,
) -> None:
    # bulk_close logs every closed ticket, and create_diff reads every relation in
    # ACTIVITY_LOG_MAPPING. This guards that _ACTIVITY_LOG_SELECT_RELATED covers them all so the
    # diff stays query-free (no per-ticket N+1); it fails if a relation is added to the mapping
    # but not to the select_related tuple.
    ticket = (
        GrievanceTicket.objects.filter(pk=complaint_for_approval.pk)
        .select_related(*_ACTIVITY_LOG_SELECT_RELATED)
        .prefetch_related("programs")
        .get()
    )

    with django_assert_num_queries(0):
        create_diff(ticket, ticket, GrievanceTicket.ACTIVITY_LOG_MAPPING)
        assert ticket.business_area is not None
        assert list(ticket.programs.all()) == []


def test_bulk_close_query_count_scales_per_ticket(
    business_area: BusinessArea,
    user: User,
    complaint_for_approval: GrievanceTicket,
    another_complaint_for_approval: GrievanceTicket,
    django_assert_max_num_queries: Any,
) -> None:
    with django_assert_max_num_queries(16):
        BulkActionService().bulk_close(
            user,
            [complaint_for_approval.id, another_complaint_for_approval.id],
            business_area.slug,
        )


def test_bulk_close_closes_multiple_complaints(
    business_area: BusinessArea,
    user: User,
    complaint_for_approval: GrievanceTicket,
    another_complaint_for_approval: GrievanceTicket,
) -> None:
    BulkActionService().bulk_close(
        user,
        [complaint_for_approval.id, another_complaint_for_approval.id],
        business_area.slug,
    )

    complaint_for_approval.refresh_from_db()
    another_complaint_for_approval.refresh_from_db()

    assert complaint_for_approval.status == GrievanceTicket.STATUS_CLOSED
    assert another_complaint_for_approval.status == GrievanceTicket.STATUS_CLOSED


def test_bulk_close_rejects_already_closed_ticket(
    business_area: BusinessArea, user: User, complaint_closed: GrievanceTicket
) -> None:
    with pytest.raises(ValidationError):
        BulkActionService().bulk_close(user, [complaint_closed.id], business_area.slug)


def test_bulk_close_rejects_non_existent_ticket(business_area: BusinessArea, user: User) -> None:
    with pytest.raises(ValidationError):
        BulkActionService().bulk_close(user, [uuid4()], business_area.slug)


def test_bulk_close_with_empty_list_closes_nothing(business_area: BusinessArea, user: User) -> None:
    result = BulkActionService().bulk_close(user, [], business_area.slug)

    assert result.count() == 0


def test_bulk_close_scopes_to_business_area(
    business_area: BusinessArea, user: User, complaint_in_other_business_area: GrievanceTicket
) -> None:
    with pytest.raises(ValidationError):
        BulkActionService().bulk_close(user, [complaint_in_other_business_area.id], business_area.slug)

    complaint_in_other_business_area.refresh_from_db()

    assert complaint_in_other_business_area.status == GrievanceTicket.STATUS_FOR_APPROVAL
