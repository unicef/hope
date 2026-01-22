"""Tests for Survey ViewSet."""

import datetime
from typing import Any, List
from unittest.mock import MagicMock, patch

from django.urls import reverse
from django.utils import timezone
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    SurveyFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.core.services.rapid_pro.api import TokenNotProvidedError
from hope.models import PaymentPlan, Program, Survey

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(code="0060", slug="afghanistan", name="Afghanistan", active=True)


@pytest.fixture
def partner():
    return PartnerFactory(name="unittest")


@pytest.fixture
def user(partner):
    return UserFactory(partner=partner, first_name="Test", last_name="User")


@pytest.fixture
def authenticated_client(api_client, user):
    return api_client(user)


@pytest.fixture
def program_active(business_area):
    program = ProgramFactory(
        name="Test Active Program",
        business_area=business_area,
        status=Program.ACTIVE,
    )
    ProgramCycleFactory(program=program)
    return program


@pytest.fixture
def user_creator(partner):
    return UserFactory(partner=partner, first_name="Creator", last_name="User")


@pytest.fixture
def household_1(program_active, business_area):
    birth_date_for_50yo = timezone.now().date() - datetime.timedelta(days=50 * 365)
    rdi = RegistrationDataImportFactory(program=program_active, business_area=business_area)
    hoh = IndividualFactory(
        household=None,
        birth_date=birth_date_for_50yo,
        sex="MALE",
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi,
        phone_no="+48600123456",
        phone_no_valid=True,
    )
    return HouseholdFactory(
        program=program_active,
        head_of_household=hoh,
        business_area=business_area,
        registration_data_import=rdi,
    )


@pytest.fixture
def payment_plan(user, business_area, program_active):
    return PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        business_area=business_area,
        program_cycle=program_active.cycles.first(),
    )


@pytest.fixture
def payment(payment_plan, program_active, household_1, business_area):
    return PaymentFactory(
        parent=payment_plan,
        program=program_active,
        household=household_1,
        business_area=business_area,
        collector=household_1.head_of_household,
    )


@pytest.fixture
def srv(program_active, business_area, user, payment_plan):
    return SurveyFactory(
        program=program_active,
        business_area=business_area,
        created_by=user,
        title="Survey 1",
        body="Survey 1 body",
        flow_id="id123",
        sample_file=None,
        sample_file_generated_at=None,
        sampling_type=Survey.SAMPLING_FULL_LIST,
        category=Survey.CATEGORY_SMS,
        payment_plan=payment_plan,
    )


@pytest.fixture
def srv_2(program_active, business_area, user_creator, payment_plan):
    return SurveyFactory(
        program=program_active,
        business_area=business_area,
        created_by=user_creator,
        title="Survey 2",
        body="Survey 2 body",
        flow_id="id456",
        sample_file=None,
        sample_file_generated_at=None,
        sampling_type=Survey.SAMPLING_RANDOM,
        category=Survey.CATEGORY_MANUAL,
        payment_plan=payment_plan,
    )


@pytest.fixture
def url_list(business_area, program_active):
    return reverse(
        "api:accountability:surveys-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )


@pytest.fixture
def url_count(business_area, program_active):
    return reverse(
        "api:accountability:surveys-count",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )


@pytest.fixture
def url_details(business_area, program_active, srv):
    return reverse(
        "api:accountability:surveys-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
            "pk": str(srv.pk),
        },
    )


@pytest.fixture
def url_export_sample(business_area, program_active, srv):
    return reverse(
        "api:accountability:surveys-export-sample",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
            "pk": str(srv.pk),
        },
    )


@pytest.fixture
def url_flows(business_area, program_active):
    return reverse(
        "api:accountability:surveys-available-flows",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )


@pytest.fixture
def url_category_choices(business_area, program_active):
    return reverse(
        "api:accountability:surveys-category-choices",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST],
            status.HTTP_200_OK,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_survey_list(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    srv,
    srv_2,
    url_list,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.get(url_list)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.status_code == status.HTTP_200_OK
        response_results = response.json()["results"]
        assert len(response_results) == 2
        # Create a mapping of survey id to result for order-independent checking
        result_by_id = {r["id"]: r for r in response_results}
        for survey in [srv, srv_2]:
            survey_result = result_by_id[str(survey.id)]
            assert survey_result["unicef_id"] == str(survey.unicef_id)
            assert survey_result["title"] == survey.title
            assert survey_result["body"] == survey.body
            assert survey_result["category"] == survey.get_category_display()
            assert survey_result["flow_id"] == survey.flow_id
            assert survey_result["rapid_pro_url"] == f"https://rapidpro.io/flow/results/{survey.flow_id}/"
            assert survey_result["created_by"] == f"{survey.created_by.first_name} {survey.created_by.last_name}"
            assert survey_result["has_valid_sample_file"] is None
            assert survey_result["sample_file_path"] is None
            assert survey_result["created_at"] == f"{survey.created_at:%Y-%m-%dT%H:%M:%SZ}"
            assert survey_result["number_of_recipients"] == survey.number_of_recipients


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST],
            status.HTTP_200_OK,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_survey_get_count(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    srv,
    srv_2,
    url_count,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.get(url_count)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["count"] == 2


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [
                Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
                Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST,
            ],
            status.HTTP_200_OK,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_survey_details(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    srv,
    url_details,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.get(url_details)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["title"] == "Survey 1"
        assert resp_data["body"] == "Survey 1 body"
        assert resp_data["category"] == "Survey with SMS"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE], status.HTTP_201_CREATED),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_survey(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    payment_plan,
    payment,
    url_list,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.post(
        url_list,
        {
            "title": "New SRV",
            "body": "LGTM",
            "category": "MANUAL",
            "sampling_type": Survey.SAMPLING_FULL_LIST,
            "full_list_arguments": {"excluded_admin_areas": []},
            "payment_plan": str(payment_plan.pk),
        },
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["title"] == "New SRV"
        assert resp_data["body"] == "LGTM"

        # create new one with PaymentPlan (TP)
        response = authenticated_client.post(
            url_list,
            {
                "title": "New SRV with TP",
                "body": "LGTM",
                "category": "MANUAL",
                "sampling_type": Survey.SAMPLING_FULL_LIST,
                "full_list_arguments": {"excluded_admin_areas": []},
                "random_sampling_arguments": None,
                "payment_plan": str(payment_plan.pk),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["title"] == "New SRV with TP"
        assert Survey.objects.get(title="New SRV with TP").payment_plan_id == payment_plan.pk


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS],
            status.HTTP_202_ACCEPTED,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_survey_export_sample(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    srv,
    url_export_sample,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.get(url_export_sample)
    assert response.status_code == expected_status
    if expected_status == status.HTTP_202_ACCEPTED:
        assert response.status_code == status.HTTP_202_ACCEPTED
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["title"] == "Survey 1"


def test_get_category_choices(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    url_category_choices,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS],
        business_area,
        program_active,
    )
    response = authenticated_client.get(url_category_choices)
    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert len(resp_data) == 3
    assert resp_data[0]["name"] == "Survey with RapidPro"
    assert resp_data[0]["value"] == "RAPID_PRO"
    assert resp_data[1]["name"] == "Survey with SMS"
    assert resp_data[1]["value"] == "SMS"
    assert resp_data[2]["name"] == "Survey with manual process"
    assert resp_data[2]["value"] == "MANUAL"


def test_get_available_flows(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    url_flows,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS],
        business_area,
        program_active,
    )
    with (
        patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
            MagicMock(return_value=None),
        ),
        patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.get_flows",
            MagicMock(
                return_value=[
                    {"uuid": 123, "name": "flow2"},
                    {"uuid": 234, "name": "flow2"},
                ]
            ),
        ),
    ):
        response = authenticated_client.get(url_flows)
    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert len(resp_data) == 2


def test_filter_surveys_by_created_at(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    srv,
    srv_2,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST],
        business_area,
        whole_business_area_access=True,
    )
    srv.created_at = timezone.make_aware(datetime.datetime(year=2021, month=3, day=12))
    srv.save()
    srv_2.created_at = timezone.make_aware(datetime.datetime(year=2020, month=5, day=15))
    srv_2.save()
    response = authenticated_client.get(
        url_list,
        {
            "created_at_after": "2020-01-01",
            "created_at_before": "2020-12-31",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(srv_2.id)


def test_filter_surveys_by_created_by(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    user_creator,
    srv,
    srv_2,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST],
        business_area,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(url_list, {"created_by": f"{user_creator.id}"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(srv_2.id)


def test_search_surveys(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    srv,
    srv_2,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST],
        business_area,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(url_list, {"search": "Survey 1"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(srv.id)

    # Search by unicef_id suffix (last 4 digits)
    unicef_id_suffix = srv.unicef_id[-4:]
    response = authenticated_client.get(url_list, {"search": unicef_id_suffix})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    # At least srv should be found
    assert str(srv.id) in [r["id"] for r in results]

    response = authenticated_client.get(url_list, {"search": "SUR-"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 2
    results_ids = [survey["id"] for survey in results]
    assert str(srv.id) in results_ids
    assert str(srv_2.id) in results_ids


def test_get_available_flows_no_token(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    url_flows,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS],
        business_area,
        program_active,
    )
    with (
        patch(
            "hope.apps.accountability.api.views.RapidProAPI.__init__",
            MagicMock(side_effect=TokenNotProvidedError),
        ),
    ):
        response = authenticated_client.get(url_flows)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == ["Token is not provided."]


def test_sample_size(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    payment_plan,
    payment,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE],
        business_area,
        program_active,
    )
    url = reverse(
        "api:accountability:surveys-sample-size",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )
    data = {
        "payment_plan": str(payment_plan.pk),
        "sampling_type": Survey.SAMPLING_RANDOM,
        "random_sampling_arguments": {
            "age": {"max": 80, "min": 30},
            "sex": "MALE",
            "margin_of_error": 20.0,
            "confidence_interval": 0.9,
            "excluded_admin_areas": [],
        },
    }

    response = authenticated_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {
        "number_of_recipients": 1,
        "sample_size": 1,
        "excluded_recipients_count": 0,
    }

    data = {
        "sampling_type": Survey.SAMPLING_FULL_LIST,
        "full_list_arguments": {"excluded_admin_areas": []},
    }

    response = authenticated_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {
        "number_of_recipients": 1,
        "sample_size": 1,
        "excluded_recipients_count": 0,
    }


def test_sample_size_with_excluded_recipients_phone_validation(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    payment_plan,
    payment,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS, Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE],
        business_area,
        program_active,
    )

    rdi = RegistrationDataImportFactory(program=program_active, business_area=business_area)

    # Household 1: Empty phone number
    hoh_empty_phone = IndividualFactory(
        household=None,
        phone_no="",
        phone_no_valid=False,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi,
    )
    hh_empty_phone = HouseholdFactory(
        program=program_active,
        head_of_household=hoh_empty_phone,
        business_area=business_area,
        registration_data_import=rdi,
    )
    PaymentFactory(
        parent=payment_plan,
        program=program_active,
        household=hh_empty_phone,
        business_area=business_area,
        collector=hoh_empty_phone,
    )

    # Household 2: Invalid phone number
    hoh_invalid_phone = IndividualFactory(
        household=None,
        phone_no="invalid123",
        phone_no_valid=False,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi,
    )
    hh_invalid_phone = HouseholdFactory(
        program=program_active,
        head_of_household=hoh_invalid_phone,
        business_area=business_area,
        registration_data_import=rdi,
    )
    PaymentFactory(
        parent=payment_plan,
        program=program_active,
        household=hh_invalid_phone,
        business_area=business_area,
        collector=hoh_invalid_phone,
    )

    # Household 3: Valid phone number
    hoh_valid_phone = IndividualFactory(
        household=None,
        phone_no="+48600111111",
        phone_no_valid=True,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi,
    )
    hh_valid_phone = HouseholdFactory(
        program=program_active,
        head_of_household=hoh_valid_phone,
        business_area=business_area,
        registration_data_import=rdi,
    )
    PaymentFactory(
        parent=payment_plan,
        program=program_active,
        household=hh_valid_phone,
        business_area=business_area,
        collector=hoh_valid_phone,
    )

    # Household 4: Another valid phone number
    hoh_valid_phone2 = IndividualFactory(
        household=None,
        phone_no="+48600222222",
        phone_no_valid=True,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi,
    )
    hh_valid_phone2 = HouseholdFactory(
        program=program_active,
        head_of_household=hoh_valid_phone2,
        business_area=business_area,
        registration_data_import=rdi,
    )
    PaymentFactory(
        parent=payment_plan,
        program=program_active,
        household=hh_valid_phone2,
        business_area=business_area,
        collector=hoh_valid_phone2,
    )

    url = reverse(
        "api:accountability:surveys-sample-size",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )

    data = {
        "payment_plan": str(payment_plan.pk),
        "sampling_type": Survey.SAMPLING_FULL_LIST,
        "full_list_arguments": {"excluded_admin_areas": []},
    }

    response = authenticated_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_202_ACCEPTED

    response_data = response.json()
    # Should include 3 valid recipients (original hh_1 + 2 new valid phone households)
    # Should exclude 2 recipients (empty phone, invalid phone)
    assert response_data["number_of_recipients"] == 3
    assert response_data["sample_size"] == 3
    assert response_data["excluded_recipients_count"] == 2


def test_sample_size_all_excluded_recipients(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS, Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE],
        business_area,
        program_active,
    )

    rdi = RegistrationDataImportFactory(program=program_active, business_area=business_area)

    # Create a new payment plan with only invalid phone households
    payment_plan_invalid = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        business_area=business_area,
        program_cycle=program_active.cycles.first(),
    )

    # Create households with only invalid phone numbers
    for _i in range(2):
        hoh_invalid = IndividualFactory(
            household=None,
            phone_no="invalid",
            phone_no_valid=False,
            program=program_active,
            business_area=business_area,
            registration_data_import=rdi,
        )
        hh_invalid = HouseholdFactory(
            program=program_active,
            head_of_household=hoh_invalid,
            business_area=business_area,
            registration_data_import=rdi,
        )
        PaymentFactory(
            parent=payment_plan_invalid,
            program=program_active,
            household=hh_invalid,
            business_area=business_area,
            collector=hoh_invalid,
        )

    url = reverse(
        "api:accountability:surveys-sample-size",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )

    data = {
        "payment_plan": str(payment_plan_invalid.pk),
        "sampling_type": Survey.SAMPLING_FULL_LIST,
        "full_list_arguments": {"excluded_admin_areas": []},
    }

    response = authenticated_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_202_ACCEPTED

    response_data = response.json()
    assert response_data["number_of_recipients"] == 0
    assert response_data["sample_size"] == 0
    assert response_data["excluded_recipients_count"] == 2


def test_survey_creation_with_excluded_recipients(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS, Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE],
        business_area,
        program_active,
    )

    rdi = RegistrationDataImportFactory(program=program_active, business_area=business_area)

    payment_plan_mixed = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        business_area=business_area,
        program_cycle=program_active.cycles.first(),
    )

    # Valid phone household
    hoh_valid = IndividualFactory(
        household=None,
        phone_no="+48600333333",
        phone_no_valid=True,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi,
    )
    hh_valid = HouseholdFactory(
        program=program_active,
        head_of_household=hoh_valid,
        business_area=business_area,
        registration_data_import=rdi,
    )
    PaymentFactory(
        parent=payment_plan_mixed,
        program=program_active,
        household=hh_valid,
        business_area=business_area,
        collector=hoh_valid,
    )

    # Invalid phone household
    hoh_invalid = IndividualFactory(
        household=None,
        phone_no="notavalidphone",
        phone_no_valid=False,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi,
    )
    hh_invalid = HouseholdFactory(
        program=program_active,
        head_of_household=hoh_invalid,
        business_area=business_area,
        registration_data_import=rdi,
    )
    PaymentFactory(
        parent=payment_plan_mixed,
        program=program_active,
        household=hh_invalid,
        business_area=business_area,
        collector=hoh_invalid,
    )

    url = reverse(
        "api:accountability:surveys-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )

    # Test successful survey creation with mixed phone validation
    data = {
        "title": "Test Survey with Mixed Recipients",
        "body": "Test survey body",
        "category": Survey.CATEGORY_SMS,
        "payment_plan": str(payment_plan_mixed.pk),
        "sampling_type": Survey.SAMPLING_FULL_LIST,
        "full_list_arguments": {"excluded_admin_areas": []},
    }

    response = authenticated_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    survey = Survey.objects.get(pk=response.json()["id"])
    # Should have 1 valid recipient, 1 excluded
    assert survey.number_of_recipients == 1
    assert survey.recipients.count() == 1
    assert survey.recipients.first().head_of_household.phone_no_valid is True

    # Test survey creation with all invalid recipients should fail
    payment_plan_all_invalid = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        business_area=business_area,
        program_cycle=program_active.cycles.first(),
    )

    hoh_no_valid = IndividualFactory(
        household=None,
        phone_no="invalid",
        phone_no_valid=False,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi,
    )
    hh_no_valid = HouseholdFactory(
        program=program_active,
        head_of_household=hoh_no_valid,
        business_area=business_area,
        registration_data_import=rdi,
    )
    PaymentFactory(
        parent=payment_plan_all_invalid,
        program=program_active,
        household=hh_no_valid,
        business_area=business_area,
        collector=hoh_no_valid,
    )

    data_invalid = {
        "title": "Test Survey All Invalid",
        "body": "Test survey body",
        "category": Survey.CATEGORY_SMS,
        "payment_plan": str(payment_plan_all_invalid.pk),
        "sampling_type": Survey.SAMPLING_FULL_LIST,
        "full_list_arguments": {"excluded_admin_areas": []},
    }

    response = authenticated_client.post(url, data=data_invalid, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "recipients were excluded because they do not have valid phone numbers" in str(response.json())
