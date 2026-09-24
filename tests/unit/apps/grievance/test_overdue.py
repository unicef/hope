from datetime import UTC, datetime

from constance.test import override_config
from freezegun import freeze_time
import pytest

from extras.test_utils.factories import GrievanceTicketFactory
from hope.apps.grievance.filters import GrievanceTicketFilter
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.utils import overdue_q

pytestmark = pytest.mark.django_db

NOW = datetime(2026, 8, 24, 12, 0, tzinfo=UTC)
TWO_DAYS_AGO = datetime(2026, 8, 22, 12, 0, tzinfo=UTC)
SIX_HOURS_AGO = datetime(2026, 8, 24, 6, 0, tzinfo=UTC)
FOUR_DAYS_AGO = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)
LAST_MONTH = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)


@pytest.fixture
def overdue_sensitive_ticket() -> GrievanceTicket:
    with freeze_time(TWO_DAYS_AGO):
        return GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
        )


@pytest.fixture
def recent_sensitive_ticket() -> GrievanceTicket:
    with freeze_time(SIX_HOURS_AGO):
        return GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
        )


@pytest.fixture
def overdue_ticket() -> GrievanceTicket:
    with freeze_time(LAST_MONTH):
        return GrievanceTicketFactory()


@pytest.fixture
def recent_ticket() -> GrievanceTicket:
    with freeze_time(FOUR_DAYS_AGO):
        return GrievanceTicketFactory()


@freeze_time(NOW)
def test_sensitive_ticket_past_its_threshold_is_overdue(overdue_sensitive_ticket: GrievanceTicket) -> None:
    overdue = GrievanceTicket.objects.filter(overdue_q())

    assert overdue_sensitive_ticket in overdue


@freeze_time(NOW)
def test_sensitive_ticket_within_its_threshold_is_not_overdue(recent_sensitive_ticket: GrievanceTicket) -> None:
    overdue = GrievanceTicket.objects.filter(overdue_q())

    assert recent_sensitive_ticket not in overdue


@freeze_time(NOW)
def test_non_sensitive_ticket_past_its_threshold_is_overdue(overdue_ticket: GrievanceTicket) -> None:
    overdue = GrievanceTicket.objects.filter(overdue_q())

    assert overdue_ticket in overdue


@freeze_time(NOW)
def test_non_sensitive_ticket_within_its_threshold_is_not_overdue(recent_ticket: GrievanceTicket) -> None:
    overdue = GrievanceTicket.objects.filter(overdue_q())

    assert recent_ticket not in overdue


@freeze_time(NOW)
def test_a_four_day_old_sensitive_ticket_is_overdue_while_a_non_sensitive_one_is_not(
    recent_ticket: GrievanceTicket, overdue_sensitive_ticket: GrievanceTicket
) -> None:
    overdue = GrievanceTicket.objects.filter(overdue_q())

    assert overdue_sensitive_ticket in overdue
    assert recent_ticket not in overdue


@freeze_time(NOW)
@override_config(GRIEVANCE_OVERDUE_THRESHOLD_NON_SENSITIVE=2)
def test_lowering_the_non_sensitive_threshold_makes_a_recent_ticket_overdue(
    recent_ticket: GrievanceTicket,
) -> None:
    overdue = GrievanceTicket.objects.filter(overdue_q())

    assert recent_ticket in overdue


@freeze_time(NOW)
@override_config(GRIEVANCE_OVERDUE_THRESHOLD_SENSITIVE=7)
def test_raising_the_sensitive_threshold_makes_an_overdue_ticket_current(
    overdue_sensitive_ticket: GrievanceTicket,
) -> None:
    overdue = GrievanceTicket.objects.filter(overdue_q())

    assert overdue_sensitive_ticket not in overdue


@freeze_time(NOW)
def test_overdue_filter_set_to_true_returns_only_overdue_tickets(
    overdue_ticket: GrievanceTicket, recent_ticket: GrievanceTicket
) -> None:
    result = GrievanceTicketFilter(data={"overdue": "true"}, queryset=GrievanceTicket.objects.all()).qs

    assert overdue_ticket in result
    assert recent_ticket not in result


@freeze_time(NOW)
def test_overdue_filter_set_to_false_excludes_overdue_tickets(
    overdue_ticket: GrievanceTicket, recent_ticket: GrievanceTicket
) -> None:
    result = GrievanceTicketFilter(data={"overdue": "false"}, queryset=GrievanceTicket.objects.all()).qs

    assert recent_ticket in result
    assert overdue_ticket not in result


@freeze_time(NOW)
def test_omitting_the_overdue_filter_returns_every_ticket(
    overdue_ticket: GrievanceTicket, recent_ticket: GrievanceTicket
) -> None:
    result = GrievanceTicketFilter(data={}, queryset=GrievanceTicket.objects.all()).qs

    assert overdue_ticket in result
    assert recent_ticket in result
