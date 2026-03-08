from unittest.mock import MagicMock, patch

import pytest

from hope.apps.grievance.api.mixins import GrievanceMutationMixin
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.notifications import GrievanceNotification


@pytest.fixture
def mock_approver():
    return MagicMock()


@pytest.fixture
def mock_ticket():
    return MagicMock()


@pytest.fixture
def mock_mixin_self():
    mock_self = MagicMock(spec=GrievanceMutationMixin)
    mock_self._set_status_based_on_assigned_to = MagicMock()
    return mock_self


@pytest.fixture
def mock_assigned_to():
    return MagicMock()


@patch("hope.apps.grievance.api.mixins.create_grievance_documents")
@patch("hope.apps.grievance.api.mixins.update_grievance_documents")
@patch("hope.apps.grievance.api.mixins.delete_grievance_documents")
def test_handle_document_operations_no_documents(mock_delete, mock_update, mock_create, mock_approver, mock_ticket):
    GrievanceMutationMixin._handle_document_operations(mock_approver, mock_ticket, {})

    mock_delete.assert_not_called()
    mock_update.assert_not_called()
    mock_create.assert_not_called()


def test_apply_ticket_field_updates_priority_unchanged(mock_ticket):
    mock_ticket.priority = 1

    GrievanceMutationMixin._apply_ticket_field_updates(mock_ticket, {"priority": 1})

    assert mock_ticket.priority == 1


def test_apply_ticket_field_updates_urgency_unchanged(mock_ticket):
    mock_ticket.urgency = 2

    GrievanceMutationMixin._apply_ticket_field_updates(mock_ticket, {"urgency": 2})

    assert mock_ticket.urgency == 2


def test_apply_ticket_field_updates_existing_field_not_overwritten(mock_ticket):
    mock_ticket.priority = 0
    mock_ticket.urgency = 0
    mock_ticket.description = "old"

    GrievanceMutationMixin._apply_ticket_field_updates(mock_ticket, {"description": "new"})

    assert mock_ticket.description == "old"


def test_handle_assignment_change_same_assignee_for_approval(
    mock_mixin_self, mock_approver, mock_ticket, mock_assigned_to
):
    mock_ticket.assigned_to = mock_assigned_to
    mock_ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
    messages = []

    GrievanceMutationMixin._handle_assignment_change(
        mock_mixin_self, mock_approver, mock_ticket, mock_assigned_to, messages
    )

    assert mock_ticket.status == GrievanceTicket.STATUS_IN_PROGRESS
    assert len(messages) == 1
    assert messages[0].action == GrievanceNotification.ACTION_SEND_BACK_TO_IN_PROGRESS
