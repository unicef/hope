from typing import Any

from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Household, Message, PaymentPlan, Program, Survey, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def attacker_business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def attacker_program(attacker_business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=attacker_business_area)


@pytest.fixture
def victim_payment_plan() -> PaymentPlan:
    business_area = BusinessAreaFactory(slug="ukraine")
    return PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        program_cycle__program=ProgramFactory(business_area=business_area),
    )


@pytest.fixture
def victim_household(victim_payment_plan: PaymentPlan) -> Household:
    victim_program = victim_payment_plan.program
    head_of_household = IndividualFactory(
        household=None,
        program=victim_program,
        business_area=victim_program.business_area,
        phone_no="+48600123450",
        phone_no_valid=True,
    )
    household = HouseholdFactory(
        program=victim_program,
        business_area=victim_program.business_area,
        head_of_household=head_of_household,
        registration_data_import=head_of_household.registration_data_import,
    )
    PaymentFactory(parent=victim_payment_plan, household=household, collector=head_of_household)
    return household


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
            Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE,
            Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE,
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
def program_kwargs(attacker_business_area: BusinessArea, attacker_program: Program) -> dict[str, str]:
    return {"business_area_slug": attacker_business_area.slug, "program_code": attacker_program.code}


def test_create_survey_for_payment_plan_from_other_business_area_is_denied(
    api_client: APIClient,
    program_kwargs: dict[str, str],
    victim_payment_plan: PaymentPlan,
    victim_household: Household,
) -> None:
    url = reverse("api:accountability:surveys-list", kwargs=program_kwargs)

    response = api_client.post(
        url,
        {
            "title": "cross business area survey",
            "body": "body",
            "category": Survey.CATEGORY_MANUAL,
            "sampling_type": Survey.SAMPLING_FULL_LIST,
            "payment_plan": str(victim_payment_plan.id),
            "full_list_arguments": {"excluded_admin_areas": []},
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
    assert not Survey.objects.exists()


def test_create_message_for_households_from_other_business_area_is_denied(
    api_client: APIClient,
    program_kwargs: dict[str, str],
    victim_household: Household,
) -> None:
    url = reverse("api:accountability:messages-list", kwargs=program_kwargs)

    response = api_client.post(
        url,
        {
            "title": "cross business area message",
            "body": "body",
            "sampling_type": Message.SamplingChoices.FULL_LIST,
            "households": [str(victim_household.id)],
            "full_list_arguments": {"excluded_admin_areas": []},
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
    assert not Message.objects.exists()
