"""Tests for grievance ticket choices endpoints."""

from typing import Any

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import BusinessAreaFactory, PartnerFactory, UserFactory
from extras.test_utils.factories.household import DocumentTypeFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.utils import to_choice_object
from hope.apps.grievance.constants import PRIORITY_CHOICES, URGENCY_CHOICES
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, DocumentType, Partner, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="AFG")


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def authenticated_client(api_client: Any, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def choices_url() -> str:
    return "api:grievance:grievance-tickets-global-choices"


@pytest.fixture
def document_types() -> None:
    DocumentTypeFactory(key="passport", label="Passport")
    DocumentTypeFactory(key="id_card", label="ID Card")
    DocumentTypeFactory(key="birth_certificate", label="Birth Certificate")


def test_get_choices_without_permissions(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    choices_url: str,
    document_types: None,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_FINISH],
        afghanistan,
    )
    response = authenticated_client.get(reverse(choices_url, kwargs={"business_area_slug": afghanistan.slug}))
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_choices(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    choices_url: str,
    document_types: None,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
        afghanistan,
    )
    response = authenticated_client.get(reverse(choices_url, kwargs={"business_area_slug": afghanistan.slug}))
    categories = dict(GrievanceTicket.CATEGORY_CHOICES)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "grievance_ticket_status_choices": to_choice_object(GrievanceTicket.STATUS_CHOICES),
        "grievance_ticket_category_choices": to_choice_object(GrievanceTicket.CATEGORY_CHOICES),
        "grievance_ticket_manual_category_choices": to_choice_object(GrievanceTicket.CREATE_CATEGORY_CHOICES),
        "grievance_ticket_system_category_choices": to_choice_object(GrievanceTicket.SYSTEM_CATEGORIES),
        "grievance_ticket_priority_choices": to_choice_object(PRIORITY_CHOICES),
        "grievance_ticket_urgency_choices": to_choice_object(URGENCY_CHOICES),
        "grievance_ticket_issue_type_choices": [
            {"category": key, "label": categories[key], "sub_categories": value}
            for (key, value) in GrievanceTicket.ISSUE_TYPES_CHOICES.items()
        ],
        "document_type_choices": [
            {"name": str(document_type.label), "value": document_type.key}
            for document_type in DocumentType.objects.order_by("key")
        ],
    }
