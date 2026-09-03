"""Tests for grievance ticket choices endpoints."""

from typing import Any

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import PartnerFactory, UserFactory
from hope.apps.core.utils import to_choice_object
from hope.apps.grievance.constants import (
    PRIORITY_CHOICES,
    SUBMISSION_CHANNEL_CHOICES,
    SUBMISSION_CHANNEL_MANUAL_CHOICES,
    URGENCY_CHOICES,
)
from hope.apps.grievance.models import GrievanceTicket

pytestmark = pytest.mark.django_db


def test_get_choices_returns_choices_for_user_without_any_role(api_client: Any) -> None:
    client = api_client(UserFactory(partner=PartnerFactory(name="TestPartner")))

    response = client.get(reverse("api:choices-grievance-tickets"))

    categories = dict(GrievanceTicket.CATEGORY_CHOICES)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "grievance_ticket_status_choices": to_choice_object(GrievanceTicket.STATUS_CHOICES),
        "grievance_ticket_category_choices": to_choice_object(GrievanceTicket.CATEGORY_CHOICES),
        "grievance_ticket_manual_category_choices": to_choice_object(GrievanceTicket.CREATE_CATEGORY_CHOICES),
        "grievance_ticket_filter_category_choices": to_choice_object(GrievanceTicket.MANUAL_CATEGORIES),
        "grievance_ticket_system_category_choices": to_choice_object(GrievanceTicket.SYSTEM_CATEGORIES),
        "grievance_ticket_priority_choices": to_choice_object(PRIORITY_CHOICES),
        "grievance_ticket_urgency_choices": to_choice_object(URGENCY_CHOICES),
        "grievance_ticket_submission_channel_choices": to_choice_object(SUBMISSION_CHANNEL_CHOICES),
        "grievance_ticket_manual_submission_channel_choices": to_choice_object(SUBMISSION_CHANNEL_MANUAL_CHOICES),
        "grievance_ticket_issue_type_choices": [
            {"category": key, "label": categories[key], "sub_categories": value}
            for (key, value) in GrievanceTicket.ISSUE_TYPES_CHOICES.items()
        ],
    }


def test_get_choices_denies_anonymous_access() -> None:
    response = APIClient().get(reverse("api:choices-grievance-tickets"))

    assert response.status_code == status.HTTP_403_FORBIDDEN
