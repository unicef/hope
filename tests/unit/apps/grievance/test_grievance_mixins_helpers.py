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


def test_apply_ticket_field_updates_priority_unchanged(mock_ticket, mock_approver):
    mock_ticket.priority = 1

    GrievanceMutationMixin._apply_ticket_field_updates(mock_ticket, {"priority": 1}, mock_approver)

    assert mock_ticket.priority == 1


def test_apply_ticket_field_updates_urgency_unchanged(mock_ticket, mock_approver):
    mock_ticket.urgency = 2

    GrievanceMutationMixin._apply_ticket_field_updates(mock_ticket, {"urgency": 2}, mock_approver)

    assert mock_ticket.urgency == 2


def test_apply_ticket_field_updates_existing_field_not_overwritten(mock_ticket, mock_approver):
    mock_ticket.priority = 0
    mock_ticket.urgency = 0
    mock_ticket.description = "old"

    GrievanceMutationMixin._apply_ticket_field_updates(mock_ticket, {"description": "new"}, mock_approver)

    assert mock_ticket.description == "old"


def test_handle_assignment_change_same_assignee_for_approval(
    mock_mixin_self, mock_approver, mock_ticket, mock_assigned_to
):
    mock_ticket.assigned_to = mock_assigned_to
    mock_ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
    messages = []

    GrievanceMutationMixin._handle_assignment_change(
        mock_mixin_self, mock_approver, mock_ticket, mock_assigned_to, messages, assignment_provided=True
    )

    assert mock_ticket.status == GrievanceTicket.STATUS_IN_PROGRESS
    assert len(messages) == 1
    assert messages[0].action == GrievanceNotification.ACTION_SEND_BACK_TO_IN_PROGRESS


@pytest.mark.django_db
def test_list_without_pagination_falls_back_to_default_list():
    from rest_framework import serializers
    from rest_framework.mixins import ListModelMixin
    from rest_framework.test import APIRequestFactory
    from rest_framework.viewsets import GenericViewSet

    from extras.test_utils.factories.grievance import GrievanceTicketFactory
    from hope.apps.grievance.api.mixins import GrievanceListBatchMixin

    ticket = GrievanceTicketFactory(household_unicef_id="HH-0000-0000.0009")

    class UnicefIdSerializer(serializers.ModelSerializer):
        class Meta:
            model = GrievanceTicket
            fields = ("unicef_id",)

    class UnpaginatedViewSet(GrievanceListBatchMixin, ListModelMixin, GenericViewSet):
        queryset = GrievanceTicket.objects.all()
        serializer_class = UnicefIdSerializer
        pagination_class = None

    view = UnpaginatedViewSet(kwargs={}, args=(), format_kwarg=None)
    view.request = APIRequestFactory().get("/")

    response = view.list(view.request)

    assert response.data == [{"unicef_id": ticket.unicef_id}]
    assert view.fallback_individual_unicef_ids is None
    assert view.existing_tickets_counts is None
