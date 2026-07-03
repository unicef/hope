from typing import Any, Callable

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import BusinessAreaFactory, PaymentPlanPurposeFactory, UserFactory
from hope.apps.account.permissions import Permissions

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="test-ba")


@pytest.fixture
def user() -> Any:
    return UserFactory()


@pytest.fixture
def client(api_client: Callable, user: Any) -> Any:
    return api_client(user)


def _list_url(ba_slug: str) -> str:
    return reverse(
        "api:payments:payment-plan-purposes-list",
        kwargs={"business_area_slug": ba_slug},
    )


def _count_url(ba_slug: str) -> str:
    return reverse(
        "api:payments:payment-plan-purposes-count",
        kwargs={"business_area_slug": ba_slug},
    )


def test_list_filters_by_limit_to(
    client: Any,
    user: Any,
    business_area: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST], business_area, whole_business_area_access=True
    )
    other_ba = BusinessAreaFactory(slug="other-ba")
    food = PaymentPlanPurposeFactory(name="Food")
    shelter = PaymentPlanPurposeFactory(name="Shelter")
    shelter.limit_to.add(business_area)
    education = PaymentPlanPurposeFactory(name="Education")
    education.limit_to.add(other_ba)

    response = client.get(_list_url(business_area.slug))

    assert response.status_code == status.HTTP_200_OK
    result_ids = {r["id"] for r in response.json()["results"]}
    assert str(food.id) in result_ids
    assert str(shelter.id) in result_ids
    assert str(education.id) not in result_ids


def test_count_excludes_purposes_restricted_to_other_ba(
    client: Any,
    user: Any,
    business_area: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST], business_area, whole_business_area_access=True
    )
    other_ba = BusinessAreaFactory(slug="other-ba")
    PaymentPlanPurposeFactory(name="Food")
    shelter = PaymentPlanPurposeFactory(name="Shelter")
    shelter.limit_to.add(business_area)
    education = PaymentPlanPurposeFactory(name="Education")
    education.limit_to.add(other_ba)

    response = client.get(_count_url(business_area.slug))

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 2


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_list_permissions(
    client: Any,
    user: Any,
    business_area: Any,
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, whole_business_area_access=True)

    response = client.get(_list_url(business_area.slug))

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_count_permissions(
    client: Any,
    user: Any,
    business_area: Any,
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, whole_business_area_access=True)

    response = client.get(_count_url(business_area.slug))

    assert response.status_code == expected_status


def test_list_caching(
    client: Any,
    user: Any,
    business_area: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST], business_area, whole_business_area_access=True
    )
    purpose = PaymentPlanPurposeFactory(name="Food")
    PaymentPlanPurposeFactory(name="Health")

    with CaptureQueriesContext(connection) as ctx:
        first = client.get(_list_url(business_area.slug))
        assert first.status_code == status.HTTP_200_OK
        assert first.has_header("etag")
        etag = first.headers["etag"]
        assert len(ctx.captured_queries) == 7

    # no change - use cache
    with CaptureQueriesContext(connection) as ctx:
        cached = client.get(_list_url(business_area.slug))
        assert cached.status_code == status.HTTP_200_OK
        assert cached.headers["etag"] == etag
        assert len(ctx.captured_queries) == 2

    with TestCase.captureOnCommitCallbacks(execute=True):
        PaymentPlanPurposeFactory(name="Shelter")

    with CaptureQueriesContext(connection) as ctx:
        after_create = client.get(_list_url(business_area.slug))
        assert after_create.status_code == status.HTTP_200_OK
        assert after_create.headers["etag"] != etag
        assert len(ctx.captured_queries) == 3
        etag = after_create.headers["etag"]

    with TestCase.captureOnCommitCallbacks(execute=True):
        purpose.name = "Emergency Cash"
        purpose.save()

    with CaptureQueriesContext(connection) as ctx:
        after_update = client.get(_list_url(business_area.slug))
        assert after_update.status_code == status.HTTP_200_OK
        assert after_update.headers["etag"] != etag
        assert len(ctx.captured_queries) == 3
        etag = after_update.headers["etag"]

    with TestCase.captureOnCommitCallbacks(execute=True):
        purpose.delete()

    with CaptureQueriesContext(connection) as ctx:
        after_delete = client.get(_list_url(business_area.slug))
        assert after_delete.status_code == status.HTTP_200_OK
        assert after_delete.headers["etag"] != etag
        assert len(ctx.captured_queries) == 3
        etag = after_delete.headers["etag"]

    # no change - use cache
    with CaptureQueriesContext(connection) as ctx:
        cached_again = client.get(_list_url(business_area.slug))
        assert cached_again.status_code == status.HTTP_200_OK
        assert cached_again.headers["etag"] == etag
        assert len(ctx.captured_queries) == 2


def test_list_purposes_search_by_name(
    client: Any,
    user: Any,
    business_area: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST], business_area, whole_business_area_access=True
    )
    PaymentPlanPurposeFactory(name="Food Assistance")
    PaymentPlanPurposeFactory(name="Shelter Support")
    PaymentPlanPurposeFactory(name="Education Grant")

    response = client.get(_list_url(business_area.slug), {"search": "shelter"})

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["name"] == "Shelter Support"
