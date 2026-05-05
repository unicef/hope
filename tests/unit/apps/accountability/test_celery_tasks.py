"""Tests for accountability celery tasks — send_survey_to_users coverage."""

from typing import Any
from unittest.mock import Mock, patch

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
from hope.apps.accountability.celery_tasks import (
    export_survey_sample_async_task,
    export_survey_sample_async_task_action,
    send_survey_to_users_async_task,
    send_survey_to_users_async_task_action,
)
from hope.models import AsyncJob, PaymentPlan, Program, Survey

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
def survey(program: Any, user: Any) -> Any:
    return SurveyFactory(
        business_area=program.business_area,
        program=program,
        created_by=user,
    )


@pytest.fixture
def survey_rapid_pro(program: Any, user: Any) -> Any:
    return SurveyFactory(
        business_area=program.business_area,
        program=program,
        created_by=user,
        category=Survey.CATEGORY_RAPID_PRO,
        flow_id="flow-1",
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


@pytest.fixture
def recipient_household(program: Any, business_area: Any) -> Any:
    household = HouseholdFactory(business_area=business_area, program=program)
    household.head_of_household.phone_no = "+48123123123"
    household.head_of_household.phone_no_valid = True
    household.head_of_household.save(update_fields=["phone_no", "phone_no_valid"])
    return household


def create_async_job(action: str, config: dict) -> AsyncJob:
    return AsyncJob.objects.create(
        type="JOB_TASK",
        action=action,
        config=config,
    )


@patch.object(AsyncJob, "queue")
def test_export_survey_sample_task_schedules_async_job(
    mock_queue: Mock, survey, user, django_capture_on_commit_callbacks
) -> None:
    with django_capture_on_commit_callbacks(execute=True):
        export_survey_sample_async_task(survey, user)

    job = AsyncJob.objects.get()

    assert job.owner == user
    assert job.program == survey.program
    assert job.type == "JOB_TASK"
    assert job.action == "hope.apps.accountability.celery_tasks.export_survey_sample_async_task_action"
    assert job.config == {"survey_id": str(survey.id), "user_id": str(user.id)}
    assert job.group_key == f"export_survey_sample_async_task:{survey.id}"
    assert job.description == f"Export survey sample for survey {survey.id}"
    mock_queue.assert_called_once_with()


@patch("hope.apps.accountability.celery_tasks.send_email_notification")
@patch("hope.apps.accountability.celery_tasks.ExportSurveySampleService")
def test_export_survey_sample_task_action_success(
    mock_service_cls: Mock,
    mock_send_email_notification: Mock,
    survey,
    user,
) -> None:
    survey.business_area.enable_email_notification = True
    survey.business_area.save(update_fields=["enable_email_notification"])
    job = create_async_job(
        "hope.apps.accountability.celery_tasks.export_survey_sample_async_task_action",
        {"survey_id": str(survey.id), "user_id": str(user.id)},
    )
    service = mock_service_cls.return_value

    export_survey_sample_async_task_action(job)

    mock_service_cls.assert_called_once_with(survey, user)
    service.export_sample.assert_called_once_with()
    mock_send_email_notification.assert_called_once_with(service, user)
    assert job.errors == {}


@patch("hope.apps.accountability.celery_tasks.send_email_notification")
@patch("hope.apps.accountability.celery_tasks.ExportSurveySampleService")
def test_export_survey_sample_task_action_success_without_email_notification(
    mock_service_cls: Mock,
    mock_send_email_notification: Mock,
    survey,
    user,
) -> None:
    survey.business_area.enable_email_notification = False
    survey.business_area.save(update_fields=["enable_email_notification"])
    job = create_async_job(
        "hope.apps.accountability.celery_tasks.export_survey_sample_async_task_action",
        {"survey_id": str(survey.id), "user_id": str(user.id)},
    )

    export_survey_sample_async_task_action(job)

    mock_service_cls.assert_called_once_with(survey, user)
    mock_send_email_notification.assert_not_called()


@patch.object(AsyncJob, "queue")
def test_send_survey_to_users_task_schedules_async_job(
    mock_queue: Mock, survey, django_capture_on_commit_callbacks
) -> None:
    with django_capture_on_commit_callbacks(execute=True):
        send_survey_to_users_async_task(survey)

    job = AsyncJob.objects.get()

    assert job.program == survey.program
    assert job.type == "JOB_TASK"
    assert job.action == "hope.apps.accountability.celery_tasks.send_survey_to_users_async_task_action"
    assert job.config == {"survey_id": str(survey.id)}
    assert job.group_key == f"send_survey_to_users_async_task:{survey.id}"
    assert job.description == f"Send survey to users for survey {survey.id}"
    mock_queue.assert_called_once_with()


@patch("hope.apps.accountability.celery_tasks.RapidProAPI")
def test_send_survey_to_users_action_sms(
    mock_rapid_pro_api: Mock, survey_sms, recipient_household, business_area
) -> None:
    survey_sms.recipients.add(recipient_household)
    job = create_async_job(
        "hope.apps.accountability.celery_tasks.send_survey_to_users_async_task_action",
        {"survey_id": str(survey_sms.id)},
    )

    send_survey_to_users_async_task_action(job)

    mock_rapid_pro_api.assert_called_once_with(business_area.slug, mock_rapid_pro_api.MODE_MESSAGE)
    phone_numbers, message_body = mock_rapid_pro_api.return_value.broadcast_message.call_args.args
    assert set(map(str, phone_numbers)) == {
        "+48123123123",
        "+48600123456",
    }
    assert message_body == survey_sms.body
    assert job.errors == {}


@patch("hope.apps.accountability.celery_tasks.RapidProAPI")
def test_send_survey_to_users_action_manual_returns_without_api_call(mock_rapid_pro_api: Mock, survey_manual) -> None:
    job = create_async_job(
        "hope.apps.accountability.celery_tasks.send_survey_to_users_async_task_action",
        {"survey_id": str(survey_manual.id)},
    )

    send_survey_to_users_async_task_action(job)

    mock_rapid_pro_api.assert_not_called()
    assert job.errors == {}


@patch("hope.apps.accountability.celery_tasks.RapidProAPI")
def test_send_survey_to_users_action_stores_start_flow_error(
    mock_rapid_pro_api: Mock, survey_rapid_pro, recipient_household
) -> None:
    survey_rapid_pro.recipients.add(recipient_household)
    job = create_async_job(
        "hope.apps.accountability.celery_tasks.send_survey_to_users_async_task_action",
        {"survey_id": str(survey_rapid_pro.id)},
    )
    successful_flow = Mock(response={"uuid": "flow-run-1"}, urns=["whatsapp:+48123123123"])
    job.errors = {"error": "previous failure"}
    job.save(update_fields=["errors"])
    mock_rapid_pro_api.return_value.start_flow.return_value = (
        [successful_flow],
        ValueError("partial failure"),
    )

    send_survey_to_users_async_task_action(job)

    job.refresh_from_db()
    survey_rapid_pro.refresh_from_db()
    assert job.errors == {
        "start_flow_error": "partial failure",
    }
    assert survey_rapid_pro.successful_rapid_pro_calls == [
        {
            "flow_uuid": "flow-run-1",
            "urns": ["whatsapp:+48123123123"],
        }
    ]


@patch("hope.apps.accountability.celery_tasks.RapidProAPI")
def test_send_survey_to_users_action_rapid_pro_excludes_already_contacted_numbers(
    mock_rapid_pro_api: Mock, survey_rapid_pro, recipient_household, business_area, program
) -> None:
    captured_phone_numbers = {}
    second_recipient = HouseholdFactory(business_area=business_area, program=program)
    second_recipient.head_of_household.phone_no = "+48577123654"
    second_recipient.head_of_household.phone_no_valid = True
    second_recipient.head_of_household.save(update_fields=["phone_no", "phone_no_valid"])
    survey_rapid_pro.recipients.add(recipient_household, second_recipient)
    survey_rapid_pro.successful_rapid_pro_calls = [
        {
            "flow_uuid": "flow-run-old",
            "urns": ["+48123123123"],
        }
    ]
    survey_rapid_pro.save(update_fields=["successful_rapid_pro_calls"])
    job = create_async_job(
        "hope.apps.accountability.celery_tasks.send_survey_to_users_async_task_action",
        {"survey_id": str(survey_rapid_pro.id)},
    )

    def capture_phone_numbers(_flow_id, phone_numbers):
        captured_phone_numbers["value"] = list(phone_numbers)
        return [], None

    mock_rapid_pro_api.return_value.start_flow.side_effect = capture_phone_numbers

    assert {
        str(phone)
        for phone in survey_rapid_pro.recipients.filter(head_of_household__phone_no_valid=True).values_list(
            "head_of_household__phone_no", flat=True
        )
    } == {"+48123123123", "+48577123654"}

    send_survey_to_users_async_task_action(job)

    mock_rapid_pro_api.assert_called_once_with(business_area.slug, mock_rapid_pro_api.MODE_VERIFICATION)
    assert captured_phone_numbers["value"] == ["+48577123654"]
