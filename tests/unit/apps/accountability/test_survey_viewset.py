"""Tests for Survey ViewSet."""

import datetime
from typing import Any
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
def srv_created_2021(program_active, business_area, user, payment_plan):
    srv = SurveyFactory(
        program=program_active,
        business_area=business_area,
        created_by=user,
        title="Survey 2021",
        body="Survey body 2021",
        flow_id="id2021",
        sampling_type=Survey.SAMPLING_FULL_LIST,
        category=Survey.CATEGORY_SMS,
        payment_plan=payment_plan,
    )
    srv.created_at = timezone.make_aware(datetime.datetime(year=2021, month=3, day=12))
    srv.save()
    return srv


@pytest.fixture
def srv_created_2020(program_active, business_area, user_creator, payment_plan):
    srv = SurveyFactory(
        program=program_active,
        business_area=business_area,
        created_by=user_creator,
        title="Survey 2020",
        body="Survey body 2020",
        flow_id="id2020",
        sampling_type=Survey.SAMPLING_RANDOM,
        category=Survey.CATEGORY_MANUAL,
        payment_plan=payment_plan,
    )
    srv.created_at = timezone.make_aware(datetime.datetime(year=2020, month=5, day=15))
    srv.save()
    return srv


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


@pytest.fixture
def rdi_for_phone_tests(program_active, business_area):
    return RegistrationDataImportFactory(program=program_active, business_area=business_area)


@pytest.fixture
def hoh_empty_phone(program_active, business_area, rdi_for_phone_tests):
    return IndividualFactory(
        household=None,
        phone_no="",
        phone_no_valid=False,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi_for_phone_tests,
    )


@pytest.fixture
def hh_empty_phone(program_active, business_area, rdi_for_phone_tests, hoh_empty_phone):
    return HouseholdFactory(
        program=program_active,
        head_of_household=hoh_empty_phone,
        business_area=business_area,
        registration_data_import=rdi_for_phone_tests,
    )


@pytest.fixture
def payment_empty_phone(payment_plan, program_active, business_area, hh_empty_phone, hoh_empty_phone):
    return PaymentFactory(
        parent=payment_plan,
        program=program_active,
        household=hh_empty_phone,
        business_area=business_area,
        collector=hoh_empty_phone,
    )


@pytest.fixture
def hoh_invalid_phone(program_active, business_area, rdi_for_phone_tests):
    return IndividualFactory(
        household=None,
        phone_no="invalid123",
        phone_no_valid=False,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi_for_phone_tests,
    )


@pytest.fixture
def hh_invalid_phone(program_active, business_area, rdi_for_phone_tests, hoh_invalid_phone):
    return HouseholdFactory(
        program=program_active,
        head_of_household=hoh_invalid_phone,
        business_area=business_area,
        registration_data_import=rdi_for_phone_tests,
    )


@pytest.fixture
def payment_invalid_phone(payment_plan, program_active, business_area, hh_invalid_phone, hoh_invalid_phone):
    return PaymentFactory(
        parent=payment_plan,
        program=program_active,
        household=hh_invalid_phone,
        business_area=business_area,
        collector=hoh_invalid_phone,
    )


@pytest.fixture
def hoh_valid_phone(program_active, business_area, rdi_for_phone_tests):
    return IndividualFactory(
        household=None,
        phone_no="+48600111111",
        phone_no_valid=True,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi_for_phone_tests,
    )


@pytest.fixture
def hh_valid_phone(program_active, business_area, rdi_for_phone_tests, hoh_valid_phone):
    return HouseholdFactory(
        program=program_active,
        head_of_household=hoh_valid_phone,
        business_area=business_area,
        registration_data_import=rdi_for_phone_tests,
    )


@pytest.fixture
def payment_valid_phone(payment_plan, program_active, business_area, hh_valid_phone, hoh_valid_phone):
    return PaymentFactory(
        parent=payment_plan,
        program=program_active,
        household=hh_valid_phone,
        business_area=business_area,
        collector=hoh_valid_phone,
    )


@pytest.fixture
def hoh_valid_phone2(program_active, business_area, rdi_for_phone_tests):
    return IndividualFactory(
        household=None,
        phone_no="+48600222222",
        phone_no_valid=True,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi_for_phone_tests,
    )


@pytest.fixture
def hh_valid_phone2(program_active, business_area, rdi_for_phone_tests, hoh_valid_phone2):
    return HouseholdFactory(
        program=program_active,
        head_of_household=hoh_valid_phone2,
        business_area=business_area,
        registration_data_import=rdi_for_phone_tests,
    )


@pytest.fixture
def payment_valid_phone2(payment_plan, program_active, business_area, hh_valid_phone2, hoh_valid_phone2):
    return PaymentFactory(
        parent=payment_plan,
        program=program_active,
        household=hh_valid_phone2,
        business_area=business_area,
        collector=hoh_valid_phone2,
    )


@pytest.fixture
def payment_plan_all_invalid(user, business_area, program_active):
    return PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        business_area=business_area,
        program_cycle=program_active.cycles.first(),
    )


@pytest.fixture
def rdi_for_invalid_tests(program_active, business_area):
    return RegistrationDataImportFactory(program=program_active, business_area=business_area)


@pytest.fixture
def hoh_invalid_1(program_active, business_area, rdi_for_invalid_tests):
    return IndividualFactory(
        household=None,
        phone_no="invalid",
        phone_no_valid=False,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi_for_invalid_tests,
    )


@pytest.fixture
def hh_invalid_1(program_active, business_area, rdi_for_invalid_tests, hoh_invalid_1):
    return HouseholdFactory(
        program=program_active,
        head_of_household=hoh_invalid_1,
        business_area=business_area,
        registration_data_import=rdi_for_invalid_tests,
    )


@pytest.fixture
def payment_invalid_1(payment_plan_all_invalid, program_active, business_area, hh_invalid_1, hoh_invalid_1):
    return PaymentFactory(
        parent=payment_plan_all_invalid,
        program=program_active,
        household=hh_invalid_1,
        business_area=business_area,
        collector=hoh_invalid_1,
    )


@pytest.fixture
def hoh_invalid_2(program_active, business_area, rdi_for_invalid_tests):
    return IndividualFactory(
        household=None,
        phone_no="invalid",
        phone_no_valid=False,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi_for_invalid_tests,
    )


@pytest.fixture
def hh_invalid_2(program_active, business_area, rdi_for_invalid_tests, hoh_invalid_2):
    return HouseholdFactory(
        program=program_active,
        head_of_household=hoh_invalid_2,
        business_area=business_area,
        registration_data_import=rdi_for_invalid_tests,
    )


@pytest.fixture
def payment_invalid_2(payment_plan_all_invalid, program_active, business_area, hh_invalid_2, hoh_invalid_2):
    return PaymentFactory(
        parent=payment_plan_all_invalid,
        program=program_active,
        household=hh_invalid_2,
        business_area=business_area,
        collector=hoh_invalid_2,
    )


@pytest.fixture
def payment_plan_mixed(user, business_area, program_active):
    return PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        business_area=business_area,
        program_cycle=program_active.cycles.first(),
    )


@pytest.fixture
def rdi_for_mixed_tests(program_active, business_area):
    return RegistrationDataImportFactory(program=program_active, business_area=business_area)


@pytest.fixture
def hoh_valid_mixed(program_active, business_area, rdi_for_mixed_tests):
    return IndividualFactory(
        household=None,
        phone_no="+48600333333",
        phone_no_valid=True,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi_for_mixed_tests,
    )


@pytest.fixture
def hh_valid_mixed(program_active, business_area, rdi_for_mixed_tests, hoh_valid_mixed):
    return HouseholdFactory(
        program=program_active,
        head_of_household=hoh_valid_mixed,
        business_area=business_area,
        registration_data_import=rdi_for_mixed_tests,
    )


@pytest.fixture
def payment_valid_mixed(payment_plan_mixed, program_active, business_area, hh_valid_mixed, hoh_valid_mixed):
    return PaymentFactory(
        parent=payment_plan_mixed,
        program=program_active,
        household=hh_valid_mixed,
        business_area=business_area,
        collector=hoh_valid_mixed,
    )


@pytest.fixture
def hoh_invalid_mixed(program_active, business_area, rdi_for_mixed_tests):
    return IndividualFactory(
        household=None,
        phone_no="notavalidphone",
        phone_no_valid=False,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi_for_mixed_tests,
    )


@pytest.fixture
def hh_invalid_mixed(program_active, business_area, rdi_for_mixed_tests, hoh_invalid_mixed):
    return HouseholdFactory(
        program=program_active,
        head_of_household=hoh_invalid_mixed,
        business_area=business_area,
        registration_data_import=rdi_for_mixed_tests,
    )


@pytest.fixture
def payment_invalid_mixed(payment_plan_mixed, program_active, business_area, hh_invalid_mixed, hoh_invalid_mixed):
    return PaymentFactory(
        parent=payment_plan_mixed,
        program=program_active,
        household=hh_invalid_mixed,
        business_area=business_area,
        collector=hoh_invalid_mixed,
    )


@pytest.fixture
def payment_plan_creation_invalid(user, business_area, program_active):
    return PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        business_area=business_area,
        program_cycle=program_active.cycles.first(),
    )


@pytest.fixture
def hoh_creation_invalid(program_active, business_area, rdi_for_mixed_tests):
    return IndividualFactory(
        household=None,
        phone_no="invalid",
        phone_no_valid=False,
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi_for_mixed_tests,
    )


@pytest.fixture
def hh_creation_invalid(program_active, business_area, rdi_for_mixed_tests, hoh_creation_invalid):
    return HouseholdFactory(
        program=program_active,
        head_of_household=hoh_creation_invalid,
        business_area=business_area,
        registration_data_import=rdi_for_mixed_tests,
    )


@pytest.fixture
def payment_creation_invalid(
    payment_plan_creation_invalid, program_active, business_area, hh_creation_invalid, hoh_creation_invalid
):
    return PaymentFactory(
        parent=payment_plan_creation_invalid,
        program=program_active,
        household=hh_creation_invalid,
        business_area=business_area,
        collector=hoh_creation_invalid,
    )


def test_survey_list_returns_data_with_permission(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    srv,
    srv_2,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST], business_area, program_active
    )
    response = authenticated_client.get(url_list)

    assert response.status_code == status.HTTP_200_OK
    response_results = response.json()["results"]
    assert len(response_results) == 2
    result_by_id = {r["id"]: r for r in response_results}

    srv_result = result_by_id[str(srv.id)]
    assert srv_result["unicef_id"] == str(srv.unicef_id)
    assert srv_result["title"] == srv.title
    assert srv_result["body"] == srv.body
    assert srv_result["category"] == srv.get_category_display()
    assert srv_result["flow_id"] == srv.flow_id
    assert srv_result["rapid_pro_url"] == f"https://rapidpro.io/flow/results/{srv.flow_id}/"
    assert srv_result["created_by"] == f"{srv.created_by.first_name} {srv.created_by.last_name}"
    assert srv_result["has_valid_sample_file"] is None
    assert srv_result["sample_file_path"] is None
    assert srv_result["created_at"] == f"{srv.created_at:%Y-%m-%dT%H:%M:%SZ}"
    assert srv_result["number_of_recipients"] == srv.number_of_recipients

    srv_2_result = result_by_id[str(srv_2.id)]
    assert srv_2_result["unicef_id"] == str(srv_2.unicef_id)
    assert srv_2_result["title"] == srv_2.title
    assert srv_2_result["body"] == srv_2.body
    assert srv_2_result["category"] == srv_2.get_category_display()
    assert srv_2_result["flow_id"] == srv_2.flow_id
    assert srv_2_result["rapid_pro_url"] == f"https://rapidpro.io/flow/results/{srv_2.flow_id}/"
    assert srv_2_result["created_by"] == f"{srv_2.created_by.first_name} {srv_2.created_by.last_name}"
    assert srv_2_result["has_valid_sample_file"] is None
    assert srv_2_result["sample_file_path"] is None
    assert srv_2_result["created_at"] == f"{srv_2.created_at:%Y-%m-%dT%H:%M:%SZ}"
    assert srv_2_result["number_of_recipients"] == srv_2.number_of_recipients


def test_survey_list_returns_403_without_permission(
    authenticated_client,
    srv,
    srv_2,
    url_list,
) -> None:
    response = authenticated_client.get(url_list)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_survey_get_count_returns_data_with_permission(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    srv,
    srv_2,
    url_count,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST], business_area, program_active
    )
    response = authenticated_client.get(url_count)

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert resp_data["count"] == 2


def test_survey_get_count_returns_403_without_permission(
    authenticated_client,
    srv,
    srv_2,
    url_count,
) -> None:
    response = authenticated_client.get(url_count)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_survey_details_returns_data_with_permission(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    srv,
    url_details,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
            Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST,
        ],
        business_area,
        program_active,
    )
    response = authenticated_client.get(url_details)

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert "id" in resp_data
    assert resp_data["title"] == "Survey 1"
    assert resp_data["body"] == "Survey 1 body"
    assert resp_data["category"] == "Survey with SMS"


def test_survey_details_returns_403_without_permission(
    authenticated_client,
    srv,
    url_details,
) -> None:
    response = authenticated_client.get(url_details)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_survey_returns_created_with_permission(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    payment_plan,
    payment,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE], business_area, program_active
    )
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
    assert response.status_code == status.HTTP_201_CREATED
    resp_data = response.json()
    assert "id" in resp_data
    assert resp_data["title"] == "New SRV"
    assert resp_data["body"] == "LGTM"


def test_create_survey_with_payment_plan(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    payment_plan,
    payment,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE], business_area, program_active
    )
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


def test_create_survey_returns_403_without_permission(
    authenticated_client,
    payment_plan,
    payment,
    url_list,
) -> None:
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
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_survey_export_sample_returns_accepted_with_permission(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    srv,
    url_export_sample,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS], business_area, program_active
    )
    response = authenticated_client.get(url_export_sample)
    assert response.status_code == status.HTTP_202_ACCEPTED
    resp_data = response.json()
    assert "id" in resp_data
    assert resp_data["title"] == "Survey 1"


def test_survey_export_sample_returns_403_without_permission(
    authenticated_client,
    srv,
    url_export_sample,
) -> None:
    response = authenticated_client.get(url_export_sample)
    assert response.status_code == status.HTTP_403_FORBIDDEN


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
    srv_created_2021,
    srv_created_2020,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST],
        business_area,
        whole_business_area_access=True,
    )
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
    assert results[0]["id"] == str(srv_created_2020.id)


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
    # srv should be found when searching for "Survey 1"
    assert str(srv.id) in [r["id"] for r in results]
    # Verify the found survey has correct title
    srv_result = next(r for r in results if r["id"] == str(srv.id))
    assert srv_result["title"] == "Survey 1"

    unicef_id_suffix = srv.unicef_id[-4:]
    response = authenticated_client.get(url_list, {"search": unicef_id_suffix})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
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
    payment_empty_phone,
    payment_invalid_phone,
    payment_valid_phone,
    payment_valid_phone2,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS, Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE],
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
        "sampling_type": Survey.SAMPLING_FULL_LIST,
        "full_list_arguments": {"excluded_admin_areas": []},
    }

    response = authenticated_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_202_ACCEPTED

    response_data = response.json()
    assert response_data["number_of_recipients"] == 3
    assert response_data["sample_size"] == 3
    assert response_data["excluded_recipients_count"] == 2


def test_sample_size_all_excluded_recipients(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    payment_plan_all_invalid,
    payment_invalid_1,
    payment_invalid_2,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS, Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE],
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
        "payment_plan": str(payment_plan_all_invalid.pk),
        "sampling_type": Survey.SAMPLING_FULL_LIST,
        "full_list_arguments": {"excluded_admin_areas": []},
    }

    response = authenticated_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_202_ACCEPTED

    response_data = response.json()
    assert response_data["number_of_recipients"] == 0
    assert response_data["sample_size"] == 0
    assert response_data["excluded_recipients_count"] == 2


def test_survey_creation_with_mixed_phone_validation(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    payment_plan_mixed,
    payment_valid_mixed,
    payment_invalid_mixed,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS, Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE],
        business_area,
        program_active,
    )

    data = {
        "title": "Test Survey with Mixed Recipients",
        "body": "Test survey body",
        "category": Survey.CATEGORY_SMS,
        "payment_plan": str(payment_plan_mixed.pk),
        "sampling_type": Survey.SAMPLING_FULL_LIST,
        "full_list_arguments": {"excluded_admin_areas": []},
    }

    response = authenticated_client.post(url_list, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    survey = Survey.objects.get(pk=response.json()["id"])
    assert survey.number_of_recipients == 1
    assert survey.recipients.count() == 1
    assert survey.recipients.first().head_of_household.phone_no_valid is True


def test_survey_creation_fails_with_all_invalid_phones(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    payment_plan_creation_invalid,
    payment_creation_invalid,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS, Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE],
        business_area,
        program_active,
    )

    data = {
        "title": "Test Survey All Invalid",
        "body": "Test survey body",
        "category": Survey.CATEGORY_SMS,
        "payment_plan": str(payment_plan_creation_invalid.pk),
        "sampling_type": Survey.SAMPLING_FULL_LIST,
        "full_list_arguments": {"excluded_admin_areas": []},
    }

    response = authenticated_client.post(url_list, data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "recipients were excluded because they do not have valid phone numbers" in str(response.json())
