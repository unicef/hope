from unittest.mock import Mock, patch

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    ProgramFactory,
    SurveyFactory,
    UserFactory,
)
from hope.apps.accountability.celery_tasks import (
    export_survey_sample_task,
    export_survey_sample_task_action,
    send_survey_to_users,
    send_survey_to_users_action,
)
from hope.models import AsyncJob, Survey

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def survey(program, user):
    return SurveyFactory(
        business_area=program.business_area,
        program=program,
        created_by=user,
    )


@pytest.fixture
def survey_sms(program, user):
    return SurveyFactory(
        business_area=program.business_area,
        program=program,
        created_by=user,
        category=Survey.CATEGORY_SMS,
    )


@pytest.fixture
def survey_rapid_pro(program, user):
    return SurveyFactory(
        business_area=program.business_area,
        program=program,
        created_by=user,
        category=Survey.CATEGORY_RAPID_PRO,
        flow_id="flow-1",
    )


@pytest.fixture
def survey_manual(program, user):
    return SurveyFactory(
        business_area=program.business_area,
        program=program,
        created_by=user,
        category=Survey.CATEGORY_MANUAL,
    )


@pytest.fixture
def recipient_household(program, business_area):
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
def test_export_survey_sample_task_schedules_async_job(mock_queue: Mock, survey, user) -> None:
    export_survey_sample_task(str(survey.id), str(user.id))

    job = AsyncJob.objects.get()

    assert job.owner == user
    assert job.program == survey.program
    assert job.type == "JOB_TASK"
    assert job.action == "hope.apps.accountability.celery_tasks.export_survey_sample_task_action"
    assert job.config == {"survey_id": str(survey.id), "user_id": str(user.id)}
    assert job.group_key == f"export_survey_sample_task:{survey.id}"
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
        "hope.apps.accountability.celery_tasks.export_survey_sample_task_action",
        {"survey_id": str(survey.id), "user_id": str(user.id)},
    )
    service = mock_service_cls.return_value

    export_survey_sample_task_action(job)

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
        "hope.apps.accountability.celery_tasks.export_survey_sample_task_action",
        {"survey_id": str(survey.id), "user_id": str(user.id)},
    )

    export_survey_sample_task_action(job)

    mock_service_cls.assert_called_once_with(survey, user)
    mock_send_email_notification.assert_not_called()


@patch("hope.apps.accountability.celery_tasks.send_email_notification")
@patch("hope.apps.accountability.celery_tasks.ExportSurveySampleService")
def test_export_survey_sample_task_action_preserves_existing_errors_on_success(
    mock_service_cls: Mock,
    mock_send_email_notification: Mock,
    survey,
    user,
) -> None:
    survey.business_area.enable_email_notification = True
    survey.business_area.save(update_fields=["enable_email_notification"])
    job = create_async_job(
        "hope.apps.accountability.celery_tasks.export_survey_sample_task_action",
        {"survey_id": str(survey.id), "user_id": str(user.id)},
    )
    job.errors = {"error": "previous failure"}
    job.save(update_fields=["errors"])

    export_survey_sample_task_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "previous failure"}
    mock_service_cls.assert_called_once_with(survey, user)
    mock_send_email_notification.assert_called_once_with(mock_service_cls.return_value, user)


@patch("hope.apps.accountability.celery_tasks.ExportSurveySampleService")
def test_export_survey_sample_task_action_failure_sets_job_errors(mock_service_cls: Mock, survey, user) -> None:
    job = create_async_job(
        "hope.apps.accountability.celery_tasks.export_survey_sample_task_action",
        {"survey_id": str(survey.id), "user_id": str(user.id)},
    )
    mock_service_cls.side_effect = RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        export_survey_sample_task_action(job)

    job.refresh_from_db()
    assert job.errors == {
        "error": "boom",
    }


@patch.object(AsyncJob, "queue")
def test_send_survey_to_users_task_schedules_async_job(mock_queue: Mock, survey) -> None:
    send_survey_to_users(str(survey.id))

    job = AsyncJob.objects.get()

    assert job.owner == survey.created_by
    assert job.program == survey.program
    assert job.type == "JOB_TASK"
    assert job.action == "hope.apps.accountability.celery_tasks.send_survey_to_users_action"
    assert job.config == {"survey_id": str(survey.id)}
    assert job.group_key == f"send_survey_to_users:{survey.id}"
    assert job.description == f"Send survey to users for survey {survey.id}"
    mock_queue.assert_called_once_with()


@patch("hope.apps.accountability.celery_tasks.RapidProAPI")
def test_send_survey_to_users_action_sms(
    mock_rapid_pro_api: Mock, survey_sms, recipient_household, business_area
) -> None:
    survey_sms.recipients.add(recipient_household)
    job = create_async_job(
        "hope.apps.accountability.celery_tasks.send_survey_to_users_action",
        {"survey_id": str(survey_sms.id)},
    )

    send_survey_to_users_action(job)

    mock_rapid_pro_api.assert_called_once_with(business_area.slug, mock_rapid_pro_api.MODE_MESSAGE)
    phone_numbers, message_body = mock_rapid_pro_api.return_value.broadcast_message.call_args.args
    assert list(map(str, phone_numbers)) == ["+48123123123"]
    assert message_body == survey_sms.body
    assert job.errors == {}


@patch("hope.apps.accountability.celery_tasks.RapidProAPI")
def test_send_survey_to_users_action_manual_returns_without_api_call(mock_rapid_pro_api: Mock, survey_manual) -> None:
    job = create_async_job(
        "hope.apps.accountability.celery_tasks.send_survey_to_users_action",
        {"survey_id": str(survey_manual.id)},
    )

    send_survey_to_users_action(job)

    mock_rapid_pro_api.assert_not_called()
    assert job.errors == {}


@patch("hope.apps.accountability.celery_tasks.RapidProAPI")
def test_send_survey_to_users_action_sms_preserves_existing_errors_on_success(
    mock_rapid_pro_api: Mock, survey_sms, recipient_household, business_area
) -> None:
    survey_sms.recipients.add(recipient_household)
    job = create_async_job(
        "hope.apps.accountability.celery_tasks.send_survey_to_users_action",
        {"survey_id": str(survey_sms.id)},
    )
    job.errors = {"error": "previous failure"}
    job.save(update_fields=["errors"])

    send_survey_to_users_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "previous failure"}
    mock_rapid_pro_api.assert_called_once_with(business_area.slug, mock_rapid_pro_api.MODE_MESSAGE)


@patch("hope.apps.accountability.celery_tasks.RapidProAPI")
def test_send_survey_to_users_action_stores_start_flow_error(
    mock_rapid_pro_api: Mock, survey_rapid_pro, recipient_household
) -> None:
    survey_rapid_pro.recipients.add(recipient_household)
    job = create_async_job(
        "hope.apps.accountability.celery_tasks.send_survey_to_users_action",
        {"survey_id": str(survey_rapid_pro.id)},
    )
    successful_flow = Mock(response={"uuid": "flow-run-1"}, urns=["whatsapp:+48123123123"])
    job.errors = {"error": "previous failure"}
    job.save(update_fields=["errors"])
    mock_rapid_pro_api.return_value.start_flow.return_value = (
        [successful_flow],
        ValueError("partial failure"),
    )

    send_survey_to_users_action(job)

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
def test_send_survey_to_users_action_rapid_pro_success_preserves_existing_errors(
    mock_rapid_pro_api: Mock, survey_rapid_pro, recipient_household
) -> None:
    survey_rapid_pro.recipients.add(recipient_household)
    job = create_async_job(
        "hope.apps.accountability.celery_tasks.send_survey_to_users_action",
        {"survey_id": str(survey_rapid_pro.id)},
    )
    successful_flow = Mock(response={"uuid": "flow-run-2"}, urns=["whatsapp:+48123123123"])
    job.errors = {"error": "previous failure"}
    job.save(update_fields=["errors"])
    mock_rapid_pro_api.return_value.start_flow.return_value = ([successful_flow], None)

    send_survey_to_users_action(job)

    job.refresh_from_db()
    survey_rapid_pro.refresh_from_db()
    assert job.errors == {"error": "previous failure"}
    assert survey_rapid_pro.successful_rapid_pro_calls == [
        {
            "flow_uuid": "flow-run-2",
            "urns": ["whatsapp:+48123123123"],
        }
    ]


@patch("hope.apps.accountability.celery_tasks.RapidProAPI")
def test_send_survey_to_users_action_rapid_pro_excludes_already_contacted_numbers(
    mock_rapid_pro_api: Mock, survey_rapid_pro, recipient_household, business_area, program
) -> None:
    second_recipient = HouseholdFactory(business_area=business_area, program=program)
    second_recipient.head_of_household.phone_no = "+48999888777"
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
        "hope.apps.accountability.celery_tasks.send_survey_to_users_action",
        {"survey_id": str(survey_rapid_pro.id)},
    )
    mock_rapid_pro_api.return_value.start_flow.return_value = ([], None)

    send_survey_to_users_action(job)

    mock_rapid_pro_api.assert_called_once_with(business_area.slug, mock_rapid_pro_api.MODE_VERIFICATION)
    phone_numbers = mock_rapid_pro_api.return_value.start_flow.call_args.args[1]
    assert list(phone_numbers) == ["+48999888777"]


@patch("hope.apps.accountability.celery_tasks.RapidProAPI")
def test_send_survey_to_users_action_failure_sets_job_errors(
    mock_rapid_pro_api: Mock, survey_sms, recipient_household
) -> None:
    survey_sms.recipients.add(recipient_household)
    job = create_async_job(
        "hope.apps.accountability.celery_tasks.send_survey_to_users_action",
        {"survey_id": str(survey_sms.id)},
    )
    mock_rapid_pro_api.return_value.broadcast_message.side_effect = RuntimeError("send failed")

    with pytest.raises(RuntimeError, match="send failed"):
        send_survey_to_users_action(job)

    job.refresh_from_db()
    assert job.errors == {
        "error": "send failed",
    }
