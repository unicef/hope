from unittest.mock import Mock, patch

from celery.exceptions import TaskError
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.core.celery_tasks import async_job_task
from hope.apps.household.forms import CreateTargetPopulationTextForm
from hope.apps.targeting.celery_tasks import (
    _serialize_form_data,
    create_tp_from_list_async_task,
    create_tp_from_list_async_task_action,
)
from hope.models import AsyncJob, PaymentPlan

pytestmark = pytest.mark.django_db


def queue_and_run_async_task(task: object, *args: object, **kwargs: object) -> object:
    with patch("hope.apps.targeting.celery_tasks.AsyncJob.queue", autospec=True):
        task(*args, **kwargs)
    job = AsyncJob.objects.latest("pk")
    return async_job_task.run(job._meta.label_lower, job.pk, job.version)


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program_cycle(program):
    return ProgramCycleFactory(program=program)


@pytest.fixture
def form_data(program_cycle):
    return {
        "action": "create",
        "name": "Test TP",
        "target_field": "unicef_id",
        "separator": ",",
        "criteria": "123,333",
        "program_cycle": program_cycle.pk,
    }


@pytest.fixture
def valid_form(program_cycle):
    form = Mock(spec=CreateTargetPopulationTextForm)
    form.is_valid.return_value = True
    form.cleaned_data = {
        "name": "Test TP",
        "target_field": "unicef_id",
        "separator": ",",
        "criteria": ["123,333"],
        "program_cycle": program_cycle,
    }
    return form


@patch("hope.apps.household.forms.CreateTargetPopulationTextForm")
@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.create_payments")
def test_create_tp_from_list_creates_payment_plan_and_triggers_payments(
    mock_create_payments,
    mock_form_class,
    form_data,
    valid_form,
    user,
    program,
):
    mock_form_class.return_value = valid_form

    queue_and_run_async_task(
        create_tp_from_list_async_task,
        form_data,
        str(user.pk),
        str(program.pk),
    )

    payment_plan = PaymentPlan.objects.get(name="Test TP")

    mock_create_payments.assert_called_once_with(payment_plan)
    assert payment_plan.business_area == program.business_area
    assert payment_plan.program_cycle == valid_form.cleaned_data["program_cycle"]
    assert payment_plan.created_by == user
    assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK


@patch("hope.apps.targeting.celery_tasks.logger.warning")
@patch("hope.apps.targeting.celery_tasks.CreateTargetPopulationTextForm")
def test_create_tp_from_list_action_raises_task_error_when_form_is_invalid(
    mock_form_class,
    mock_warning,
    form_data,
    program,
    user,
) -> None:
    invalid_form = Mock(spec=CreateTargetPopulationTextForm)
    invalid_form.is_valid.return_value = False
    invalid_form.errors = {"name": ["This field is required."]}
    mock_form_class.return_value = invalid_form
    job = AsyncJob(
        config={
            "form_data": form_data,
            "user_id": str(user.pk),
            "program_pk": str(program.pk),
        }
    )

    with pytest.raises(TaskError, match="Form validation failed"):
        create_tp_from_list_async_task_action(job)

    mock_form_class.assert_called_once_with(form_data, program=program)
    mock_warning.assert_called_once()


def test_serialize_form_data_serializes_nested_lists_with_uuids(program, user) -> None:
    program_uuid = program.pk
    user_uuid = user.pk

    value = {
        "items": [
            program_uuid,
            {"nested": [user_uuid]},
        ]
    }

    assert _serialize_form_data(value) == {
        "items": [
            str(program_uuid),
            {"nested": [str(user_uuid)]},
        ]
    }
