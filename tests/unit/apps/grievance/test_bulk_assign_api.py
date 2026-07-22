from typing import Any, Callable
from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from extras.test_utils.factories.geo import CountryFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, Partner, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def user2(partner: Partner) -> User:
    return UserFactory(first_name="SecondUser", partner=partner)


@pytest.fixture
def afghanistan() -> BusinessArea:
    CountryFactory(name="Afghanistan", short_name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="0004")
    CountryFactory(name="Poland", short_name="Poland", iso_code2="PL", iso_code3="POL", iso_num="0616")
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="program afghanistan 1",
    )


@pytest.fixture
def bulk_grievance_tickets(
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    user2: User,
) -> tuple:
    ticket1 = GrievanceTicketFactory(
        description="Test 1",
        assigned_to=user,
        priority=1,
        urgency=1,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        language="PL",
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        created_by=user2,
        business_area=afghanistan,
        issue_type=GrievanceTicket.ISSUE_TYPE_OTHER_COMPLAINT,
    )
    ticket1.programs.set([program])

    ticket2 = GrievanceTicketFactory(
        description="Test 2",
        assigned_to=user,
        priority=1,
        urgency=1,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        language="PL",
        status=GrievanceTicket.STATUS_NEW,
        created_by=user2,
        business_area=afghanistan,
        issue_type=GrievanceTicket.ISSUE_TYPE_OTHER_COMPLAINT,
    )
    ticket2.programs.set([program])

    return (ticket1, ticket2)


@pytest.fixture
def bulk_assign_url(afghanistan: BusinessArea) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-bulk-update-assignee",
        kwargs={"business_area_slug": afghanistan.slug},
    )


@pytest.mark.usefixtures("mock_elasticsearch")
@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [
                Permissions.PROGRAMME_UPDATE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            ],
            status.HTTP_403_FORBIDDEN,
        ),
        (
            [
                Permissions.GRIEVANCES_UPDATE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            ],
            status.HTTP_202_ACCEPTED,
        ),
    ],
)
def test_bulk_update_grievance_assignee(
    api_client: Any,
    user: User,
    user2: User,
    afghanistan: BusinessArea,
    program: Program,
    bulk_grievance_tickets: tuple,
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, permissions, afghanistan, program=program)

    ticket1, ticket2 = bulk_grievance_tickets

    url_list = reverse(
        "api:grievance:grievance-tickets-list",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_code": program.code,
        },
    )

    client = api_client(user)

    response_list_before = client.get(url_list, {"category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT})
    assert response_list_before.status_code == status.HTTP_200_OK
    assert len(response_list_before.json()["results"]) == 2
    for ticket in response_list_before.json()["results"]:
        assert ticket["assigned_to"]["id"] == str(user.id)

    # Bulk update assignee
    data = {
        "assigned_to": str(user2.id),
        "grievance_ticket_ids": [
            str(ticket1.id),
            str(ticket2.id),
        ],
    }

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-bulk-update-assignee",
        kwargs={"business_area_slug": afghanistan.slug},
    )

    response = client.post(url, data, format="json")

    resp_data = response.json()
    assert response.status_code == expected_status

    if expected_status == status.HTTP_202_ACCEPTED:
        assert len(resp_data) == 2
        assert resp_data[0]["assigned_to"]["first_name"] == "SecondUser"
        assert resp_data[1]["assigned_to"]["first_name"] == "SecondUser"

    # Check list after bulk update
    response_list_after = client.get(url_list, {"category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT})
    assert response_list_after.status_code == status.HTTP_200_OK
    assert len(response_list_after.json()["results"]) == 2

    if expected_status == status.HTTP_202_ACCEPTED:
        for ticket in response_list_after.json()["results"]:
            assert ticket["assigned_to"]["id"] == str(user2.id)
    else:
        for ticket in response_list_after.json()["results"]:
            assert ticket["assigned_to"]["id"] == str(user.id)


def test_bulk_assign_endpoint_enqueues_notification_for_new_assignee(
    api_client: Any,
    user: User,
    user2: User,
    afghanistan: BusinessArea,
    program: Program,
    bulk_grievance_tickets: tuple,
    bulk_assign_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_UPDATE], afghanistan, program=program)
    ticket1, ticket2 = bulk_grievance_tickets
    client = api_client(user)

    with patch("hope.apps.grievance.services.bulk_action_service.bulk_assign_notifications_async_task") as mock_enqueue:
        response = client.post(
            bulk_assign_url,
            {
                "grievance_ticket_ids": [str(ticket1.id), str(ticket2.id)],
                "assigned_to": str(user2.id),
            },
            format="json",
        )

    assert response.status_code == status.HTTP_202_ACCEPTED

    reassigned_ids, action_user_id = mock_enqueue.call_args.args
    assert set(reassigned_ids) == {ticket1.id, ticket2.id}
    assert action_user_id == user.id
