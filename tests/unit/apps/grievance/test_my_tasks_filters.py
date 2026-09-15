import pytest

from extras.test_utils.factories import GrievanceTicketFactory, UserFactory
from hope.apps.grievance.filters import GrievanceTicketFilter
from hope.apps.grievance.models import GrievanceTicket
from hope.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def sensitive_ticket() -> GrievanceTicket:
    return GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
    )


@pytest.fixture
def complaint_ticket() -> GrievanceTicket:
    return GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_FSP_COMPLAINT,
    )


@pytest.fixture
def assignee() -> User:
    return UserFactory()


@pytest.fixture
def assigned_ticket(assignee: User) -> GrievanceTicket:
    return GrievanceTicketFactory(assigned_to=assignee)


@pytest.fixture
def unassigned_ticket() -> GrievanceTicket:
    return GrievanceTicketFactory(assigned_to=None)


def test_sensitive_filter_set_to_true_returns_only_sensitive_tickets(
    sensitive_ticket: GrievanceTicket, complaint_ticket: GrievanceTicket
) -> None:
    result = GrievanceTicketFilter(data={"sensitive": "true"}, queryset=GrievanceTicket.objects.all()).qs

    assert sensitive_ticket in result
    assert complaint_ticket not in result


def test_sensitive_filter_set_to_false_excludes_sensitive_tickets(
    sensitive_ticket: GrievanceTicket, complaint_ticket: GrievanceTicket
) -> None:
    result = GrievanceTicketFilter(data={"sensitive": "false"}, queryset=GrievanceTicket.objects.all()).qs

    assert complaint_ticket in result
    assert sensitive_ticket not in result


def test_omitting_the_sensitive_filter_returns_every_ticket(
    sensitive_ticket: GrievanceTicket, complaint_ticket: GrievanceTicket
) -> None:
    result = GrievanceTicketFilter(data={}, queryset=GrievanceTicket.objects.all()).qs

    assert sensitive_ticket in result
    assert complaint_ticket in result


def test_unassigned_filter_set_to_true_returns_only_tickets_with_no_assignee(
    unassigned_ticket: GrievanceTicket, assigned_ticket: GrievanceTicket
) -> None:
    result = GrievanceTicketFilter(data={"unassigned": "true"}, queryset=GrievanceTicket.objects.all()).qs

    assert unassigned_ticket in result
    assert assigned_ticket not in result


def test_unassigned_filter_set_to_false_returns_only_assigned_tickets(
    unassigned_ticket: GrievanceTicket, assigned_ticket: GrievanceTicket
) -> None:
    result = GrievanceTicketFilter(data={"unassigned": "false"}, queryset=GrievanceTicket.objects.all()).qs

    assert assigned_ticket in result
    assert unassigned_ticket not in result


def test_sensitive_and_assigned_to_compose_into_the_mine_sensitive_preset(
    assignee: User, sensitive_ticket: GrievanceTicket
) -> None:
    sensitive_ticket.assigned_to = assignee
    sensitive_ticket.save(update_fields=["assigned_to"])
    someone_elses_sensitive = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
    )

    result = GrievanceTicketFilter(
        data={"sensitive": "true", "assigned_to": str(assignee.pk)},
        queryset=GrievanceTicket.objects.all(),
    ).qs

    assert sensitive_ticket in result
    assert someone_elses_sensitive not in result
