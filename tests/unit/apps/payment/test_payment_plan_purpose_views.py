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


def test_list_purposes_filtered_by_business_area(
    client: Any,
    user: Any,
    business_area: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST], business_area, whole_business_area_access=True)
    other_ba = BusinessAreaFactory(slug="other-ba")
    purpose_in_ba = PaymentPlanPurposeFactory(business_area=business_area, name="Food")
    PaymentPlanPurposeFactory(business_area=other_ba, name="Education")

    response = client.get(_list_url(business_area.slug))

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(purpose_in_ba.id)
    assert results[0]["name"] == "Food"


def test_count_purposes_filtered_by_business_area(
    client: Any,
    user: Any,
    business_area: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST], business_area, whole_business_area_access=True)
    other_ba = BusinessAreaFactory(slug="other-ba")
    PaymentPlanPurposeFactory(business_area=business_area, name="Food")
    PaymentPlanPurposeFactory(business_area=business_area, name="Shelter")
    PaymentPlanPurposeFactory(business_area=other_ba, name="Education")

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
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST], business_area, whole_business_area_access=True)
    purpose = PaymentPlanPurposeFactory(business_area=business_area, name="Food")

    with CaptureQueriesContext(connection) as miss_ctx:
        first = client.get(_list_url(business_area.slug))
    assert first.status_code == status.HTTP_200_OK
    assert first.has_header("etag")
    etag = first.headers["etag"]

    with CaptureQueriesContext(connection) as hit_ctx:
        cached = client.get(_list_url(business_area.slug))
    assert cached.status_code == status.HTTP_200_OK
    assert cached.headers["etag"] == etag
    assert len(hit_ctx.captured_queries) == 3
    assert len(miss_ctx.captured_queries) == 7

    with TestCase.captureOnCommitCallbacks(execute=True):
        PaymentPlanPurposeFactory(business_area=business_area, name="Shelter")

    with CaptureQueriesContext(connection) as invalidated_create_ctx:
        after_create = client.get(_list_url(business_area.slug))
    assert after_create.status_code == status.HTTP_200_OK
    assert after_create.headers["etag"] != etag
    assert len(invalidated_create_ctx.captured_queries) == 3
    etag = after_create.headers["etag"]

    with TestCase.captureOnCommitCallbacks(execute=True):
        purpose.delete()

    with CaptureQueriesContext(connection) as invalidated_delete_ctx:
        after_delete = client.get(_list_url(business_area.slug))
    assert after_delete.status_code == status.HTTP_200_OK
    assert after_delete.headers["etag"] != etag
    assert len(invalidated_delete_ctx.captured_queries) == 3
