"""Tests for accountability celery tasks — send_survey_to_users coverage."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    SurveyFactory,
    UserFactory,
)
from hope.models import PaymentPlan, Program, Survey

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(code="0060", slug="afghanistan", name="Afghanistan", active=True)


@pytest.fixture
def program(business_area: Any) -> Any:
    prog = ProgramFactory(
        name="Test Program",
        business_area=business_area,
        status=Program.ACTIVE,
    )
    ProgramCycleFactory(program=prog)
    return prog


@pytest.fixture
def user() -> Any:
    return UserFactory()


@pytest.fixture
def payment_plan(user: Any, business_area: Any, program: Any) -> Any:
    return PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        business_area=business_area,
        program_cycle=program.cycles.first(),
    )


@pytest.fixture
def rdi(program: Any, business_area: Any) -> Any:
    return RegistrationDataImportFactory(program=program, business_area=business_area)


@pytest.fixture
def hoh_valid(program: Any, business_area: Any, rdi: Any) -> Any:
    return IndividualFactory(
        household=None,
        phone_no="+48600123456",
        phone_no_valid=True,
        program=program,
        business_area=business_area,
        registration_data_import=rdi,
    )


@pytest.fixture
def household_valid(program: Any, business_area: Any, rdi: Any, hoh_valid: Any) -> Any:
    return HouseholdFactory(
        program=program,
        head_of_household=hoh_valid,
        business_area=business_area,
        registration_data_import=rdi,
    )


@pytest.fixture
def payment_valid(payment_plan: Any, program: Any, business_area: Any, household_valid: Any, hoh_valid: Any) -> Any:
    return PaymentFactory(
        parent=payment_plan,
        program=program,
        household=household_valid,
        business_area=business_area,
        collector=hoh_valid,
    )


@pytest.fixture
def survey_manual(program: Any, business_area: Any, user: Any, payment_plan: Any) -> Any:
    return SurveyFactory(
        program=program,
        business_area=business_area,
        created_by=user,
        title="Manual survey",
        body="body",
        category=Survey.CATEGORY_MANUAL,
        payment_plan=payment_plan,
    )


@pytest.fixture
def survey_sms(program: Any, business_area: Any, user: Any, payment_plan: Any, payment_valid: Any) -> Any:
    srv = SurveyFactory(
        program=program,
        business_area=business_area,
        created_by=user,
        title="SMS survey",
        body="body",
        category=Survey.CATEGORY_SMS,
        payment_plan=payment_plan,
    )
    srv.recipients.set([payment_valid.household])
    return srv


@pytest.fixture
def survey_rapid_pro_no_flow_id(
    program: Any, business_area: Any, user: Any, payment_plan: Any, payment_valid: Any
) -> Any:
    srv = SurveyFactory(
        program=program,
        business_area=business_area,
        created_by=user,
        title="RapidPro survey no flow",
        body="body",
        category=Survey.CATEGORY_RAPID_PRO,
        flow_id=None,
        payment_plan=payment_plan,
    )
    srv.recipients.set([payment_valid.household])
    return srv


@pytest.fixture
def survey_rapid_pro_with_flow_id(
    program: Any, business_area: Any, user: Any, payment_plan: Any, payment_valid: Any
) -> Any:
    srv = SurveyFactory(
        program=program,
        business_area=business_area,
        created_by=user,
        title="RapidPro survey with flow",
        body="body",
        category=Survey.CATEGORY_RAPID_PRO,
        flow_id="flow-uuid-123",
        payment_plan=payment_plan,
        successful_rapid_pro_calls=[],
    )
    srv.recipients.set([payment_valid.household])
    return srv


def test_send_survey_to_users_manual_category_returns_early(survey_manual: Any) -> None:
    from hope.apps.accountability.celery_tasks import send_survey_to_users

    with patch("hope.apps.accountability.celery_tasks.RapidProAPI") as mock_api_cls:
        send_survey_to_users(str(survey_manual.id))

    mock_api_cls.assert_not_called()


def test_send_survey_to_users_sms_category_broadcasts_list_of_phone_numbers(survey_sms: Any) -> None:
    from hope.apps.accountability.celery_tasks import send_survey_to_users

    mock_broadcast = MagicMock()
    mock_api_instance = MagicMock()
    mock_api_instance.broadcast_message = mock_broadcast

    with patch(
        "hope.apps.accountability.celery_tasks.RapidProAPI",
        return_value=mock_api_instance,
    ) as mock_api_cls:
        send_survey_to_users(str(survey_sms.id))

    mock_api_cls.assert_called_once()
    assert mock_api_cls.call_args[0][0] == survey_sms.business_area.slug
    # broadcast_message must be called with a list (not a QuerySet/ValuesQuerySet)
    assert mock_broadcast.called
    call_args = mock_broadcast.call_args
    phone_numbers_arg = call_args[0][0]
    assert isinstance(phone_numbers_arg, list)


def test_send_survey_to_users_rapid_pro_no_flow_id_returns_early(survey_rapid_pro_no_flow_id: Any) -> None:
    from hope.apps.accountability.celery_tasks import send_survey_to_users

    mock_start_flow = MagicMock()
    mock_api_instance = MagicMock()
    mock_api_instance.start_flow = mock_start_flow

    with patch(
        "hope.apps.accountability.celery_tasks.RapidProAPI",
        return_value=mock_api_instance,
    ):
        send_survey_to_users(str(survey_rapid_pro_no_flow_id.id))

    mock_start_flow.assert_not_called()


def test_send_survey_to_users_rapid_pro_calls_start_flow_and_saves(survey_rapid_pro_with_flow_id: Any) -> None:
    from hope.apps.accountability.celery_tasks import send_survey_to_users

    fake_flow_response = MagicMock()
    fake_flow_response.response = {"uuid": "run-uuid-1"}
    fake_flow_response.urns = ["+48600123456"]

    mock_api_instance = MagicMock()
    mock_api_instance.start_flow = MagicMock(return_value=([fake_flow_response], None))

    with patch(
        "hope.apps.accountability.celery_tasks.RapidProAPI",
        return_value=mock_api_instance,
    ):
        send_survey_to_users(str(survey_rapid_pro_with_flow_id.id))

    mock_api_instance.start_flow.assert_called_once()
    survey_rapid_pro_with_flow_id.refresh_from_db()
    assert len(survey_rapid_pro_with_flow_id.successful_rapid_pro_calls) == 1
    assert survey_rapid_pro_with_flow_id.successful_rapid_pro_calls[0]["flow_uuid"] == "run-uuid-1"
