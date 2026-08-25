from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import BusinessAreaFactory, UserFactory
from extras.test_utils.factories.grievance import TicketComplaintDetailsFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def user() -> User:
    return UserFactory(first_name="user")


@pytest.fixture
def complaint_for_approval(business_area: BusinessArea, user: User) -> GrievanceTicket:
    return TicketComplaintDetailsFactory(
        ticket__business_area=business_area,
        ticket__created_by=user,
        ticket__status=GrievanceTicket.STATUS_FOR_APPROVAL,
    ).ticket


@pytest.fixture
def complaint_owned_by_user(business_area: BusinessArea, user: User) -> GrievanceTicket:
    return TicketComplaintDetailsFactory(
        ticket__business_area=business_area,
        ticket__created_by=UserFactory(first_name="other"),
        ticket__assigned_to=user,
        ticket__status=GrievanceTicket.STATUS_FOR_APPROVAL,
    ).ticket


@pytest.fixture
def bulk_close_url(business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-bulk-close",
        kwargs={"business_area_slug": business_area.slug},
    )


def test_bulk_close_forbidden_without_close_permission(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    complaint_for_approval: GrievanceTicket,
    bulk_close_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        business_area,
        whole_business_area_access=True,
    )

    client = api_client(user)
    response = client.post(
        bulk_close_url,
        {"grievance_ticket_ids": [str(complaint_for_approval.id)]},
        format="json",
    )

    complaint_for_approval.refresh_from_db()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert complaint_for_approval.status == GrievanceTicket.STATUS_FOR_APPROVAL


def test_bulk_close_allowed_with_close_permission(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    complaint_for_approval: GrievanceTicket,
    bulk_close_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK],
        business_area,
        whole_business_area_access=True,
    )

    client = api_client(user)
    response = client.post(
        bulk_close_url,
        {"grievance_ticket_ids": [str(complaint_for_approval.id)]},
        format="json",
    )

    complaint_for_approval.refresh_from_db()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert complaint_for_approval.status == GrievanceTicket.STATUS_CLOSED
    assert len(response.data) == 1
    assert response.data[0]["id"] == str(complaint_for_approval.id)
    assert response.data[0]["status"] == GrievanceTicket.STATUS_CLOSED


def test_bulk_close_forbidden_as_creator_when_not_creator(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    complaint_owned_by_user: GrievanceTicket,
    bulk_close_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    # user is the owner but only holds the AS_CREATOR permission, and is not the creator
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR],
        business_area,
        whole_business_area_access=True,
    )

    client = api_client(user)
    response = client.post(
        bulk_close_url,
        {"grievance_ticket_ids": [str(complaint_owned_by_user.id)]},
        format="json",
    )

    complaint_owned_by_user.refresh_from_db()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert complaint_owned_by_user.status == GrievanceTicket.STATUS_FOR_APPROVAL


def test_bulk_close_forbidden_as_owner_when_not_owner(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    complaint_for_approval: GrievanceTicket,
    bulk_close_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    # user is the creator but only holds the AS_OWNER permission, and is not the owner
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER],
        business_area,
        whole_business_area_access=True,
    )

    client = api_client(user)
    response = client.post(
        bulk_close_url,
        {"grievance_ticket_ids": [str(complaint_for_approval.id)]},
        format="json",
    )

    complaint_for_approval.refresh_from_db()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert complaint_for_approval.status == GrievanceTicket.STATUS_FOR_APPROVAL
