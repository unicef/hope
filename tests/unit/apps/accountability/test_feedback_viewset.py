"""Tests for Feedback ViewSet."""

import datetime
from typing import Any, List

from django.urls import reverse
from django.utils import timezone
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    AreaFactory,
    BusinessAreaFactory,
    FeedbackFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(code="0060", slug="afghanistan", name="Afghanistan", active=True)


@pytest.fixture
def partner():
    return PartnerFactory(name="unittest")


@pytest.fixture
def user(partner, business_area):
    u = UserFactory(partner=partner, first_name="Test", last_name="User")
    partner.allowed_business_areas.add(business_area)
    return u


@pytest.fixture
def authenticated_client(api_client, user):
    return api_client(user)


@pytest.fixture
def program_active(business_area):
    return ProgramFactory(
        name="Test Active Program",
        business_area=business_area,
        status=Program.ACTIVE,
    )


@pytest.fixture
def program_finished(business_area):
    return ProgramFactory(
        name="Test Finished Program",
        business_area=business_area,
        status=Program.FINISHED,
    )


@pytest.fixture
def program_2(business_area):
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def household_1(program_active, business_area):
    return HouseholdFactory(program=program_active, business_area=business_area)


@pytest.fixture
def individual_1(household_1, business_area):
    return IndividualFactory(
        household=household_1,
        program=household_1.program,
        business_area=business_area,
        registration_data_import=household_1.registration_data_import,
    )


@pytest.fixture
def area_1():
    return AreaFactory(name="AREA_name")


@pytest.fixture
def area_2():
    return AreaFactory(name="Wroclaw")


@pytest.fixture
def user_creator(partner):
    return UserFactory(first_name="Creator", last_name="User", partner=partner)


@pytest.fixture
def feedback_1(program_active, household_1, individual_1, user, area_1):
    return FeedbackFactory(
        program=program_active,
        household_lookup=household_1,
        individual_lookup=individual_1,
        created_by=user,
        description="test description 111",
        area="test area 111",
        language="test language 111",
        comments="test comments 111",
        issue_type="NEGATIVE_FEEDBACK",
        admin2=area_1,
        business_area=program_active.business_area,
    )


@pytest.fixture
def feedback_2(household_1, individual_1, user, area_1, business_area):
    return FeedbackFactory(
        program=None,
        household_lookup=household_1,
        individual_lookup=individual_1,
        created_by=user,
        issue_type="POSITIVE_FEEDBACK",
        description="test description",
        area="test area",
        language="test language",
        comments="test comments",
        admin2=area_1,
        business_area=business_area,
    )


@pytest.fixture
def feedback_with_finished_program(program_finished, household_1, individual_1, user, area_1, business_area):
    return FeedbackFactory(
        program=program_finished,
        household_lookup=household_1,
        individual_lookup=individual_1,
        created_by=user,
        issue_type="POSITIVE_FEEDBACK",
        description="test description finished",
        area="test area finished",
        language="test language finished",
        comments="test comments finished",
        admin2=area_1,
        business_area=business_area,
    )


@pytest.fixture
def feedback_3(program_2, user_creator):
    return FeedbackFactory(
        program=program_2,
        issue_type="NEGATIVE_FEEDBACK",
        created_by=user_creator,
        business_area=program_2.business_area,
    )


@pytest.fixture
def url_list(business_area):
    return reverse(
        "api:accountability:feedbacks-list",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def url_count(business_area):
    return reverse(
        "api:accountability:feedbacks-count",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def url_details(business_area, feedback_2):
    return reverse(
        "api:accountability:feedbacks-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "pk": str(feedback_2.pk),
        },
    )


@pytest.fixture
def url_details_feedback_1(business_area, feedback_1):
    return reverse(
        "api:accountability:feedbacks-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "pk": str(feedback_1.pk),
        },
    )


@pytest.fixture
def url_msg_create(business_area, feedback_2):
    return reverse(
        "api:accountability:feedbacks-message",
        kwargs={
            "business_area_slug": business_area.slug,
            "pk": str(feedback_2.pk),
        },
    )


@pytest.fixture
def url_msg_create_for_feedback_1(business_area, feedback_1):
    return reverse(
        "api:accountability:feedbacks-message",
        kwargs={
            "business_area_slug": business_area.slug,
            "pk": str(feedback_1.pk),
        },
    )


@pytest.fixture
def url_list_per_program(business_area, program_active):
    return reverse(
        "api:accountability:feedbacks-per-program-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )


@pytest.fixture
def url_count_per_program(business_area, program_active):
    return reverse(
        "api:accountability:feedbacks-per-program-count",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )


@pytest.fixture
def url_details_per_program(business_area, program_active, feedback_1):
    return reverse(
        "api:accountability:feedbacks-per-program-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
            "pk": str(feedback_1.pk),
        },
    )


@pytest.fixture
def url_msg_create_per_program(business_area, program_active, feedback_1):
    return reverse(
        "api:accountability:feedbacks-per-program-message",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
            "pk": str(feedback_1.pk),
        },
    )


# per BA
@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [
                Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
                Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
            ],
            status.HTTP_200_OK,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_feedback_get_list(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    program_2,
    feedback_1,
    feedback_2,
    feedback_3,
    url_list,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    create_user_role_with_permissions(user, permissions, business_area, program_2)
    response = authenticated_client.get(url_list)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        response_results = response.json()["results"]
        assert len(response_results) == 3
        for i, feedback in enumerate([feedback_1, feedback_2, feedback_3]):
            feedback_result = response_results[i]
            assert feedback_result["id"] == str(feedback.id)
            assert feedback_result["issue_type"] == feedback.issue_type
            assert feedback_result["unicef_id"] == str(feedback.unicef_id)
            assert feedback_result["household_unicef_id"] == (
                str(feedback.household_lookup.unicef_id) if feedback.household_lookup else None
            )
            assert feedback_result["household_id"] == (
                str(feedback.household_lookup.id) if feedback.household_lookup else None
            )
            assert feedback_result["individual_unicef_id"] == (
                str(feedback.individual_lookup.unicef_id) if feedback.individual_lookup else None
            )
            assert feedback_result["individual_id"] == (
                str(feedback.individual_lookup.id) if feedback.individual_lookup else None
            )
            assert feedback_result["linked_grievance_id"] == (
                str(feedback.linked_grievance.id) if feedback.linked_grievance else None
            )
            assert feedback_result["linked_grievance_unicef_id"] == (
                str(feedback.linked_grievance.unicef_id) if feedback.linked_grievance else None
            )
            assert feedback_result["program_name"] == (feedback.program.name if feedback.program else None)
            assert feedback_result["program_id"] == (str(feedback.program.id) if feedback.program else None)
            assert feedback_result["created_by"] == f"{feedback.created_by.first_name} {feedback.created_by.last_name}"
            assert feedback_result["created_at"] == f"{feedback.created_at:%Y-%m-%dT%H:%M:%SZ}"
            assert feedback_result["feedback_messages"] == []


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [
                Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
                Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
            ],
            status.HTTP_200_OK,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_feedback_get_count(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    program_2,
    feedback_1,
    feedback_2,
    feedback_3,
    url_count,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.get(url_count)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["count"] == 2

        # add permissions to second program
        create_user_role_with_permissions(user, permissions, business_area, program_2)
        response = authenticated_client.get(url_count)
        resp_data = response.json()
        assert resp_data["count"] == 3


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [
                Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
                Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
            ],
            status.HTTP_200_OK,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_feedback_details(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    area_1,
    url_details,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.get(url_details)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["admin2"] == {
            "id": str(area_1.id),
            "name": "AREA_name",
        }
        assert resp_data["household_unicef_id"] is not None
        assert resp_data["household_id"] is not None
        assert resp_data["individual_unicef_id"] is not None
        assert resp_data["individual_id"] is not None
        assert resp_data["program_name"] is None
        assert resp_data["program_id"] is None
        assert resp_data["created_by"] == "Test User"
        assert resp_data["description"] == "test description"
        assert resp_data["area"] == "test area"
        assert resp_data["language"] == "test language"
        assert resp_data["comments"] == "test comments"
        assert resp_data["admin_url"] is None


def test_feedback_details_admin_url(
    authenticated_client,
    user,
    feedback_2,
    url_details,
) -> None:
    user.is_superuser = True
    user.save()
    response = authenticated_client.get(url_details)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["admin_url"] == f"/api/unicorn/accountability/feedback/{str(feedback_2.id)}/change/"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE], status.HTTP_201_CREATED),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_feedback(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    household_1,
    area_1,
    url_list,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.post(
        url_list,
        {
            "area": "Area 1",
            "comments": "Test Comments",
            "consent": True,
            "description": "Test new description",
            "household_lookup": str(household_1.pk),
            "issue_type": "POSITIVE_FEEDBACK",
            "admin2": str(area_1.pk),
            "language": "polish",
            "program_id": str(program_active.pk),
        },
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["admin2"] == {
            "id": str(area_1.id),
            "name": "AREA_name",
        }
        assert resp_data["issue_type"] == "POSITIVE_FEEDBACK"
        assert resp_data["household_id"] is not None
        assert resp_data["household_unicef_id"] is not None
        assert resp_data["individual_unicef_id"] is None
        assert resp_data["individual_id"] is None
        assert resp_data["program_name"] == household_1.program.name
        assert resp_data["program_id"] is not None
        assert resp_data["created_by"] == "Test User"
        assert resp_data["description"] == "Test new description"
        assert resp_data["area"] == "Area 1"
        assert resp_data["language"] == "polish"
        assert resp_data["comments"] == "Test Comments"


def test_create_feedback_without_permission_in_program(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    program_2,
    household_1,
    area_1,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE],
        business_area,
        program_2,
    )
    response = authenticated_client.post(
        url_list,
        {
            "area": "Area 1",
            "comments": "Test Comments",
            "consent": True,
            "description": "Test new description",
            "household_lookup": str(household_1.pk),
            "issue_type": "POSITIVE_FEEDBACK",
            "admin2": str(area_1.pk),
            "language": "polish",
            "program_id": str(program_active.pk),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE],
            status.HTTP_400_BAD_REQUEST,
        ),
    ],
)
def test_create_feedback_for_finished_program(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    household_1,
    area_1,
    url_list,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    program_finished = ProgramFactory(
        name="Test Finished Program",
        business_area=business_area,
        status=Program.FINISHED,
    )
    response = authenticated_client.post(
        url_list,
        {
            "area": "Area 1",
            "comments": "Test Comments",
            "consent": True,
            "description": "Test new description",
            "household_lookup": str(household_1.pk),
            "issue_type": "POSITIVE_FEEDBACK",
            "admin2": str(area_1.pk),
            "language": "polish",
            "program_id": str(program_finished.pk),
        },
        format="json",
    )
    assert response.status_code == expected_status
    assert "It is not possible to create Feedback for a Finished Program." in response.json()


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE], status.HTTP_201_CREATED),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_feedback_with_minimum_data(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    url_list,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.post(
        url_list,
        {
            "description": "small",
            "issue_type": "NEGATIVE_FEEDBACK",
        },
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["admin2"] is None
        assert resp_data["issue_type"] == "NEGATIVE_FEEDBACK"
        assert resp_data["household_id"] is None
        assert resp_data["household_unicef_id"] is None
        assert resp_data["individual_unicef_id"] is None
        assert resp_data["individual_id"] is None
        assert resp_data["program_name"] is None
        assert resp_data["program_id"] is None
        assert resp_data["created_by"] == "Test User"
        assert resp_data["description"] == "small"
        assert resp_data["area"] == ""
        assert resp_data["language"] == ""
        assert resp_data["comments"] is None
        assert resp_data["consent"] is True


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_update_feedback_without_program(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    individual_1,
    area_2,
    url_details,
    feedback_2,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.patch(
        url_details,
        {
            "issue_type": "NEGATIVE_FEEDBACK",
            "individual_lookup": str(individual_1.pk),
            "description": "Test_update",
            "comments": "AAA_update",
            "admin2": str(area_2.pk),
            "area": "Area 1_updated",
            "language": "eng_update",
            "consent": False,
        },
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["admin2"] == {
            "id": str(area_2.id),
            "name": "Wroclaw",
        }
        assert resp_data["issue_type"] == "NEGATIVE_FEEDBACK"
        assert resp_data["household_id"] is not None
        assert resp_data["household_unicef_id"] is not None
        assert resp_data["individual_unicef_id"] is not None
        assert resp_data["individual_id"] is not None
        assert resp_data["program_name"] is None
        assert resp_data["program_id"] is None
        assert resp_data["created_by"] == "Test User"
        assert resp_data["description"] == "Test_update"
        assert resp_data["area"] == "Area 1_updated"
        assert resp_data["language"] == "eng_update"
        assert resp_data["comments"] == "AAA_update"
        assert resp_data["consent"] is False


def test_update_feedback_with_program_with_permission_in_program(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    individual_1,
    area_2,
    url_details_feedback_1,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE],
        business_area,
        program_active,
    )
    response = authenticated_client.patch(
        url_details_feedback_1,
        {
            "issue_type": "NEGATIVE_FEEDBACK",
            "individual_lookup": str(individual_1.pk),
            "description": "Test_update",
            "comments": "AAA_update",
            "admin2": str(area_2.pk),
            "area": "Area 1_updated",
            "language": "eng_update",
            "consent": False,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK


def test_update_feedback_with_program_without_permission_in_program(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_2,
    individual_1,
    area_2,
    url_details_feedback_1,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE],
        business_area,
        program_2,
    )
    response = authenticated_client.patch(
        url_details_feedback_1,
        {
            "issue_type": "NEGATIVE_FEEDBACK",
            "individual_lookup": str(individual_1.pk),
            "description": "Test_update",
            "comments": "AAA_update",
            "admin2": str(area_2.pk),
            "area": "Area 1_updated",
            "language": "eng_update",
            "consent": False,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_update_feedback_hh_lookup(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    household_1,
    area_2,
    url_details,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.patch(
        url_details,
        {
            "issue_type": "NEGATIVE_FEEDBACK",
            "household_lookup": str(household_1.pk),
            "description": "Test_update",
            "comments": "AAA_update",
            "admin2": str(area_2.pk),
            "area": "Area 1_updated",
            "language": "eng_update",
            "consent": False,
        },
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["admin2"] == {
            "id": str(area_2.id),
            "name": "Wroclaw",
        }
        assert resp_data["issue_type"] == "NEGATIVE_FEEDBACK"
        assert resp_data["household_id"] is not None
        assert resp_data["household_unicef_id"] is not None
        assert resp_data["individual_unicef_id"] is not None
        assert resp_data["individual_id"] is not None
        assert resp_data["program_name"] is None
        assert resp_data["program_id"] is None
        assert resp_data["created_by"] == "Test User"
        assert resp_data["description"] == "Test_update"
        assert resp_data["area"] == "Area 1_updated"
        assert resp_data["language"] == "eng_update"
        assert resp_data["comments"] == "AAA_update"
        assert resp_data["consent"] is False


# per Program
@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [
                Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
                Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
            ],
            status.HTTP_200_OK,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_feedback_per_program(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    feedback_1,
    url_list_per_program,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.get(url_list_per_program)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        response_results = response.json()["results"]
        assert len(response_results) == 1
        feedback_result = response_results[0]
        assert feedback_result["id"] == str(feedback_1.id)
        assert feedback_result["issue_type"] == feedback_1.issue_type
        assert feedback_result["unicef_id"] == str(feedback_1.unicef_id)
        assert feedback_result["household_unicef_id"] == str(feedback_1.household_lookup.unicef_id)
        assert feedback_result["household_id"] == str(feedback_1.household_lookup.id)
        assert feedback_result["individual_unicef_id"] == str(feedback_1.individual_lookup.unicef_id)
        assert feedback_result["individual_id"] == str(feedback_1.individual_lookup.id)
        assert feedback_result["linked_grievance_id"] is None
        assert feedback_result["linked_grievance_unicef_id"] is None
        assert feedback_result["program_name"] == feedback_1.program.name
        assert feedback_result["program_id"] == str(feedback_1.program.id)
        assert feedback_result["created_by"] == f"{feedback_1.created_by.first_name} {feedback_1.created_by.last_name}"
        assert feedback_result["created_at"] == f"{feedback_1.created_at:%Y-%m-%dT%H:%M:%SZ}"
        assert feedback_result["feedback_messages"] == []


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [
                Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
                Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
            ],
            status.HTTP_200_OK,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_feedback_get_count_per_program(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    feedback_1,
    url_count_per_program,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, whole_business_area_access=True)
    response = authenticated_client.get(url_count_per_program)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["count"] == 1


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [
                Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
                Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
            ],
            status.HTTP_200_OK,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_feedback_details_per_program(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    area_1,
    url_details_per_program,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.get(url_details_per_program)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["admin2"] == {
            "id": str(area_1.id),
            "name": "AREA_name",
        }
        assert resp_data["household_unicef_id"] is not None
        assert resp_data["household_id"] is not None
        assert resp_data["individual_unicef_id"] is not None
        assert resp_data["individual_id"] is not None
        assert resp_data["program_name"] == "Test Active Program"
        assert resp_data["program_id"] is not None
        assert resp_data["created_by"] == "Test User"
        assert resp_data["description"] == "test description 111"
        assert resp_data["area"] == "test area 111"
        assert resp_data["language"] == "test language 111"
        assert resp_data["comments"] == "test comments 111"
        assert resp_data["admin_url"] is None


def test_feedback_details_per_program_admin_url(
    authenticated_client,
    user,
    feedback_2,
    url_details,
) -> None:
    user.is_superuser = True
    user.save()
    response = authenticated_client.get(url_details)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["admin_url"] == f"/api/unicorn/accountability/feedback/{str(feedback_2.id)}/change/"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE], status.HTTP_201_CREATED),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_feedback_per_program(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    individual_1,
    area_1,
    url_list_per_program,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.post(
        url_list_per_program,
        {
            "issue_type": "POSITIVE_FEEDBACK",
            "individual_lookup": str(individual_1.pk),
            "description": "Description per Program Create",
            "comments": "New comments per Program Create",
            "admin2": str(area_1.pk),
            "area": "Area new",
            "language": "polish_english",
        },
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["program_name"] == "Test Active Program"
        assert resp_data["description"] == "Description per Program Create"
        assert resp_data["comments"] == "New comments per Program Create"
        assert resp_data["admin2"] == {
            "id": str(area_1.id),
            "name": "AREA_name",
        }
        assert resp_data["area"] == "Area new"
        assert resp_data["language"] == "polish_english"
        assert resp_data["issue_type"] == "POSITIVE_FEEDBACK"
        assert resp_data["individual_unicef_id"] == str(individual_1.unicef_id)
        assert resp_data["individual_id"] == str(individual_1.id)


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_update_feedback_per_program(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    individual_1,
    area_1,
    url_details_per_program,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.patch(
        url_details_per_program,
        {
            "issue_type": "POSITIVE_FEEDBACK",
            "individual_lookup": str(individual_1.pk),
            "description": "new description",
            "comments": "new comments",
            "admin2": str(area_1.pk),
            "area": "Area new",
            "language": "polish_english",
        },
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["admin2"] == {
            "id": str(area_1.id),
            "name": "AREA_name",
        }
        assert resp_data["issue_type"] == "POSITIVE_FEEDBACK"
        assert resp_data["household_id"] is not None
        assert resp_data["household_unicef_id"] is not None
        assert resp_data["individual_unicef_id"] is not None
        assert resp_data["individual_id"] is not None
        assert resp_data["program_name"] is not None
        assert resp_data["program_id"] is not None
        assert resp_data["created_by"] == "Test User"
        assert resp_data["description"] == "new description"
        assert resp_data["area"] == "Area new"
        assert resp_data["language"] == "polish_english"
        assert resp_data["comments"] == "new comments"
        assert resp_data["consent"] is True


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE],
            status.HTTP_400_BAD_REQUEST,
        ),
    ],
)
def test_update_feedback_per_program_when_finished(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    individual_1,
    area_1,
    url_details_per_program,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    program_active.status = Program.FINISHED
    program_active.save()
    response = authenticated_client.patch(
        url_details_per_program,
        {
            "issue_type": "POSITIVE_FEEDBACK",
            "individual_lookup": str(individual_1.pk),
            "description": "new description",
            "comments": "new comments",
            "admin2": str(area_1.pk),
            "area": "Area new",
            "language": "polish_english",
        },
        format="json",
    )
    assert response.status_code == expected_status
    assert "It is not possible to update Feedback for a Finished Program." in response.json()


def test_list_feedback_issue_type(authenticated_client) -> None:
    response_data = authenticated_client.get(reverse("api:choices-feedback-issue-type")).data
    assert response_data is not None
    assert len(response_data) == 2
    assert "NEGATIVE_FEEDBACK" in response_data[0]["value"]
    assert "POSITIVE_FEEDBACK" in response_data[1]["value"]


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [
                Permissions.GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE,
                Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
            ],
            status.HTTP_201_CREATED,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_feedback_message(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    url_msg_create,
    url_details,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.post(
        url_msg_create,
        {"description": "Message for Feedback #1"},
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["description"] == "Message for Feedback #1"
        assert "created_by" in resp_data
        assert "id" in resp_data
        assert "created_at" in resp_data

        # check message details
        response_details = authenticated_client.get(url_details)
        assert response_details.status_code == status.HTTP_200_OK
        resp_data = response_details.json()
        assert "id" in resp_data
        assert len(resp_data["feedback_messages"]) == 1
        feedback_message = resp_data["feedback_messages"][0]
        assert feedback_message["description"] == "Message for Feedback #1"
        assert feedback_message["created_by"] == "Test User"
        assert "id" in feedback_message
        assert "created_at" in feedback_message


def test_create_feedback_message_with_program_with_permission_in_program(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    url_msg_create_for_feedback_1,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE],
        business_area,
        program_active,
    )
    response = authenticated_client.post(
        url_msg_create_for_feedback_1,
        {"description": "Message for Feedback #1"},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_create_feedback_message_with_program_without_permission_in_program(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_2,
    url_msg_create_for_feedback_1,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE],
        business_area,
        program_2,
    )
    response = authenticated_client.post(
        url_msg_create_for_feedback_1,
        {"description": "Message for Feedback #1"},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [
                Permissions.GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE,
                Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
            ],
            status.HTTP_201_CREATED,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_feedback_message_per_program(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    url_msg_create_per_program,
    url_details_per_program,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.post(
        url_msg_create_per_program,
        {"description": "New Message for Feedback Per Program"},
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["description"] == "New Message for Feedback Per Program"
        assert "created_by" in resp_data
        assert "id" in resp_data
        assert "created_at" in resp_data

        # check message details
        response_details = authenticated_client.get(url_details_per_program)
        assert response_details.status_code == status.HTTP_200_OK
        resp_data = response_details.json()
        assert "id" in resp_data
        assert len(resp_data["feedback_messages"]) == 1
        feedback_message = resp_data["feedback_messages"][0]
        assert feedback_message["description"] == "New Message for Feedback Per Program"
        assert feedback_message["created_by"] == "Test User"
        assert "id" in feedback_message
        assert "created_at" in feedback_message


@pytest.mark.parametrize(
    ("filter_value", "expected_count"),
    [
        ("POSITIVE_FEEDBACK", 1),
        ("NEGATIVE_FEEDBACK", 2),
    ],
)
def test_filter_feedback_by_issue_type(
    filter_value: str,
    expected_count: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    feedback_1,
    feedback_2,
    feedback_3,
    url_list,
    url_count,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST],
        business_area,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(url_list, {"issue_type": filter_value})
    response_count = authenticated_client.get(url_count, {"issue_type": filter_value})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == expected_count
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == expected_count


def test_filter_by_created_at(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    feedback_1,
    feedback_2,
    feedback_3,
    url_list,
    url_count,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST],
        business_area,
        whole_business_area_access=True,
    )
    feedback_1.created_at = timezone.make_aware(datetime.datetime(year=2020, month=3, day=12))
    feedback_1.save()
    feedback_2.created_at = timezone.make_aware(datetime.datetime(year=2023, month=1, day=31))
    feedback_2.save()
    feedback_3.created_at = timezone.make_aware(datetime.datetime(year=2023, month=2, day=1))
    feedback_3.save()
    response = authenticated_client.get(
        url_list,
        {
            "created_at_after": "2023-01-30",
            "created_at_before": "2023-03-01",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 2
    results_ids = [feedback["id"] for feedback in results]
    assert str(feedback_1.id) not in results_ids
    assert str(feedback_2.id) in results_ids
    assert str(feedback_3.id) in results_ids

    # check count
    response_count = authenticated_client.get(
        url_count,
        {
            "created_at_after": "2023-01-30",
            "created_at_before": "2023-03-01",
        },
    )
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == 2


def test_filter_by_created_by(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    user_creator,
    feedback_1,
    feedback_2,
    feedback_3,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST],
        business_area,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(url_list, {"created_by": str(user_creator.id)})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(feedback_3.id)


def test_filter_by_is_active_program(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    feedback_1,
    feedback_with_finished_program,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST],
        business_area,
        whole_business_area_access=True,
    )
    response_true = authenticated_client.get(url_list, {"is_active_program": True})
    assert response_true.status_code == status.HTTP_200_OK
    results = response_true.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(feedback_1.id)

    response_false = authenticated_client.get(url_list, {"is_active_program": False})
    assert response_false.status_code == status.HTTP_200_OK
    results = response_false.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(feedback_with_finished_program.id)
