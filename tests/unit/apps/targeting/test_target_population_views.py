import json

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
import freezegun
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def partner():
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner):
    return UserFactory(partner=partner)


@pytest.fixture
def api_client_for_user(api_client, user):
    return api_client(user)


@pytest.fixture
def programs(business_area):
    program1 = ProgramFactory(business_area=business_area, name="Program1")
    program2 = ProgramFactory(business_area=business_area, name="Program2")

    return program1, program2


@pytest.fixture
def target_populations(business_area, programs):
    program1, program2 = programs
    ProgramCycleFactory(program=program1)
    ProgramCycleFactory(program=program2)
    with freezegun.freeze_time("2022-01-01"):
        tp1 = PaymentPlanFactory(
            business_area=business_area,
            program_cycle=program1.cycles.first(),
            status=PaymentPlan.Status.TP_OPEN,
            name="Test TP 1",
        )
        tp1.created_at = "2022-01-01T04:00:00Z"
        tp1.save()

        tp2 = PaymentPlanFactory(
            business_area=business_area,
            program_cycle=program1.cycles.first(),
            status=PaymentPlan.Status.TP_LOCKED,
            name="Test TP 2",
        )
        tp2.created_at = "2022-01-01T03:00:00Z"
        tp2.save()

        tp3 = PaymentPlanFactory(
            business_area=business_area,
            program_cycle=program1.cycles.first(),
            status=PaymentPlan.Status.OPEN,
            name="Test 3 TP",
        )
        tp3.created_at = "2022-01-01T02:00:00Z"
        tp3.save()

        tp_program2 = PaymentPlanFactory(
            business_area=business_area,
            program_cycle=program2.cycles.first(),
            status=PaymentPlan.Status.OPEN,
            name="Test TP Program 2",
        )
        tp_program2.created_at = "2022-01-01T01:00:00Z"
        tp_program2.save()

    return tp1, tp2, tp3, tp_program2


@pytest.fixture
def list_url(business_area, programs):
    program1, _ = programs
    return reverse(
        "api:payments:target-populations-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program1.slug,
        },
    )


@pytest.mark.parametrize(
    ("permissions", "partner_permissions", "access_to_program", "expected_status"),
    [
        ([], [], True, status.HTTP_403_FORBIDDEN),
        ([Permissions.TARGETING_VIEW_LIST], [], True, status.HTTP_200_OK),
        ([], [Permissions.TARGETING_VIEW_LIST], True, status.HTTP_200_OK),
        (
            [Permissions.TARGETING_VIEW_LIST],
            [Permissions.TARGETING_VIEW_LIST],
            True,
            status.HTTP_200_OK,
        ),
        ([], [], False, status.HTTP_403_FORBIDDEN),
        ([Permissions.TARGETING_VIEW_LIST], [], False, status.HTTP_403_FORBIDDEN),
        ([], [Permissions.TARGETING_VIEW_LIST], False, status.HTTP_403_FORBIDDEN),
        (
            [Permissions.TARGETING_VIEW_LIST],
            [Permissions.TARGETING_VIEW_LIST],
            False,
            status.HTTP_403_FORBIDDEN,
        ),
    ],
)
def test_list_target_populations_permission(
    permissions,
    partner_permissions,
    access_to_program,
    expected_status,
    api_client_for_user,
    user,
    partner,
    business_area,
    programs,
    list_url,
    create_user_role_with_permissions,
    create_partner_role_with_permissions,
):
    program1, _ = programs

    create_user_role_with_permissions(user, permissions, business_area)

    if access_to_program:
        create_user_role_with_permissions(user, permissions, business_area, program1)
        create_partner_role_with_permissions(partner, partner_permissions, business_area, program1)
    else:
        create_partner_role_with_permissions(partner, partner_permissions, business_area)

    response = api_client_for_user.get(list_url)
    assert response.status_code == expected_status


def test_list_target_populations(
    api_client_for_user,
    user,
    business_area,
    programs,
    list_url,
    target_populations,
    create_user_role_with_permissions,
):
    program1, _ = programs
    tp1, tp2, tp3, _ = target_populations

    create_user_role_with_permissions(
        user,
        [Permissions.TARGETING_VIEW_LIST],
        business_area,
        program1,
    )

    response = api_client_for_user.get(list_url)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()["results"]
    assert len(response_json) == 3

    expected_1 = {
        "name": tp1.name,
        "status": tp1.get_status_display().upper(),
        "created_by": tp1.created_by.get_full_name(),
        "created_at": "2022-01-01T04:00:00Z",
        "total_households_count": tp1.total_households_count,
        "total_individuals_count": tp1.total_individuals_count,
        "updated_at": "2022-01-01T00:00:00Z",
    }
    for key, value in expected_1.items():
        assert response_json[0][key] == value

    expected_2 = {
        "name": tp2.name,
        "status": tp2.get_status_display().upper(),
        "created_by": tp2.created_by.get_full_name(),
        "created_at": "2022-01-01T03:00:00Z",
    }
    for key, value in expected_2.items():
        assert response_json[1][key] == value

    expected_3 = {
        "name": tp3.name,
        "status": "ASSIGNED",
        "created_by": tp3.created_by.get_full_name(),
        "created_at": "2022-01-01T02:00:00Z",
    }
    assert "id" in response_json[2]
    for key, value in expected_3.items():
        assert response_json[2][key] == value


def test_list_target_populations_filter(
    api_client_for_user,
    user,
    business_area,
    programs,
    list_url,
    target_populations,
    create_user_role_with_permissions,
):
    program1, _ = programs

    create_user_role_with_permissions(
        user,
        [Permissions.TARGETING_VIEW_LIST],
        business_area,
        program1,
    )

    response = api_client_for_user.get(list_url, {"status": PaymentPlan.Status.TP_OPEN})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1


def test_list_target_populations_search_by_name(
    api_client_for_user,
    user,
    business_area,
    programs,
    list_url,
    target_populations,
    create_user_role_with_permissions,
):
    program1, _ = programs

    create_user_role_with_permissions(
        user,
        [Permissions.TARGETING_VIEW_LIST],
        business_area,
        program1,
    )

    response = api_client_for_user.get(list_url, {"name": "Test TP"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 2


def test_list_target_populations_caching(
    api_client_for_user,
    user,
    business_area,
    programs,
    list_url,
    target_populations,
    create_user_role_with_permissions,
):
    program1, _ = programs
    tp1, _, _, _ = target_populations

    create_user_role_with_permissions(
        user,
        [Permissions.TARGETING_VIEW_LIST],
        business_area,
        program1,
    )

    with CaptureQueriesContext(connection) as ctx:
        response = api_client_for_user.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 18

    with CaptureQueriesContext(connection) as ctx:
        response = api_client_for_user.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(ctx.captured_queries) == 7
        assert response.headers["etag"] == etag

    tp1.status = PaymentPlan.Status.TP_PROCESSING
    tp1.save()

    with CaptureQueriesContext(connection) as ctx:
        response = api_client_for_user.get(list_url)
        etag_call_after_update = response.headers["etag"]
        assert response.status_code == status.HTTP_200_OK
        assert len(ctx.captured_queries) == 12
        assert etag != etag_call_after_update

    with CaptureQueriesContext(connection) as ctx:
        response = api_client_for_user.get(list_url)
        etag_call_after_update_second_call = response.headers["etag"]
        assert response.status_code == status.HTTP_200_OK
        assert len(ctx.captured_queries) == 7
        assert etag_call_after_update == etag_call_after_update_second_call
