from unittest.mock import MagicMock, patch

import pytest

from hope.apps.grievance.api.views import GrievanceTicketGlobalViewSet
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.notifications import GrievanceNotification
import hope.apps.household.api.serializers.household  # noqa: F401 - resolve circular import


@pytest.fixture
def mock_user():
    return MagicMock()


@pytest.fixture
def mock_ticket():
    return MagicMock()


@pytest.fixture
def mock_old_ticket():
    return MagicMock()


@pytest.fixture
def mock_viewset():
    mock_self = MagicMock(spec=GrievanceTicketGlobalViewSet)
    mock_self.get_permissions_for_status_change = MagicMock(return_value=[])
    mock_self.business_area = MagicMock()
    return mock_self


@patch("hope.apps.grievance.api.views.check_creator_or_owner_permission")
def test_validate_preconditions_no_permissions_needed(mock_check_permission, mock_viewset, mock_user, mock_ticket):
    mock_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
    mock_ticket.is_feedback = False
    mock_ticket.assigned_to = MagicMock()
    mock_ticket.can_change_status = MagicMock(return_value=True)

    GrievanceTicketGlobalViewSet._validate_status_change_preconditions(
        mock_viewset, mock_user, mock_ticket, GrievanceTicket.STATUS_FOR_APPROVAL, []
    )

    mock_check_permission.assert_not_called()


@patch("hope.apps.grievance.api.views.clear_cache")
def test_build_notifications_no_matching_status(mock_clear_cache, mock_user, mock_ticket, mock_old_ticket):
    mock_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
    mock_old_ticket.status = GrievanceTicket.STATUS_ASSIGNED
    notifications = []

    GrievanceTicketGlobalViewSet._build_status_change_notifications(
        mock_user, mock_old_ticket, mock_ticket, notifications
    )

    assert len(notifications) == 0
    mock_clear_cache.assert_not_called()


@patch("hope.apps.grievance.api.views.clear_cache")
@patch.object(GrievanceNotification, "_prepare_emails", return_value=[])
@patch.object(GrievanceNotification, "_prepare_user_recipients", return_value=[])
def test_build_notifications_for_approval(
    mock_recipients, mock_emails, mock_clear_cache, mock_user, mock_ticket, mock_old_ticket
):
    mock_ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
    mock_old_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
    notifications = []

    GrievanceTicketGlobalViewSet._build_status_change_notifications(
        mock_user, mock_old_ticket, mock_ticket, notifications
    )

    assert len(notifications) == 1
    assert notifications[0].action == GrievanceNotification.ACTION_SEND_TO_APPROVAL


@patch("hope.apps.grievance.api.views.clear_cache")
def test_build_notifications_back_to_in_progress(mock_clear_cache, mock_user, mock_ticket, mock_old_ticket):
    mock_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
    mock_old_ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
    notifications = []

    GrievanceTicketGlobalViewSet._build_status_change_notifications(
        mock_user, mock_old_ticket, mock_ticket, notifications
    )

    assert len(notifications) == 1
    assert notifications[0].action == GrievanceNotification.ACTION_SEND_BACK_TO_IN_PROGRESS
