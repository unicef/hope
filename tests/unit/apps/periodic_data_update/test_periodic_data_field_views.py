"""Tests for periodic data field views."""

import json
from typing import Any, Callable

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
import freezegun
import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FlexibleAttributeForPDUFactory,
    PartnerFactory,
    PeriodicFieldDataFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Partner, PeriodicFieldData, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def program1(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, name="Program1")


@pytest.fixture
def program2(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, name="Program2")


@pytest.fixture
def periodic_field1(program1: Program) -> Any:
    periodic_field1_data = PeriodicFieldDataFactory()
    return FlexibleAttributeForPDUFactory(program=program1, pdu_data=periodic_field1_data)


@pytest.fixture
def periodic_field2(program1: Program) -> Any:
    periodic_field2_data = PeriodicFieldDataFactory()
    return FlexibleAttributeForPDUFactory(program=program1, pdu_data=periodic_field2_data)


@pytest.fixture
def periodic_field3(program1: Program) -> Any:
    periodic_field3_data = PeriodicFieldDataFactory()
    return FlexibleAttributeForPDUFactory(program=program1, pdu_data=periodic_field3_data)


@pytest.fixture
def periodic_field_program2(program2: Program) -> Any:
    periodic_field_data_program2 = PeriodicFieldDataFactory()
    return FlexibleAttributeForPDUFactory(program=program2, pdu_data=periodic_field_data_program2)


@pytest.fixture
def url_list(business_area: BusinessArea, program1: Program) -> str:
    return reverse(
        "api:periodic-data-update:periodic-fields-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program1.slug,
        },
    )


@freezegun.freeze_time("2022-01-01")
def test_list_periodic_fields(
    authenticated_client: APIClient,
    user: User,
    business_area: BusinessArea,
    program1: Program,
    periodic_field1: Any,
    periodic_field2: Any,
    periodic_field3: Any,
    periodic_field_program2: Any,
    url_list: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        business_area,
        program1,
    )

    response = authenticated_client.get(url_list)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()["results"]
    assert len(response_json) == 3
    assert {
        "id": str(periodic_field1.id),
        "name": periodic_field1.name,
        "label": periodic_field1.label["English(EN)"],
        "pdu_data": {
            "subtype": periodic_field1.pdu_data.subtype,
            "number_of_rounds": periodic_field1.pdu_data.number_of_rounds,
            "rounds_names": periodic_field1.pdu_data.rounds_names,
        },
    } in response_json
    assert {
        "id": str(periodic_field2.id),
        "name": periodic_field2.name,
        "label": periodic_field2.label["English(EN)"],
        "pdu_data": {
            "subtype": periodic_field2.pdu_data.subtype,
            "number_of_rounds": periodic_field2.pdu_data.number_of_rounds,
            "rounds_names": periodic_field2.pdu_data.rounds_names,
        },
    } in response_json
    assert {
        "id": str(periodic_field3.id),
        "name": periodic_field3.name,
        "label": periodic_field3.label["English(EN)"],
        "pdu_data": {
            "subtype": periodic_field3.pdu_data.subtype,
            "number_of_rounds": periodic_field3.pdu_data.number_of_rounds,
            "rounds_names": periodic_field3.pdu_data.rounds_names,
        },
    } in response_json

    assert {
        "id": str(periodic_field_program2.id),
        "name": periodic_field_program2.name,
        "label": periodic_field_program2.label["English(EN)"],
        "pdu_data": {
            "subtype": periodic_field_program2.pdu_data.subtype,
            "number_of_rounds": periodic_field_program2.pdu_data.number_of_rounds,
            "rounds_names": periodic_field_program2.pdu_data.rounds_names,
        },
    } not in response_json


@freezegun.freeze_time("2022-01-01")
def test_list_periodic_fields_caching(
    authenticated_client: APIClient,
    user: User,
    business_area: BusinessArea,
    program1: Program,
    periodic_field1: Any,
    periodic_field2: Any,
    periodic_field3: Any,
    periodic_field_program2: Any,
    url_list: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        business_area,
        program1,
    )

    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK

        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 7

    # Test that recurring requests use cached data
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK

        etag_second_call = response.headers["etag"]
        assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 1

        assert etag_second_call == etag

    # After update of periodic field, it does not use the cached data
    periodic_field1.name = "New Name"
    periodic_field1.save()
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK

        etag_call_after_update = response.headers["etag"]
        assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 7

        assert etag_call_after_update != etag

    # Cached data again
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK

        etag_call_after_update_second_call = response.headers["etag"]
        assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 1

        assert etag_call_after_update_second_call == etag_call_after_update

    # After update of periodic field data, it does not use the cached data
    periodic_field1.pdu_data.subtype = PeriodicFieldData.DECIMAL
    periodic_field1.pdu_data.save()
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK

        etag_call_after_update_2 = response.headers["etag"]
        assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 7

        assert etag_call_after_update_2 != etag_call_after_update_second_call
