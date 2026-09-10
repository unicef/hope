from typing import Any

from django.db import connection
from django.test.utils import CaptureQueriesContext
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import PaymentPlan, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def payments_context(api_client: Any) -> dict[str, Any]:
    """Values are chosen so that no column's sort order matches the ``-created_at`` fallback."""
    afghanistan = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    program = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)

    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    client = api_client(user)

    household = HouseholdFactory(program=program, business_area=afghanistan)

    first_cycle = ProgramCycleFactory(program=program, title="Beta cycle")
    first = PaymentFactory(
        parent=PaymentPlanFactory(
            status=PaymentPlan.Status.ACCEPTED,
            business_area=afghanistan,
            program_cycle=first_cycle,
            payment_plan_group=PaymentPlanGroupFactory(cycle=first_cycle, name="Beta group"),
        ),
        household=household,
        business_area=afghanistan,
        currency=household.currency,
        entitlement_quantity=90,
        head_of_household=IndividualFactory(
            household=None, business_area=afghanistan, program=program, full_name="Mia Mike"
        ),
    )
    second_cycle = ProgramCycleFactory(program=program, title="Alpha cycle")
    second = PaymentFactory(
        parent=PaymentPlanFactory(
            status=PaymentPlan.Status.ACCEPTED,
            business_area=afghanistan,
            program_cycle=second_cycle,
            payment_plan_group=PaymentPlanGroupFactory(cycle=second_cycle, name="Alpha group"),
        ),
        household=household,
        business_area=afghanistan,
        currency=household.currency,
        entitlement_quantity=10,
        head_of_household=IndividualFactory(
            household=None, business_area=afghanistan, program=program, full_name="Zoe Zulu"
        ),
    )
    third_cycle = ProgramCycleFactory(program=program, title="Gamma cycle")
    third = PaymentFactory(
        parent=PaymentPlanFactory(
            status=PaymentPlan.Status.ACCEPTED,
            business_area=afghanistan,
            program_cycle=third_cycle,
            payment_plan_group=PaymentPlanGroupFactory(cycle=third_cycle, name="Gamma group"),
        ),
        household=household,
        business_area=afghanistan,
        currency=household.currency,
        entitlement_quantity=50,
        head_of_household=IndividualFactory(
            household=None, business_area=afghanistan, program=program, full_name="Adam Alpha"
        ),
    )

    return {
        "afghanistan": afghanistan,
        "program": program,
        "user": user,
        "api_client": client,
        "household": household,
        "first": first,
        "second": second,
        "third": third,
    }


@pytest.fixture
def payments_url(payments_context: dict[str, Any]) -> str:
    return reverse(
        "api:households:households-payments",
        kwargs={
            "business_area_slug": payments_context["afghanistan"].slug,
            "program_code": payments_context["program"].code,
            "pk": str(payments_context["household"].id),
        },
    )


def test_household_payments_default_ordering_is_newest_first(
    create_user_role_with_permissions: Any,
    payments_context: dict[str, Any],
    payments_url: str,
) -> None:
    create_user_role_with_permissions(
        user=payments_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
        business_area=payments_context["afghanistan"],
        program=payments_context["program"],
    )

    response = payments_context["api_client"].get(payments_url)

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert results[0]["unicef_id"] == payments_context["third"].unicef_id
    assert results[1]["unicef_id"] == payments_context["second"].unicef_id
    assert results[2]["unicef_id"] == payments_context["first"].unicef_id


def test_household_payments_ordering_by_entitlement_quantity_ascending(
    create_user_role_with_permissions: Any,
    payments_context: dict[str, Any],
    payments_url: str,
) -> None:
    create_user_role_with_permissions(
        user=payments_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
        business_area=payments_context["afghanistan"],
        program=payments_context["program"],
    )

    response = payments_context["api_client"].get(payments_url, {"ordering": "entitlement_quantity"})

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert results[0]["entitlement_quantity"] == "10.00"
    assert results[1]["entitlement_quantity"] == "50.00"
    assert results[2]["entitlement_quantity"] == "90.00"


def test_household_payments_ordering_by_entitlement_quantity_descending(
    create_user_role_with_permissions: Any,
    payments_context: dict[str, Any],
    payments_url: str,
) -> None:
    create_user_role_with_permissions(
        user=payments_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
        business_area=payments_context["afghanistan"],
        program=payments_context["program"],
    )

    response = payments_context["api_client"].get(payments_url, {"ordering": "-entitlement_quantity"})

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert results[0]["entitlement_quantity"] == "90.00"
    assert results[1]["entitlement_quantity"] == "50.00"
    assert results[2]["entitlement_quantity"] == "10.00"


def test_household_payments_ordering_by_payment_plan_cycle_ascending(
    create_user_role_with_permissions: Any,
    payments_context: dict[str, Any],
    payments_url: str,
) -> None:
    create_user_role_with_permissions(
        user=payments_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
        business_area=payments_context["afghanistan"],
        program=payments_context["program"],
    )

    response = payments_context["api_client"].get(payments_url, {"ordering": "payment_plan_cycle"})

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert results[0]["payment_plan_cycle"] == "Alpha cycle"
    assert results[1]["payment_plan_cycle"] == "Beta cycle"
    assert results[2]["payment_plan_cycle"] == "Gamma cycle"


def test_household_payments_ordering_by_payment_plan_cycle_descending(
    create_user_role_with_permissions: Any,
    payments_context: dict[str, Any],
    payments_url: str,
) -> None:
    create_user_role_with_permissions(
        user=payments_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
        business_area=payments_context["afghanistan"],
        program=payments_context["program"],
    )

    response = payments_context["api_client"].get(payments_url, {"ordering": "-payment_plan_cycle"})

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert results[0]["payment_plan_cycle"] == "Gamma cycle"
    assert results[1]["payment_plan_cycle"] == "Beta cycle"
    assert results[2]["payment_plan_cycle"] == "Alpha cycle"


def test_household_payments_ordering_by_payment_plan_group(
    create_user_role_with_permissions: Any,
    payments_context: dict[str, Any],
    payments_url: str,
) -> None:
    create_user_role_with_permissions(
        user=payments_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
        business_area=payments_context["afghanistan"],
        program=payments_context["program"],
    )

    response = payments_context["api_client"].get(payments_url, {"ordering": "payment_plan_group"})

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert results[0]["payment_plan_group"] == "Alpha group"
    assert results[1]["payment_plan_group"] == "Beta group"
    assert results[2]["payment_plan_group"] == "Gamma group"


def test_household_payments_ordering_by_hoh_full_name(
    create_user_role_with_permissions: Any,
    payments_context: dict[str, Any],
    payments_url: str,
) -> None:
    create_user_role_with_permissions(
        user=payments_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
        business_area=payments_context["afghanistan"],
        program=payments_context["program"],
    )

    response = payments_context["api_client"].get(payments_url, {"ordering": "hoh_full_name"})

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert results[0]["hoh_full_name"] == "Adam Alpha"
    assert results[1]["hoh_full_name"] == "Mia Mike"
    assert results[2]["hoh_full_name"] == "Zoe Zulu"


def test_household_payments_query_count_does_not_grow_with_rows(
    create_user_role_with_permissions: Any,
    payments_context: dict[str, Any],
    payments_url: str,
) -> None:
    create_user_role_with_permissions(
        user=payments_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
        business_area=payments_context["afghanistan"],
        program=payments_context["program"],
    )

    # Warm the permission cache so it is not charged to the first measured request.
    payments_context["api_client"].get(payments_url)

    with CaptureQueriesContext(connection) as one_row:
        first_page = payments_context["api_client"].get(payments_url, {"limit": 1})
    with CaptureQueriesContext(connection) as all_rows:
        full_page = payments_context["api_client"].get(payments_url, {"limit": 3})

    assert len(first_page.json()["results"]) == 1
    assert len(full_page.json()["results"]) == 3
    assert len(all_rows.captured_queries) == len(one_row.captured_queries)


def test_household_payments_unknown_ordering_field_falls_back_to_default(
    create_user_role_with_permissions: Any,
    payments_context: dict[str, Any],
    payments_url: str,
) -> None:
    create_user_role_with_permissions(
        user=payments_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
        business_area=payments_context["afghanistan"],
        program=payments_context["program"],
    )

    response = payments_context["api_client"].get(payments_url, {"ordering": "not_a_field"})

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert results[0]["unicef_id"] == payments_context["third"].unicef_id
    assert results[2]["unicef_id"] == payments_context["first"].unicef_id
