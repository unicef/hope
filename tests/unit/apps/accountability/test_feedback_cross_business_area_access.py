from typing import Any

from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FeedbackFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Feedback, Household, Individual, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def attacker_business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def attacker_program(attacker_business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=attacker_business_area)


@pytest.fixture
def victim_feedback() -> Feedback:
    business_area = BusinessAreaFactory(slug="ukraine")
    return FeedbackFactory(
        business_area=business_area,
        program=ProgramFactory(business_area=business_area),
        created_by=UserFactory(),
    )


@pytest.fixture
def attacker(
    attacker_business_area: BusinessArea,
    attacker_program: Program,
    create_user_role_with_permissions: Any,
) -> User:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
            Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
            Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE,
            Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE,
        ],
        attacker_business_area,
        program=attacker_program,
    )
    return user


@pytest.fixture
def api_client(attacker: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=attacker)
    return client


@pytest.fixture
def cross_ba_detail_url(attacker_business_area: BusinessArea, victim_feedback: Feedback) -> str:
    return reverse(
        "api:accountability:feedbacks-detail",
        kwargs={"business_area_slug": attacker_business_area.slug, "pk": str(victim_feedback.id)},
    )


def test_retrieve_feedback_from_other_business_area_is_denied(api_client: APIClient, cross_ba_detail_url: str) -> None:
    response = api_client.get(cross_ba_detail_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code


def test_update_feedback_from_other_business_area_is_denied(
    api_client: APIClient, cross_ba_detail_url: str, victim_feedback: Feedback
) -> None:
    response = api_client.patch(cross_ba_detail_url, {"description": "hijacked"}, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
    victim_feedback.refresh_from_db()
    assert victim_feedback.description != "hijacked"


@pytest.fixture
def feedback_in_program_without_role(attacker_business_area: BusinessArea) -> Feedback:
    return FeedbackFactory(
        business_area=attacker_business_area,
        program=ProgramFactory(business_area=attacker_business_area),
        created_by=UserFactory(),
    )


def test_retrieve_feedback_from_program_without_role_is_denied(
    api_client: APIClient, attacker_business_area: BusinessArea, feedback_in_program_without_role: Feedback
) -> None:
    url = reverse(
        "api:accountability:feedbacks-detail",
        kwargs={
            "business_area_slug": attacker_business_area.slug,
            "pk": str(feedback_in_program_without_role.id),
        },
    )

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code


@pytest.fixture
def attacker_feedback(attacker_business_area: BusinessArea, attacker_program: Program) -> Feedback:
    return FeedbackFactory(
        business_area=attacker_business_area,
        program=attacker_program,
        created_by=UserFactory(),
    )


def test_move_feedback_to_program_in_other_business_area_is_denied(
    api_client: APIClient,
    attacker_business_area: BusinessArea,
    attacker_feedback: Feedback,
    victim_feedback: Feedback,
) -> None:
    url = reverse(
        "api:accountability:feedbacks-detail",
        kwargs={"business_area_slug": attacker_business_area.slug, "pk": str(attacker_feedback.id)},
    )

    response = api_client.patch(
        url,
        {
            "issue_type": attacker_feedback.issue_type,
            "description": attacker_feedback.description,
            "program_id": str(victim_feedback.program_id),
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
    attacker_feedback.refresh_from_db()
    assert attacker_feedback.program_id != victim_feedback.program_id


@pytest.fixture
def victim_household() -> Household:
    program = ProgramFactory(business_area=BusinessAreaFactory(slug="ukraine"))
    return HouseholdFactory(business_area=program.business_area, program=program, create_role=False)


@pytest.fixture
def victim_individual(victim_household: Household) -> Individual:
    return IndividualFactory(
        household=victim_household,
        business_area=victim_household.business_area,
        program=victim_household.program,
        registration_data_import=victim_household.registration_data_import,
    )


@pytest.fixture
def create_url(attacker_business_area: BusinessArea) -> str:
    return reverse("api:accountability:feedbacks-list", kwargs={"business_area_slug": attacker_business_area.slug})


def test_create_feedback_for_household_from_other_business_area_is_denied(
    api_client: APIClient,
    create_url: str,
    victim_household: Household,
) -> None:
    response = api_client.post(
        create_url,
        {
            "issue_type": Feedback.POSITIVE_FEEDBACK,
            "description": "cross business area feedback",
            "household_lookup": str(victim_household.id),
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
    assert not Feedback.objects.filter(household_lookup=victim_household).exists()


def test_create_feedback_for_individual_from_other_business_area_is_denied(
    api_client: APIClient,
    create_url: str,
    victim_individual: Individual,
) -> None:
    response = api_client.post(
        create_url,
        {
            "issue_type": Feedback.POSITIVE_FEEDBACK,
            "description": "cross business area feedback",
            "individual_lookup": str(victim_individual.id),
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
    assert not Feedback.objects.filter(individual_lookup=victim_individual).exists()
