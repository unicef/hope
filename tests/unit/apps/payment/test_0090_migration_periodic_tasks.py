from importlib import import_module

from django.apps import apps as django_apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.utils.module_loading import import_string
from django_celery_beat.models import CrontabSchedule, PeriodicTask
import pytest

from extras.test_utils.factories import AsyncJobFactory, PaymentListFactory, PeriodicAsyncJobFactory
from hope.apps.core.tasks_schedules import TASKS_SCHEDULES

pytestmark = pytest.mark.django_db

migration = import_module("hope.apps.payment.migrations.0090_migration")
OWNER_ID = "00000000-0000-0000-0000-000000000001"
ACTION_RENAMES = tuple((old, new) for old, new in migration.TASK_RENAMES.items() if old.endswith("_async_task_action"))


@pytest.fixture(params=(AsyncJobFactory, PeriodicAsyncJobFactory), ids=("async_job", "periodic_async_job"))
def job_factory(request):
    return request.param


@pytest.fixture(params=ACTION_RENAMES, ids=[old.rsplit(".", 1)[-1] for old, _ in ACTION_RENAMES])
def queued_old_action(request, job_factory):
    old_action, new_action = request.param
    job = job_factory(action=old_action, job_name=old_action.rsplit(".", 1)[-1].removesuffix("_action"))
    return job, new_action


@pytest.fixture(
    params=(
        (
            "hope.apps.payment.celery_tasks.payment_plan_refresh_payees_async_task_action",
            "payment_plan_id",
            "payment_list_id",
        ),
        (
            "hope.apps.payment.celery_tasks.export_payment_plan_group_delivery_xlsx_async_task_action",
            "payment_plan_group_id",
            "payment_plan_id",
        ),
    ),
    ids=("list_owner", "plan_owner"),
)
def queued_old_owner_job(request, job_factory):
    old_action, old_key, new_key = request.param
    job = job_factory(action=old_action, config={old_key: OWNER_ID})
    return job, new_key


@pytest.fixture(
    params=(
        (
            "payment_plan_refresh_payees_async_task_action",
            "payment_plan_id",
            "payment_list_id",
            "mark_payment_plan_rebuild_error",
            "mark_payment_list_rebuild_error",
        ),
        (
            "import_payment_plan_group_delivery_from_xlsx_async_task_action",
            "payment_plan_group_id",
            "payment_plan_id",
            "notify_payment_plan_group_reconciliation_import_failure",
            "notify_payment_plan_reconciliation_import_failure",
        ),
    ),
    ids=("rebuild_failure", "reconciliation_failure"),
)
def queued_old_failure_job(request, job_factory):
    old_action, old_key, new_key, old_failure, new_failure = request.param
    prefix = "hope.apps.payment.celery_tasks."
    job = job_factory(
        action=f"{prefix}{old_action}",
        config={old_key: OWNER_ID, "on_failure_action": f"{prefix}{old_failure}"},
    )
    return job, new_key, f"{prefix}{new_failure}"


@pytest.fixture(
    params=migration.DROPPED_DEVELOP_ACTIONS,
    ids=[action.rsplit(".", 1)[-1] for action in migration.DROPPED_DEVELOP_ACTIONS],
)
def queued_develop_list_job(request, job_factory):
    return job_factory(action=request.param, config={"payment_plan_id": OWNER_ID})


@pytest.fixture
def queued_tp_from_list_job():
    return AsyncJobFactory(
        action="hope.apps.targeting.celery_tasks.create_tp_from_list_async_task_action",
        config={"form_data": {"name": "TP", "payment_plan_group": OWNER_ID}, "program_pk": OWNER_ID},
    )


@pytest.fixture
def payment_list_importing_fsp_extra_fields():
    return PaymentListFactory(background_action_status="XLSX_IMPORTING_FSP_EXTRA_FIELDS")


@pytest.fixture(params=("REJECTED", "ABORTED"))
def queued_old_vision_notification(request, job_factory):
    status = request.param
    return job_factory(
        action="hope.contrib.vision.tasks.notify_payment_plan_group_status_to_vision_async_task_action",
        job_name=f"notify_payment_plan_group_{status.lower()}_to_vision",
        config={"payment_plan_group_id": OWNER_ID, "vision_status": status},
    )


@pytest.fixture(
    params=(
        (
            "paymentlistsplit",
            "add_paymentplansplit",
            "add_paymentlistsplit",
            "Can add payment plan split",
            "Can add payment list split",
        ),
        (
            "paymentlist",
            "restart_preparing_payment_plan",
            "restart_preparing_payment_list",
            "Can restart Preparing Payment Plans",
            "Can restart Preparing Payment Lists",
        ),
    ),
    ids=("model_permission", "custom_permission"),
)
def old_permission(request):
    model, old_codename, new_codename, old_name, new_name = request.param
    content_type = ContentType.objects.get(app_label="payment", model=model)
    permission, _ = Permission.objects.get_or_create(
        content_type=content_type, codename=new_codename, defaults={"name": new_name}
    )
    Permission.objects.filter(pk=permission.pk).update(codename=old_codename, name=old_name)
    return permission, new_codename, new_name


@pytest.fixture
def overdue_emails_row_before_the_rename() -> PeriodicTask:
    return PeriodicTask.objects.create(
        name="periodic_send_payment_plan_reconciliation_overdue_emails_async_task",
        task="hope.apps.payment.celery_tasks.periodic_send_payment_plan_reconciliation_overdue_emails_async_task",
        crontab=CrontabSchedule.objects.create(minute="0", hour="2"),
    )


@pytest.fixture
def overdue_emails_row_after_the_rename() -> PeriodicTask:
    return PeriodicTask.objects.create(
        name="periodic_send_payment_list_reconciliation_overdue_emails_async_task",
        task="hope.apps.payment.celery_tasks.periodic_send_payment_list_reconciliation_overdue_emails_async_task",
        crontab=CrontabSchedule.objects.create(minute="0", hour="2"),
    )


def test_forwards_renames_the_periodic_task_row_to_the_schedule_key_beat_looks_it_up_by(
    overdue_emails_row_before_the_rename: PeriodicTask,
) -> None:
    migration.forwards(django_apps, connection.schema_editor())

    overdue_emails_row_before_the_rename.refresh_from_db()
    assert (
        overdue_emails_row_before_the_rename.name
        == "periodic_send_payment_list_reconciliation_overdue_emails_async_task"
    )
    assert (
        overdue_emails_row_before_the_rename.task
        == TASKS_SCHEDULES["periodic_send_payment_list_reconciliation_overdue_emails_async_task"]["task"]
    )


def test_backwards_gives_the_periodic_task_row_its_old_name_and_task(
    overdue_emails_row_after_the_rename: PeriodicTask,
) -> None:
    migration.backwards(django_apps, connection.schema_editor())

    overdue_emails_row_after_the_rename.refresh_from_db()
    assert (
        overdue_emails_row_after_the_rename.name
        == "periodic_send_payment_plan_reconciliation_overdue_emails_async_task"
    )
    assert (
        overdue_emails_row_after_the_rename.task
        == "hope.apps.payment.celery_tasks.periodic_send_payment_plan_reconciliation_overdue_emails_async_task"
    )


def test_forwards_renames_every_queued_action_and_job_name(queued_old_action) -> None:
    job, new_action = queued_old_action

    migration.forwards(django_apps, connection.schema_editor())

    job.refresh_from_db()
    assert job.action == new_action
    assert callable(import_string(job.action))
    assert job.job_name == new_action.rsplit(".", 1)[-1].removesuffix("_action")


def test_forwards_rewrites_both_owner_id_keys(queued_old_owner_job) -> None:
    job, new_key = queued_old_owner_job

    migration.forwards(django_apps, connection.schema_editor())

    job.refresh_from_db()
    assert callable(import_string(job.action))
    assert job.config == {new_key: OWNER_ID}


def test_forwards_drops_develop_jobs_that_hold_a_payment_list_id(queued_develop_list_job) -> None:
    job_model = type(queued_develop_list_job)

    migration.forwards(django_apps, connection.schema_editor())

    assert not job_model.objects.filter(pk=queued_develop_list_job.pk).exists()


def test_forwards_renames_the_payment_plan_field_in_queued_tp_from_list_jobs(queued_tp_from_list_job) -> None:
    migration.forwards(django_apps, connection.schema_editor())

    queued_tp_from_list_job.refresh_from_db()
    assert queued_tp_from_list_job.config == {
        "form_data": {"name": "TP", "payment_plan": OWNER_ID},
        "program_pk": OWNER_ID,
    }


def test_forwards_clears_the_fsp_extra_fields_import_status_of_payment_lists(
    payment_list_importing_fsp_extra_fields,
) -> None:
    migration.forwards(django_apps, connection.schema_editor())

    payment_list_importing_fsp_extra_fields.refresh_from_db()
    assert payment_list_importing_fsp_extra_fields.background_action_status is None


def test_forwards_rewrites_failure_handler_paths(queued_old_failure_job) -> None:
    job, new_key, new_failure = queued_old_failure_job

    migration.forwards(django_apps, connection.schema_editor())

    job.refresh_from_db()
    assert job.config == {new_key: OWNER_ID, "on_failure_action": new_failure}
    assert callable(import_string(job.config["on_failure_action"]))


def test_forwards_rewrites_status_specific_vision_job_names(queued_old_vision_notification) -> None:
    job = queued_old_vision_notification

    migration.forwards(django_apps, connection.schema_editor())

    job.refresh_from_db()
    assert job.job_name == f"notify_payment_plan_{job.config['vision_status'].lower()}_to_vision"
    assert job.config == {"payment_plan_id": OWNER_ID, "vision_status": job.config["vision_status"]}


def test_forwards_renames_default_and_custom_permissions(old_permission) -> None:
    permission, new_codename, new_name = old_permission

    migration.forwards(django_apps, connection.schema_editor())

    permission.refresh_from_db()
    assert permission.codename == new_codename
    assert permission.name == new_name
