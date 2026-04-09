import datetime
from decimal import Decimal
from tempfile import NamedTemporaryFile
from typing import Any
from unittest.mock import Mock, PropertyMock, patch

from celery.exceptions import Retry
from django.contrib.admin.options import get_content_type_for_model
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.utils import timezone
from flags.models import FlagState
import pytest

from extras.test_utils.factories import (
    DeliveryMechanismFactory,
    FileTempFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
    RuleCommitFactory,
    RuleFactory,
    UserFactory,
    WesternUnionPaymentPlanReportFactory,
)
from hope.apps.core.celery_tasks import async_retry_job_task
from hope.apps.payment.celery_tasks import (
    create_payment_plan_payment_list_xlsx_async_task_action,
    create_payment_plan_payment_list_xlsx_per_fsp_async_task,
    create_payment_plan_payment_list_xlsx_per_fsp_async_task_action,
    create_payment_verification_plan_xlsx_async_task,
    create_payment_verification_plan_xlsx_async_task_action,
    export_pdf_payment_plan_summary_async_task,
    export_pdf_payment_plan_summary_async_task_action,
    get_sync_run_rapid_pro_async_task,
    get_sync_run_rapid_pro_async_task_action,
    import_payment_plan_payment_list_from_xlsx_async_task,
    import_payment_plan_payment_list_per_fsp_from_xlsx_async_task,
    payment_plan_apply_custom_exchange_rate_async_task,
    payment_plan_apply_custom_exchange_rate_async_task_action,
    payment_plan_apply_engine_rule_async_task,
    payment_plan_apply_engine_rule_async_task_action,
    payment_plan_apply_steficon_hh_selection_async_task,
    payment_plan_apply_steficon_hh_selection_async_task_action,
    payment_plan_exclude_beneficiaries_async_task,
    payment_plan_full_rebuild_async_task,
    payment_plan_rebuild_stats_async_task,
    payment_plan_set_entitlement_flat_amount_async_task,
    periodic_send_payment_plan_reconciliation_overdue_emails_async_task,
    periodic_sync_payment_gateway_records_async_task,
    periodic_sync_payment_gateway_records_async_task_action,
    periodic_sync_payment_plan_invoices_western_union_ftp_async_task,
    prepare_follow_up_payment_plan_async_task,
    prepare_payment_plan_async_task,
    remove_old_cash_plan_payment_verification_xlsx_async_task,
    remove_old_cash_plan_payment_verification_xlsx_async_task_action,
    remove_old_payment_plan_payment_list_xlsx_async_task,
    send_payment_notification_emails_async_task,
    send_payment_plan_payment_list_xlsx_per_fsp_password_async_task,
    send_payment_plan_reconciliation_overdue_email_async_task,
    send_qcf_report_email_notifications_async_task,
    send_to_payment_gateway_async_task,
    update_exchange_rate_on_release_payments_async_task,
    update_exchange_rate_on_release_payments_async_task_action,
)
from hope.apps.payment.utils import generate_cache_key
from hope.models import (
    AsyncJob,
    AsyncJobModel,
    AsyncRetryJob,
    FileTemp,
    Payment,
    PaymentPlan,
    PaymentVerificationPlan,
    Rule,
)

pytestmark = pytest.mark.django_db


def queue_and_run_retry_task(task: object, *args: object, **kwargs: object) -> object:
    with patch("hope.apps.payment.celery_tasks.AsyncRetryJob.queue", autospec=True):
        task(*args, **kwargs)
    job = AsyncRetryJob.objects.latest("pk")
    return async_retry_job_task.run(job.pk, job.version)


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def payment_plan():
    return PaymentPlanFactory()


@pytest.fixture
def delivery_mechanism_cash():
    return DeliveryMechanismFactory(code="cash", name="Cash")


@pytest.fixture
def financial_service_provider(delivery_mechanism_cash):
    return FinancialServiceProviderFactory(
        delivery_mechanisms=[delivery_mechanism_cash],
    )


@pytest.fixture
def qcf_report(payment_plan):
    return WesternUnionPaymentPlanReportFactory(payment_plan=payment_plan)


@pytest.mark.parametrize(
    ("task", "job_model", "args_builder", "expected_job_name"),
    [
        (
            create_payment_plan_payment_list_xlsx_per_fsp_async_task,
            AsyncRetryJob,
            lambda payment_plan, user, rule: (payment_plan, str(user.pk), None),
            "create_payment_plan_payment_list_xlsx_per_fsp_async_task",
        ),
        (
            import_payment_plan_payment_list_from_xlsx_async_task,
            AsyncRetryJob,
            lambda payment_plan, user, rule: (payment_plan,),
            "import_payment_plan_payment_list_from_xlsx_async_task",
        ),
        (
            payment_plan_set_entitlement_flat_amount_async_task,
            AsyncRetryJob,
            lambda payment_plan, user, rule: (payment_plan,),
            "payment_plan_set_entitlement_flat_amount_async_task",
        ),
        (
            payment_plan_apply_custom_exchange_rate_async_task,
            AsyncRetryJob,
            lambda payment_plan, user, rule: (payment_plan,),
            "payment_plan_apply_custom_exchange_rate_async_task",
        ),
        (
            import_payment_plan_payment_list_per_fsp_from_xlsx_async_task,
            AsyncRetryJob,
            lambda payment_plan, user, rule: (payment_plan,),
            "import_payment_plan_payment_list_per_fsp_from_xlsx_async_task",
        ),
        (
            payment_plan_apply_engine_rule_async_task,
            AsyncRetryJob,
            lambda payment_plan, user, rule: (payment_plan, rule),
            "payment_plan_apply_engine_rule_async_task",
        ),
        (
            update_exchange_rate_on_release_payments_async_task,
            AsyncRetryJob,
            lambda payment_plan, user, rule: (payment_plan,),
            "update_exchange_rate_on_release_payments_async_task",
        ),
        (
            prepare_follow_up_payment_plan_async_task,
            AsyncRetryJob,
            lambda payment_plan, user, rule: (payment_plan,),
            "prepare_follow_up_payment_plan_async_task",
        ),
        (
            payment_plan_exclude_beneficiaries_async_task,
            AsyncRetryJob,
            lambda payment_plan, user, rule: (payment_plan, [], ""),
            "payment_plan_exclude_beneficiaries_async_task",
        ),
        (
            send_payment_plan_payment_list_xlsx_per_fsp_password_async_task,
            AsyncRetryJob,
            lambda payment_plan, user, rule: (payment_plan, str(user.pk)),
            "send_payment_plan_payment_list_xlsx_per_fsp_password_async_task",
        ),
        (
            send_payment_notification_emails_async_task,
            AsyncJob,
            lambda payment_plan, user, rule: (
                payment_plan,
                PaymentPlan.Action.SEND_FOR_APPROVAL.value,
                str(user.pk),
                "3 April 2026",
            ),
            "send_payment_notification_emails_async_task",
        ),
        (
            payment_plan_apply_steficon_hh_selection_async_task,
            AsyncRetryJob,
            lambda payment_plan, user, rule: (payment_plan, str(rule.pk)),
            "payment_plan_apply_steficon_hh_selection_async_task",
        ),
        (
            payment_plan_rebuild_stats_async_task,
            AsyncRetryJob,
            lambda payment_plan, user, rule: (payment_plan,),
            "payment_plan_rebuild_stats_async_task",
        ),
        (
            payment_plan_full_rebuild_async_task,
            AsyncRetryJob,
            lambda payment_plan, user, rule: (payment_plan, False),
            "payment_plan_full_rebuild_async_task",
        ),
        (
            send_payment_plan_reconciliation_overdue_email_async_task,
            AsyncRetryJob,
            lambda payment_plan, user, rule: (payment_plan,),
            "send_payment_plan_reconciliation_overdue_email_async_task",
        ),
    ],
)
def test_payment_plan_async_job_factories_attach_jobs_to_payment_plan(
    task: Any,
    job_model: type[AsyncJob] | type[AsyncRetryJob],
    args_builder: Any,
    expected_job_name: str,
) -> None:
    payment_plan = PaymentPlanFactory()
    user = UserFactory()
    rule = RuleFactory()

    with patch("django_celery_boost.models.CeleryTaskModel.queue", autospec=True) as mock_queue:
        task(*args_builder(payment_plan, user, rule))

    job = job_model.objects.latest("pk")
    assert job.content_object == payment_plan
    assert job.object_id == str(payment_plan.pk)
    assert job.job_name == expected_job_name
    mock_queue.assert_called_once()


@patch("hope.apps.payment.celery_tasks.logger")
def test_prepare_payment_plan_task_wrong_pp_status(mock_logger: Mock) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
    )
    payment_plan.refresh_from_db()
    queue_and_run_retry_task(prepare_payment_plan_async_task, payment_plan)
    mock_logger.info.assert_called_with("The Payment Plan must have the status TP_OPEN.")


@patch("hope.apps.payment.celery_tasks.logger")
def test_prepare_payment_plan_task_already_running(mock_logger: Mock) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_OPEN,
        build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
    )
    payment_plan.refresh_from_db()
    pp_id_str = str(payment_plan.pk)
    cache_key = generate_cache_key(
        {
            "task_name": "prepare_payment_plan_async_task",
            "payment_plan_id": str(payment_plan.id),
        }
    )
    cache.set(cache_key, True, timeout=300)
    queue_and_run_retry_task(prepare_payment_plan_async_task, payment_plan)
    mock_logger.info.assert_called_with(
        f"Task prepare_payment_plan_async_task with payment_plan_id {pp_id_str} already running."
    )


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.create_payments")
@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
def test_prepare_payment_plan_task_exception_handling(
    mock_retry: Mock, mock_logger: Mock, mock_create_payments: Mock
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_OPEN,
        build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
    )
    payment_plan.refresh_from_db()
    assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_PENDING

    mock_create_payments.side_effect = Exception("test")
    mock_retry.side_effect = Retry("retry")
    with pytest.raises(Retry):
        queue_and_run_retry_task(prepare_payment_plan_async_task, payment_plan=payment_plan)

    payment_plan.refresh_from_db()

    mock_logger.exception.assert_called_once_with("Prepare Payment Plan Error")
    mock_retry.assert_called_once_with(exc=mock_create_payments.side_effect)

    assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_FAILED


@patch("hope.models.payment_plan.PaymentPlan.update_money_fields")
@patch("hope.models.payment_plan.PaymentPlan.update_population_count_fields")
def test_payment_plan_rebuild_stats(
    mock_update_population_count_fields: Mock,
    mock_update_money_fields: Mock,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_STEFICON_WAIT,
        build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
    )
    PaymentFactory(parent=payment_plan)

    queue_and_run_retry_task(payment_plan_rebuild_stats_async_task, payment_plan)

    payment_plan.refresh_from_db(fields=["build_status", "built_at"])
    assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK
    assert payment_plan.built_at is not None
    mock_update_population_count_fields.assert_called_once()
    mock_update_money_fields.assert_called_once()


@patch("hope.models.payment_plan.PaymentPlan.update_population_count_fields")
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
def test_payment_plan_rebuild_stats_exception_handling(
    mock_retry: Mock, mock_update_population_count_fields: Mock
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_STEFICON_WAIT,
        build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
    )
    PaymentFactory(parent=payment_plan)
    mock_update_population_count_fields.side_effect = Exception("test")
    mock_retry.side_effect = Retry("retry")
    with pytest.raises(Retry):
        queue_and_run_retry_task(payment_plan_rebuild_stats_async_task, payment_plan)

    mock_retry.assert_called_once()


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.full_rebuild")
def test_payment_plan_full_rebuild(
    mock_full_rebuild: Mock,
    financial_service_provider,
    delivery_mechanism_cash,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_OPEN,
        build_status=PaymentPlan.BuildStatus.BUILD_STATUS_FAILED,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism_cash,
    )
    PaymentFactory(
        parent=payment_plan,
        financial_service_provider=financial_service_provider,
        delivery_type=delivery_mechanism_cash,
    )
    queue_and_run_retry_task(payment_plan_full_rebuild_async_task, payment_plan)

    payment_plan.refresh_from_db(fields=["build_status", "built_at"])
    assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK
    assert payment_plan.built_at is not None
    mock_full_rebuild.assert_called_once()


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.full_rebuild")
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
def test_payment_plan_full_rebuild_retry_exception_handling(mock_retry: Mock, mock_full_rebuild: Mock) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        build_status=PaymentPlan.BuildStatus.BUILD_STATUS_OK,
    )
    PaymentFactory(parent=payment_plan)
    mock_full_rebuild.side_effect = Exception("test")
    mock_retry.side_effect = Retry("retry")
    with pytest.raises(Retry):
        queue_and_run_retry_task(payment_plan_full_rebuild_async_task, payment_plan)

    mock_retry.assert_called_once()
    payment_plan.refresh_from_db()
    assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_FAILED


def test_create_payment_plan_payment_list_xlsx_per_fsp(
    financial_service_provider,
    delivery_mechanism_cash,
    user,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism_cash,
    )
    fsp_template = FinancialServiceProviderXlsxTemplateFactory()
    payment_plan.business_area.enable_email_notification = True
    payment_plan.business_area.save(update_fields=["enable_email_notification"])
    with (
        patch.object(
            PaymentPlan,
            "is_payment_gateway_and_all_sent_to_fsp",
            new_callable=PropertyMock,
        ) as mock_is_payment_gateway_and_all_sent_to_fsp,
        patch(
            "hope.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service."
            "XlsxPaymentPlanExportPerFspService.generate_token_and_order_numbers"
        ) as mock_generate_tokens,
        patch(
            "hope.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service."
            "XlsxPaymentPlanExportPerFspService.send_email_with_passwords"
        ) as mock_send_passwords,
        patch("hope.apps.payment.celery_tasks.send_email_notification") as mock_send_email,
    ):
        mock_is_payment_gateway_and_all_sent_to_fsp.return_value = True
        assert payment_plan.is_payment_gateway_and_all_sent_to_fsp

        queue_and_run_retry_task(
            create_payment_plan_payment_list_xlsx_per_fsp_async_task, payment_plan, str(user.pk), str(fsp_template.pk)
        )

        payment_plan.refresh_from_db()
        file_obj = FileTemp.objects.get(object_id=payment_plan.id)

        assert payment_plan.background_action_status is None
        assert payment_plan.has_export_file
        assert payment_plan.export_file_per_fsp.file.name.startswith(
            f"payment_plan_payment_list_{payment_plan.unicef_id}"
        )
        assert payment_plan.export_file_per_fsp.file.name.endswith(".zip")
        assert file_obj.password is not None
        assert file_obj.xlsx_password is not None
        mock_generate_tokens.assert_called_once()
        mock_send_email.assert_called_once()
        mock_send_passwords.assert_called_once_with(user, payment_plan)


@patch("hope.apps.payment.notifications.MailjetClient.send_email")
def test_send_payment_plan_payment_list_xlsx_per_fsp_password(
    mock_mailjet_send: Mock,
    financial_service_provider,
    delivery_mechanism_cash,
    user,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.FINISHED,
        background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism_cash,
    )
    fsp_template = FinancialServiceProviderXlsxTemplateFactory()
    with patch.object(
        PaymentPlan,
        "is_payment_gateway_and_all_sent_to_fsp",
        new_callable=PropertyMock,
    ) as mock_is_payment_gateway_and_all_sent_to_fsp:
        mock_is_payment_gateway_and_all_sent_to_fsp.return_value = True
        assert payment_plan.is_payment_gateway_and_all_sent_to_fsp

        queue_and_run_retry_task(
            create_payment_plan_payment_list_xlsx_per_fsp_async_task, payment_plan, str(user.pk), str(fsp_template.pk)
        )
        payment_plan.refresh_from_db()
        file_obj = FileTemp.objects.get(object_id=payment_plan.id)

        assert payment_plan.background_action_status is None
        assert payment_plan.export_file_per_fsp == file_obj
        assert isinstance(file_obj.password, str)
        assert isinstance(file_obj.xlsx_password, str)
        assert len(file_obj.xlsx_password) == 12
        assert len(file_obj.password) == 12

        queue_and_run_retry_task(
            send_payment_plan_payment_list_xlsx_per_fsp_password_async_task, payment_plan, str(user.pk)
        )

        assert mock_mailjet_send.call_count == 3

    from hope.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import (
        XlsxPaymentPlanExportPerFspService,
    )

    assert XlsxPaymentPlanExportPerFspService._as_plain_text(memoryview(b"zip-pass")) == "zip-pass"
    assert XlsxPaymentPlanExportPerFspService._as_plain_text(b"xlsx-pass") == "xlsx-pass"


@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
@patch("hope.models.User")
def test_send_payment_plan_payment_list_xlsx_per_fsp_password_failure(
    mock_get_user_model: Mock, mock_retry: Mock, mock_logger: Mock
) -> None:
    payment_plan = PaymentPlanFactory()
    mock_retry.side_effect = Retry("retry")
    mock_get_user_model.objects.get.side_effect = Exception("User not found")
    with pytest.raises(Retry):
        queue_and_run_retry_task(
            send_payment_plan_payment_list_xlsx_per_fsp_password_async_task, payment_plan, "invalid-user-id-123"
        )

    mock_logger.exception.assert_not_called()
    mock_retry.assert_called_once()


@patch("hope.apps.payment.xlsx.xlsx_payment_plan_export_service.XlsxPaymentPlanExportService.save_xlsx_file")
def test_create_payment_plan_payment_list_xlsx_action_marks_error_on_exception(
    mock_save_xlsx_file: Mock,
    user,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
    )
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.payment.celery_tasks.create_payment_plan_payment_list_xlsx_async_task_action",
        config={"payment_plan_id": str(payment_plan.pk), "user_id": str(user.pk)},
    )
    mock_save_xlsx_file.side_effect = Exception("xlsx failed")

    with pytest.raises(Exception, match="xlsx failed"):
        create_payment_plan_payment_list_xlsx_async_task_action(job)

    payment_plan.refresh_from_db(fields=["background_action_status"])
    assert payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.XLSX_EXPORT_ERROR


@patch(
    "hope.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service.XlsxPaymentPlanExportPerFspService.export_per_fsp"
)
def test_create_payment_plan_payment_list_xlsx_per_fsp_action_marks_error_on_exception(
    mock_export_per_fsp: Mock,
    financial_service_provider,
    delivery_mechanism_cash,
    user,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism_cash,
    )
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.payment.celery_tasks.create_payment_plan_payment_list_xlsx_per_fsp_async_task_action",
        config={"payment_plan_id": str(payment_plan.pk), "user_id": str(user.pk), "fsp_xlsx_template_id": None},
    )
    mock_export_per_fsp.side_effect = Exception("per-fsp xlsx failed")

    with pytest.raises(Exception, match="per-fsp xlsx failed"):
        create_payment_plan_payment_list_xlsx_per_fsp_async_task_action(job)

    payment_plan.refresh_from_db(fields=["background_action_status"])
    assert payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.XLSX_EXPORT_ERROR


@patch("hope.apps.payment.celery_tasks.send_email_notification")
@patch("hope.apps.payment.xlsx.xlsx_verification_export_service.XlsxVerificationExportService.save_xlsx_file")
def test_create_payment_verification_plan_xlsx_action_saves_file_and_sends_email(
    mock_save_xlsx_file: Mock,
    mock_send_email: Mock,
    user,
) -> None:
    payment_verification_plan = PaymentVerificationPlanFactory(
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX
    )
    payment_verification_plan.business_area.enable_email_notification = True
    payment_verification_plan.business_area.save(update_fields=["enable_email_notification"])
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.payment.celery_tasks.create_payment_verification_plan_xlsx_async_task_action",
        config={"payment_verification_plan_id": str(payment_verification_plan.pk), "user_id": str(user.pk)},
    )

    create_payment_verification_plan_xlsx_async_task_action(job)

    payment_verification_plan.refresh_from_db(fields=["xlsx_file_exporting"])
    assert payment_verification_plan.xlsx_file_exporting is False
    mock_save_xlsx_file.assert_called_once_with(user)
    mock_send_email.assert_called_once()


@patch("hope.apps.payment.celery_tasks.send_email_notification")
@patch("hope.apps.payment.xlsx.xlsx_verification_export_service.XlsxVerificationExportService.save_xlsx_file")
def test_create_payment_verification_plan_xlsx_action_skips_save_when_file_exists_and_email_is_disabled(
    mock_save_xlsx_file: Mock,
    mock_send_email: Mock,
    user,
) -> None:
    payment_verification_plan = PaymentVerificationPlanFactory(
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX
    )
    payment_verification_plan.business_area.enable_email_notification = False
    payment_verification_plan.business_area.save(update_fields=["enable_email_notification"])
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.payment.celery_tasks.create_payment_verification_plan_xlsx_async_task_action",
        config={"payment_verification_plan_id": str(payment_verification_plan.pk), "user_id": str(user.pk)},
    )

    with patch.object(
        PaymentVerificationPlan,
        "has_xlsx_payment_verification_plan_file",
        new_callable=PropertyMock,
        return_value=True,
    ):
        create_payment_verification_plan_xlsx_async_task_action(job)

    payment_verification_plan.refresh_from_db(fields=["xlsx_file_exporting"])
    assert payment_verification_plan.xlsx_file_exporting is False
    mock_save_xlsx_file.assert_not_called()
    mock_send_email.assert_not_called()


@patch("hope.apps.payment.celery_tasks.send_email_notification_on_commit")
@patch("hope.apps.payment.xlsx.xlsx_payment_plan_export_service.XlsxPaymentPlanExportService.save_xlsx_file")
def test_create_payment_plan_payment_list_xlsx_action_sends_email_when_enabled(
    mock_save_xlsx_file: Mock,
    mock_send_email_on_commit: Mock,
    payment_plan: PaymentPlan,
    user,
) -> None:
    payment_plan.business_area.enable_email_notification = True
    payment_plan.business_area.save(update_fields=["enable_email_notification"])
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.payment.celery_tasks.create_payment_plan_payment_list_xlsx_async_task_action",
        config={"payment_plan_id": str(payment_plan.pk), "user_id": str(user.pk)},
    )

    create_payment_plan_payment_list_xlsx_async_task_action(job)

    mock_save_xlsx_file.assert_called_once_with(user)
    mock_send_email_on_commit.assert_called_once()


@patch("hope.apps.payment.celery_tasks.send_email_notification")
@patch("hope.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service.XlsxPaymentPlanExportPerFspService")
def test_create_payment_plan_payment_list_xlsx_per_fsp_action_generates_tokens_and_sends_emails(
    mock_service_cls: Mock,
    mock_send_email: Mock,
    financial_service_provider,
    delivery_mechanism_cash,
    user,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism_cash,
    )
    payment_plan.business_area.enable_email_notification = True
    payment_plan.business_area.save(update_fields=["enable_email_notification"])
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.payment.celery_tasks.create_payment_plan_payment_list_xlsx_per_fsp_async_task_action",
        config={
            "payment_plan_id": str(payment_plan.pk),
            "user_id": str(user.pk),
            "fsp_xlsx_template_id": "template-id",
        },
    )
    mock_service = mock_service_cls.return_value
    mock_service.payment_generate_token_and_order_numbers = True

    create_payment_plan_payment_list_xlsx_per_fsp_async_task_action(job)

    mock_service.generate_token_and_order_numbers.assert_called_once()
    mock_service.export_per_fsp.assert_called_once_with(user)
    mock_send_email.assert_called_once_with(mock_service, user)
    mock_service.send_email_with_passwords.assert_called_once_with(user, payment_plan)


def test_get_sync_run_rapid_pro_task_queues_retry_job() -> None:
    with patch("hope.apps.payment.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        get_sync_run_rapid_pro_async_task()

    job = AsyncRetryJob.objects.latest("pk")
    assert job.type == AsyncJobModel.JobType.JOB_TASK
    assert job.action == "hope.apps.payment.celery_tasks.get_sync_run_rapid_pro_async_task_action"
    assert job.config == {}
    assert job.group_key == "get_sync_run_rapid_pro_async_task"
    assert job.description == "Sync RapidPro verification runs"
    mock_queue.assert_called_once()


@patch("hope.apps.payment.celery_tasks.CheckRapidProVerificationTask.execute")
def test_get_sync_run_rapid_pro_task_action_executes_check(mock_execute: Mock) -> None:
    get_sync_run_rapid_pro_async_task_action()

    mock_execute.assert_called_once()


@patch("hope.apps.payment.celery_tasks.get_quantity_in_usd")
@patch("hope.models.payment_plan.PaymentPlan.update_money_fields")
@patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate")
def test_update_exchange_rate_on_release_payments_success(
    mock_get_exchange_rate: Mock,
    mock_update_money_fields: Mock,
    mock_get_quantity_in_usd: Mock,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        currency="PLN",
        exchange_rate=0.1,
    )
    payment_plan.refresh_from_db()
    assert payment_plan.exchange_rate == Decimal("0.10000000")
    payment = PaymentFactory(parent=payment_plan, entitlement_quantity=100)

    mock_get_exchange_rate.return_value = 1.25
    mock_get_quantity_in_usd.return_value = 125.0

    queue_and_run_retry_task(update_exchange_rate_on_release_payments_async_task, payment_plan=payment_plan)
    payment_plan.refresh_from_db()
    assert payment_plan.exchange_rate == 1.25

    payment.refresh_from_db()
    assert payment.entitlement_quantity_usd == 125.0

    mock_update_money_fields.assert_called_once()


@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
def test_update_exchange_rate_on_release_payments_exception_triggers_retry(
    mock_retry: Mock, mock_logger: Mock, payment_plan
) -> None:
    mock_retry.side_effect = Retry("retry")

    with patch.object(PaymentPlan, "get_exchange_rate", side_effect=Exception("test")):
        with pytest.raises(Retry):
            queue_and_run_retry_task(update_exchange_rate_on_release_payments_async_task, payment_plan=payment_plan)

    mock_logger.exception.assert_not_called()
    mock_retry.assert_called_once()


@patch("hope.models.Payment.objects.bulk_update")
@patch("hope.apps.payment.celery_tasks.get_quantity_in_usd", return_value=Decimal("125.00"))
@patch("hope.apps.payment.celery_tasks.get_object_or_404")
def test_update_exchange_rate_on_release_payments_action_bulk_updates_in_chunks(
    mock_get_object_or_404: Mock,
    mock_get_quantity_in_usd: Mock,
    mock_bulk_update: Mock,
) -> None:
    bulk_update_calls: list[tuple[int, list[str], int | None]] = []
    payments = [Mock(entitlement_quantity=Decimal("100.00")) for _ in range(1000)]
    payment_plan = Mock()
    payment_plan.business_area.name = "Test BA"
    payment_plan.currency = "PLN"
    payment_plan.exchange_rate = Decimal("1.25")
    payment_plan.currency_exchange_date = timezone.now().date()
    payment_plan.get_exchange_rate.return_value = Decimal("1.25")
    payment_plan.eligible_payments.only.return_value.iterator.return_value = payments
    payment_plan.program_cycle = Mock()
    mock_get_object_or_404.return_value = payment_plan
    mock_bulk_update.side_effect = lambda objs, fields, batch_size=None: bulk_update_calls.append(
        (len(objs), fields, batch_size)
    )

    update_exchange_rate_on_release_payments_async_task_action(Mock(config={"payment_plan_id": "payment-plan-id"}))

    mock_get_quantity_in_usd.assert_called()
    mock_bulk_update.assert_called_once()
    assert bulk_update_calls == [(1000, ["entitlement_quantity_usd"], 1000)]


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService")
def test_periodic_send_payment_plan_reconciliation_overdue_emails(
    mock_service_cls: Mock,
) -> None:
    queue_and_run_retry_task(periodic_send_payment_plan_reconciliation_overdue_emails_async_task)
    mock_service_cls.send_reconciliation_overdue_emails.assert_called_once()


@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.send_reconciliation_overdue_emails")
def test_periodic_send_payment_plan_reconciliation_overdue_emails_retries_on_exception(
    mock_send_reconciliation: Mock,
    mock_retry: Mock,
    mock_logger: Mock,
) -> None:
    error = Exception("test")
    mock_send_reconciliation.side_effect = error
    mock_retry.side_effect = Retry("retry")

    with pytest.raises(Retry):
        queue_and_run_retry_task(periodic_send_payment_plan_reconciliation_overdue_emails_async_task)

    mock_logger.exception.assert_not_called()
    mock_retry.assert_called_once_with(exc=error)


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService")
def test_send_payment_plan_reconciliation_overdue_email(mock_service_cls: Mock, payment_plan: PaymentPlan) -> None:
    mock_service = mock_service_cls.return_value
    queue_and_run_retry_task(send_payment_plan_reconciliation_overdue_email_async_task, payment_plan)
    mock_service.send_reconciliation_overdue_email_for_pp.assert_called_once()


@patch("hope.apps.payment.celery_tasks.logger")
def test_payment_plan_apply_engine_rule_failure_if_rule_commit_not_released(mock_logger: Mock) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        background_action_status=PaymentPlan.BackgroundActionStatus.RULE_ENGINE_RUN,
    )
    rule = RuleFactory(name="test_rule", type=Rule.TYPE_PAYMENT_PLAN)
    rule_commit = RuleCommitFactory(definition="result.value=Decimal('500')", rule=rule, is_release=False)

    assert rule_commit.is_release is False
    queue_and_run_retry_task(payment_plan_apply_engine_rule_async_task, payment_plan, rule)

    mock_logger.error.assert_called_once_with("PaymentPlan Run Engine Rule Error no RuleCommit")

    payment_plan.refresh_from_db(fields=["background_action_status"])
    assert payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.RULE_ENGINE_ERROR

    rule_commit.is_release = True
    rule_commit.save()
    rule_commit.refresh_from_db(fields=["is_release"])

    assert rule_commit.is_release is True
    queue_and_run_retry_task(payment_plan_apply_engine_rule_async_task, payment_plan, rule)

    payment_plan.refresh_from_db(fields=["background_action_status", "steficon_rule_id"])
    assert str(payment_plan.steficon_rule_id) == str(rule_commit.id)
    assert payment_plan.background_action_status is None


@patch("hope.apps.payment.celery_tasks.get_quantity_in_usd", return_value=Decimal("250.00"))
def test_payment_plan_apply_engine_rule_action_updates_payments_and_entitlement_date(
    mock_get_quantity_in_usd: Mock,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        background_action_status=PaymentPlan.BackgroundActionStatus.RULE_ENGINE_RUN,
        currency="PLN",
        exchange_rate=Decimal("2.00000000"),
    )
    payment = PaymentFactory(parent=payment_plan, entitlement_quantity=Decimal(0))
    rule = RuleFactory(name="test_rule", type=Rule.TYPE_PAYMENT_PLAN)
    rule_commit = RuleCommitFactory(definition="result.value=Decimal('500')", rule=rule, is_release=True)
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.payment.celery_tasks.payment_plan_apply_engine_rule_async_task_action",
        config={"payment_plan_id": str(payment_plan.pk), "engine_rule_id": str(rule.pk)},
    )

    payment_plan_apply_engine_rule_async_task_action(job)

    payment.refresh_from_db()
    payment_plan.refresh_from_db(fields=["background_action_status", "steficon_rule_id", "steficon_applied_date"])
    assert payment.entitlement_quantity == Decimal(500)
    assert payment.entitlement_quantity_usd == Decimal("250.00")
    assert payment.entitlement_date is not None
    assert payment_plan.steficon_applied_date is not None
    assert payment_plan.background_action_status is None
    assert str(payment_plan.steficon_rule_id) == str(rule_commit.id)
    mock_get_quantity_in_usd.assert_called_once()


@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.models.rule.RuleCommit.execute", side_effect=Exception("rule failure"))
def test_payment_plan_apply_engine_rule_action_sets_error_status_on_exception(
    mock_execute: Mock,
    mock_logger: Mock,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        background_action_status=PaymentPlan.BackgroundActionStatus.RULE_ENGINE_RUN,
    )
    PaymentFactory(parent=payment_plan)
    rule = RuleFactory(name="test_rule", type=Rule.TYPE_PAYMENT_PLAN)
    RuleCommitFactory(definition="result.value=Decimal('500')", rule=rule, is_release=True)
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.payment.celery_tasks.payment_plan_apply_engine_rule_async_task_action",
        config={"payment_plan_id": str(payment_plan.pk), "engine_rule_id": str(rule.pk)},
    )

    with pytest.raises(Exception, match="rule failure"):
        payment_plan_apply_engine_rule_async_task_action(job)

    payment_plan.refresh_from_db(fields=["background_action_status"])
    assert payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.RULE_ENGINE_ERROR
    mock_execute.assert_called_once()
    mock_logger.exception.assert_called_once_with("PaymentPlan Run Engine Rule Error")


@patch("hope.apps.payment.xlsx.xlsx_payment_plan_import_service.XlsxPaymentPlanImportService")
@patch("hope.models.payment_plan.PaymentPlan.update_money_fields")
@patch("hope.models.payment_plan.PaymentPlan.remove_export_files")
def test_import_payment_plan_payment_list_from_xlsx(
    mock_remove_export_files: Mock,
    mock_update_money_fields: Mock,
    mock_service_cls: Mock,
    user,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS,
    )
    file_temp = FileTempFactory(
        object_id=payment_plan.pk,
        content_type=get_content_type_for_model(payment_plan),
        created_by=user,
    )
    payment_plan.imported_file = file_temp
    payment_plan.save(update_fields=["imported_file"])
    payment_plan.refresh_from_db()

    mock_service = mock_service_cls.return_value
    queue_and_run_retry_task(import_payment_plan_payment_list_from_xlsx_async_task, payment_plan)

    payment_plan.refresh_from_db(fields=["background_action_status", "imported_file_date"])
    assert payment_plan.background_action_status is None
    assert payment_plan.imported_file_date is not None
    mock_service_cls.assert_called_once()
    assert mock_service_cls.call_args[0][0].id == payment_plan.id
    assert mock_service_cls.call_args[0][1].name == payment_plan.imported_file.file.name
    mock_service.open_workbook.assert_called_once()
    mock_service.import_payment_list.assert_called_once()
    mock_remove_export_files.assert_called_once()
    mock_update_money_fields.assert_called_once()


@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
@patch("hope.apps.payment.xlsx.xlsx_payment_plan_import_service.XlsxPaymentPlanImportService")
def test_import_payment_plan_payment_list_from_xlsx_missing_file_error(
    mock_service_cls: Mock,
    mock_retry: Mock,
    mock_logger: Mock,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS,
    )
    mock_retry.side_effect = Retry("retry")

    with pytest.raises(Retry):
        queue_and_run_retry_task(import_payment_plan_payment_list_from_xlsx_async_task, payment_plan)

    mock_service_cls.assert_not_called()
    mock_logger.exception.assert_not_called()
    mock_retry.assert_called_once()
    error = mock_retry.call_args.kwargs.get("exc")
    assert error is not None
    assert str(error).startswith("Error import from xlsx, file does not exist for Payment Plan ID")


@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
@patch("hope.apps.payment.xlsx.xlsx_payment_plan_import_service.XlsxPaymentPlanImportService")
def test_import_payment_plan_payment_list_from_xlsx_import_error_retries(
    mock_service_cls: Mock,
    mock_retry: Mock,
    mock_logger: Mock,
    user,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS,
    )
    file_temp = FileTempFactory(
        object_id=payment_plan.pk,
        content_type=get_content_type_for_model(payment_plan),
        created_by=user,
    )
    payment_plan.imported_file = file_temp
    payment_plan.save(update_fields=["imported_file"])

    mock_service = mock_service_cls.return_value
    mock_service.import_payment_list.side_effect = Exception("test")
    mock_retry.side_effect = Retry("retry")

    with pytest.raises(Retry):
        queue_and_run_retry_task(import_payment_plan_payment_list_from_xlsx_async_task, payment_plan)

    payment_plan.refresh_from_db(fields=["background_action_status"])
    assert payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.XLSX_IMPORT_ERROR
    mock_service.open_workbook.assert_called_once()
    mock_logger.exception.assert_called_once_with("PaymentPlan Error import from xlsx")
    mock_retry.assert_called_once()


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService")
@patch("hope.apps.payment.celery_tasks.XlsxPaymentPlanImportPerFspService")
@patch("hope.models.payment_plan.PaymentPlan.update_money_fields")
@patch("hope.models.payment_plan.PaymentPlan.remove_export_files")
def test_import_payment_plan_payment_list_per_fsp_from_xlsx(
    mock_remove_export_files: Mock,
    mock_update_money_fields: Mock,
    mock_service_cls: Mock,
    mock_payment_plan_service_cls: Mock,
    user,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
    )
    file_temp = FileTempFactory(
        object_id=payment_plan.pk,
        content_type=get_content_type_for_model(payment_plan),
        created_by=user,
    )
    payment_plan.reconciliation_import_file = file_temp
    payment_plan.save(update_fields=["reconciliation_import_file"])

    mock_service = mock_service_cls.return_value
    with (
        patch.object(PaymentPlan, "is_reconciled", new_callable=PropertyMock) as mock_is_reconciled,
        patch("hope.models.program_cycle.ProgramCycle.save") as mock_program_cycle_save,
    ):
        mock_is_reconciled.return_value = True
        queue_and_run_retry_task(import_payment_plan_payment_list_per_fsp_from_xlsx_async_task, payment_plan)

    payment_plan.refresh_from_db(fields=["background_action_status", "status"])
    assert payment_plan.background_action_status is None
    assert payment_plan.status == PaymentPlan.Status.FINISHED
    mock_service_cls.assert_called_once_with(payment_plan, file_temp.file)
    mock_service.open_workbook.assert_called_once()
    mock_service.import_payment_list.assert_called_once()
    mock_remove_export_files.assert_called_once()
    mock_update_money_fields.assert_called_once()
    mock_program_cycle_save.assert_called_once()
    mock_payment_plan_service_cls.return_value.recalculate_signatures_in_batch.assert_called_once()


@patch("hope.apps.payment.celery_tasks.XlsxPaymentPlanImportPerFspService")
def test_import_payment_plan_payment_list_per_fsp_from_xlsx_no_finish_when_not_reconciled(
    mock_service_cls: Mock,
    user,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
    )
    file_temp = FileTempFactory(
        object_id=payment_plan.pk,
        content_type=get_content_type_for_model(payment_plan),
        created_by=user,
    )
    payment_plan.reconciliation_import_file = file_temp
    payment_plan.save(update_fields=["reconciliation_import_file"])

    with patch.object(PaymentPlan, "is_reconciled", new_callable=PropertyMock) as mock_is_reconciled:
        mock_is_reconciled.return_value = False
        queue_and_run_retry_task(import_payment_plan_payment_list_per_fsp_from_xlsx_async_task, payment_plan)

    payment_plan.refresh_from_db(fields=["status"])
    assert payment_plan.status == PaymentPlan.Status.ACCEPTED
    mock_service_cls.return_value.import_payment_list.assert_called_once()


@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
@patch("hope.apps.payment.celery_tasks.XlsxPaymentPlanImportPerFspService")
def test_import_payment_plan_payment_list_per_fsp_from_xlsx_retries_on_exception(
    mock_service_cls: Mock,
    mock_retry: Mock,
    mock_logger: Mock,
    user,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
    )
    file_temp = FileTempFactory(
        object_id=payment_plan.pk,
        content_type=get_content_type_for_model(payment_plan),
        created_by=user,
    )
    payment_plan.reconciliation_import_file = file_temp
    payment_plan.save(update_fields=["reconciliation_import_file"])

    mock_service = mock_service_cls.return_value
    mock_service.import_payment_list.side_effect = Exception("test")
    mock_retry.side_effect = Retry("retry")

    with pytest.raises(Retry):
        queue_and_run_retry_task(import_payment_plan_payment_list_per_fsp_from_xlsx_async_task, payment_plan)

    payment_plan.refresh_from_db(fields=["background_action_status"])
    assert payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.XLSX_IMPORT_ERROR
    mock_logger.exception.assert_called_once_with("Unexpected error during xlsx per fsp import")
    mock_retry.assert_called_once()


def test_payment_plan_apply_steficon_hh_selection() -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_STEFICON_WAIT,
        steficon_rule_targeting=RuleCommitFactory(version=33, is_release=True),
    )
    payment = PaymentFactory(parent=payment_plan)
    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.TP_STEFICON_WAIT

    engine_rule = RuleFactory(name="Rule-test", type=Rule.TYPE_TARGETING)
    RuleCommitFactory(
        definition="result.value=Decimal('500.33333333')",
        rule=engine_rule,
        version=11,
        is_release=True,
    )

    queue_and_run_retry_task(payment_plan_apply_steficon_hh_selection_async_task, payment_plan, str(engine_rule.id))

    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.TP_STEFICON_COMPLETED

    payment.refresh_from_db(fields=["vulnerability_score"])
    assert payment.vulnerability_score == Decimal("500.333")


@patch("hope.models.Payment.objects.bulk_update")
@patch("hope.apps.payment.celery_tasks.normalize_score", return_value=Decimal("500.333"))
@patch("hope.apps.payment.celery_tasks.get_object_or_404")
def test_payment_plan_apply_steficon_hh_selection_action_bulk_updates_in_chunks(
    mock_get_object_or_404: Mock,
    mock_normalize_score: Mock,
    mock_bulk_update: Mock,
) -> None:
    bulk_update_calls: list[tuple[int, list[str], int | None]] = []
    payments = [Mock(household=Mock()) for _ in range(1000)]
    payment_plan = Mock()
    payment_plan.business_area.name = "Test BA"
    payment_plan.payment_items.select_related.return_value.iterator.return_value = payments
    payment_plan.vulnerability_score_min = None
    payment_plan.vulnerability_score_max = None
    payment_plan.steficon_rule_targeting_id = 1
    rule = Mock(id=1)
    rule.execute.return_value = Mock(value=Decimal("500.333333"))
    engine_rule = Mock(latest=rule)
    mock_get_object_or_404.side_effect = [payment_plan, engine_rule]
    mock_bulk_update.side_effect = lambda objs, fields, batch_size=None: bulk_update_calls.append(
        (len(objs), fields, batch_size)
    )

    payment_plan_apply_steficon_hh_selection_async_task_action(
        Mock(config={"payment_plan_id": "payment-plan-id", "engine_rule_id": "engine-rule-id"})
    )

    mock_normalize_score.assert_called()
    mock_bulk_update.assert_called_once()
    assert bulk_update_calls == [(1000, ["vulnerability_score"], 1000)]


@patch("hope.models.rule.RuleCommit.execute")
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
def test_payment_plan_apply_steficon_hh_selection_exception_handling(mock_retry: Mock, mock_rule_execute: Mock) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_STEFICON_WAIT,
    )
    PaymentFactory(parent=payment_plan)
    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.TP_STEFICON_WAIT
    engine_rule = RuleFactory(name="Rule-test123", type=Rule.TYPE_TARGETING)
    RuleCommitFactory(definition="result.value=Decimal('123')", rule=engine_rule, version=2, is_release=True)

    mock_rule_execute.side_effect = Exception("test")
    mock_retry.side_effect = Retry("retry")
    with pytest.raises(Retry):
        queue_and_run_retry_task(payment_plan_apply_steficon_hh_selection_async_task, payment_plan, str(engine_rule.id))

    mock_retry.assert_called_once()
    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.TP_STEFICON_ERROR


@patch("hope.apps.payment.celery_tasks.logger")
def test_payment_plan_apply_steficon_hh_selection_failure_if_rule_commit_not_released(mock_logger: Mock) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        background_action_status=PaymentPlan.BackgroundActionStatus.RULE_ENGINE_RUN,
    )
    rule = RuleFactory(name="test_rule", type=Rule.TYPE_PAYMENT_PLAN)
    rule_commit = RuleCommitFactory(definition="result.value=Decimal('1')", rule=rule, is_release=False)

    assert rule_commit.is_release is False
    queue_and_run_retry_task(payment_plan_apply_steficon_hh_selection_async_task, payment_plan, str(rule.id))

    mock_logger.error.assert_called_once_with("PaymentPlan Run Engine Rule Error no RuleCommit")

    payment_plan.refresh_from_db(fields=["background_action_status"])
    assert payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.RULE_ENGINE_ERROR


def test_remove_old_cash_plan_payment_verification_xlsx() -> None:
    filename = "Test_File_ABC.xlsx"
    file_content = b"Test abc"
    with NamedTemporaryFile(delete=False) as file_temp:
        file_temp.write(file_content)
        file_temp.flush()
    pp = PaymentPlanFactory(status=PaymentPlan.Status.FINISHED)
    payment_verification_plan = PaymentVerificationPlanFactory(payment_plan=pp)
    creation_time = timezone.now() - datetime.timedelta(days=99)
    FileTempFactory(
        object_id=payment_verification_plan.pk,
        content_type=get_content_type_for_model(payment_verification_plan),
        created=creation_time,
        file=ContentFile(file_content, filename),
    )
    assert FileTemp.objects.all().count() == 1

    queue_and_run_retry_task(remove_old_cash_plan_payment_verification_xlsx_async_task)

    assert FileTemp.objects.all().count() == 0


@patch("hope.apps.payment.celery_tasks.logger")
def test_remove_old_cash_plan_payment_verification_xlsx_action_returns_when_no_old_files(mock_logger: Mock) -> None:
    remove_old_cash_plan_payment_verification_xlsx_async_task_action(Mock(config={"past_days": 30}))

    mock_logger.info.assert_not_called()


def test_remove_old_payment_plan_payment_list_xlsx(payment_plan) -> None:
    filename = "Test_File_ABC1.xlsx"
    file_content = b"Test abc1"
    with NamedTemporaryFile(delete=False) as file_temp:
        file_temp.write(file_content)
        file_temp.flush()
    creation_time = timezone.now() - datetime.timedelta(days=99)
    FileTempFactory(
        object_id=payment_plan.pk,
        content_type=get_content_type_for_model(payment_plan),
        created=creation_time,
        file=ContentFile(file_content, filename),
    )
    assert FileTemp.objects.all().count() == 1

    queue_and_run_retry_task(remove_old_payment_plan_payment_list_xlsx_async_task)

    assert FileTemp.objects.all().count() == 0


@patch("hope.apps.payment.services.qcf_reports_service.QCFReportsService")
def test_periodic_sync_payment_plan_invoices_western_union_ftp_runs_service_process_files_since(
    mock_service_cls: Mock,
) -> None:
    mock_service = mock_service_cls.return_value
    queue_and_run_retry_task(periodic_sync_payment_plan_invoices_western_union_ftp_async_task)
    mock_service.process_files_since.assert_called_once()


@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
@patch("hope.apps.payment.services.qcf_reports_service.QCFReportsService")
def test_periodic_sync_payment_plan_invoices_western_union_ftp_retries_on_exception(
    mock_service_cls: Mock,
    mock_retry: Mock,
) -> None:
    mock_service = mock_service_cls.return_value
    mock_service.process_files_since.side_effect = Exception("test")
    mock_retry.side_effect = Retry("retry")
    with pytest.raises(Retry):
        queue_and_run_retry_task(periodic_sync_payment_plan_invoices_western_union_ftp_async_task)
    mock_retry.assert_called_once()


@pytest.mark.parametrize(
    "should_send",
    [True, False],
)
@patch("hope.apps.payment.services.qcf_reports_service.QCFReportsService")
def test_send_qcf_report_email_notifications(
    mock_service_cls: Mock,
    qcf_report,
    should_send: bool,
) -> None:
    FlagState.objects.get_or_create(
        name="WU_PAYMENT_PLAN_INVOICES_NOTIFICATIONS_ENABLED",
        condition="boolean",
        value=str(should_send),
        required=False,
    )

    mock_service = mock_service_cls.return_value
    queue_and_run_retry_task(send_qcf_report_email_notifications_async_task, qcf_report_id=str(qcf_report.id))
    assert bool(mock_service.send_notification_emails.call_count) == should_send
    qcf_report.refresh_from_db()
    assert qcf_report.sent is should_send


@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
@patch("hope.apps.payment.services.qcf_reports_service.QCFReportsService")
def test_send_qcf_report_email_notifications_retries_on_exception(
    mock_service_cls: Mock,
    mock_retry: Mock,
    qcf_report,
) -> None:
    FlagState.objects.get_or_create(
        name="WU_PAYMENT_PLAN_INVOICES_NOTIFICATIONS_ENABLED",
        condition="boolean",
        value="True",
        required=False,
    )
    mock_service = mock_service_cls.return_value
    mock_service.send_notification_emails.side_effect = Exception("test")

    mock_retry.side_effect = Retry("retry")
    with pytest.raises(Retry):
        queue_and_run_retry_task(send_qcf_report_email_notifications_async_task, qcf_report_id=str(qcf_report.id))
    mock_retry.assert_called_once()


@patch("hope.apps.payment.celery_tasks.send_email_notification_on_commit")
@patch("hope.apps.payment.celery_tasks.PaymentPlanPDFExportService.generate_pdf_summary")
def test_export_pdf_payment_plan_summary_action_replaces_existing_file_and_sends_email(
    mock_generate_pdf_summary: Mock,
    mock_send_email: Mock,
    payment_plan: PaymentPlan,
    user,
) -> None:
    old_file = FileTempFactory(
        object_id=payment_plan.pk,
        content_type=get_content_type_for_model(payment_plan),
        created_by=user,
    )
    payment_plan.export_pdf_file_summary = old_file
    payment_plan.business_area.enable_email_notification = True
    payment_plan.business_area.save(update_fields=["enable_email_notification"])
    payment_plan.save(update_fields=["export_pdf_file_summary"])
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.payment.celery_tasks.export_pdf_payment_plan_summary_async_task_action",
        config={"payment_plan_id": str(payment_plan.pk), "user_id": str(user.pk)},
    )
    mock_generate_pdf_summary.return_value = (b"%PDF-1.4 test", "summary.pdf")

    export_pdf_payment_plan_summary_async_task_action(job)

    payment_plan.refresh_from_db(fields=["export_pdf_file_summary"])
    assert payment_plan.export_pdf_file_summary_id is not None
    assert payment_plan.export_pdf_file_summary_id != old_file.pk
    assert FileTemp.objects.filter(pk=old_file.pk).exists() is False
    assert FileTemp.objects.filter(pk=payment_plan.export_pdf_file_summary_id).exists() is True
    mock_send_email.assert_called_once()


def test_export_pdf_payment_plan_summary_queues_retry_job() -> None:
    payment_plan = PaymentPlanFactory()
    user = UserFactory()

    with patch("hope.apps.payment.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        export_pdf_payment_plan_summary_async_task(payment_plan, str(user.pk))

    job = AsyncRetryJob.objects.latest("pk")
    assert job.type == AsyncJobModel.JobType.JOB_TASK
    assert job.action == "hope.apps.payment.celery_tasks.export_pdf_payment_plan_summary_async_task_action"
    assert job.program == payment_plan.program
    assert job.content_object == payment_plan
    assert job.config == {"payment_plan_id": str(payment_plan.pk), "user_id": str(user.pk)}
    assert job.group_key == f"export_pdf_payment_plan_summary_async_task:{payment_plan.pk}:{user.pk}"
    assert job.description == f"Export payment plan summary pdf for {payment_plan.pk}"
    mock_queue.assert_called_once()


@patch("hope.models.payment_plan.PaymentPlan.update_money_fields")
@patch("hope.models.payment_plan.PaymentPlan.remove_export_files")
def test_payment_plan_set_entitlement_flat_amount_task(
    mock_remove_export_files: Mock,
    mock_update_money_fields: Mock,
    user,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        background_action_status=PaymentPlan.BackgroundActionStatus.IMPORTING_ENTITLEMENTS,
        flat_amount_value=1.22,
        exchange_rate=2.00,
    )
    payment_plan.refresh_from_db()
    payment_1 = PaymentFactory(
        parent=payment_plan,
        status=Payment.STATUS_PENDING,
        currency="PLN",
        entitlement_quantity_usd=None,
        entitlement_date=None,
    )

    queue_and_run_retry_task(payment_plan_set_entitlement_flat_amount_async_task, payment_plan)

    payment_plan.refresh_from_db(fields=["background_action_status", "flat_amount_value"])
    payment_1.refresh_from_db()
    assert payment_plan.background_action_status is None

    mock_remove_export_files.assert_called_once()
    mock_update_money_fields.assert_called_once()
    assert payment_1.entitlement_quantity == Decimal("1.22")
    assert payment_1.entitlement_quantity_usd is not None
    assert payment_1.entitlement_date is not None


@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
@patch("hope.apps.payment.celery_tasks.get_quantity_in_usd")
def test_payment_plan_set_entitlement_flat_amount_error_get_quantity_in_usd(
    mock_payment_plan_get_quantity_in_usd: Mock,
    mock_retry: Mock,
    mock_logger: Mock,
    user,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        background_action_status=PaymentPlan.BackgroundActionStatus.IMPORTING_ENTITLEMENTS,
        flat_amount_value=1.12,
        exchange_rate=1.0,
    )
    mock_retry.side_effect = Retry("retry")
    mock_payment_plan_get_quantity_in_usd.side_effect = Exception("exchange error")

    with pytest.raises(Retry):
        queue_and_run_retry_task(payment_plan_set_entitlement_flat_amount_async_task, payment_plan)

    payment_plan.refresh_from_db(fields=["background_action_status"])
    assert payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.XLSX_IMPORT_ERROR

    mock_logger.exception.assert_called_once_with("PaymentPlan Error set entitlement flat amount")


@patch("hope.models.payment_plan.PaymentPlan.update_money_fields")
def test_payment_plan_apply_custom_exchange_rate_task(
    mock_update_money_fields: Mock,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        currency="PLN",
        exchange_rate=Decimal("2.00"),
        custom_exchange_rate=True,
    )
    payment_1 = PaymentFactory(
        parent=payment_plan,
        status=Payment.STATUS_PENDING,
        currency="PLN",
        entitlement_quantity=Decimal("100.00"),
        delivered_quantity=Decimal("40.00"),
        entitlement_quantity_usd=Decimal("1.00"),
        delivered_quantity_usd=Decimal("1.00"),
    )

    queue_and_run_retry_task(payment_plan_apply_custom_exchange_rate_async_task, payment_plan)

    payment_plan.refresh_from_db(fields=["exchange_rate"])
    payment_1.refresh_from_db()
    assert payment_plan.exchange_rate == Decimal("2.00")
    assert payment_1.entitlement_quantity_usd == Decimal("50.00")
    assert payment_1.delivered_quantity_usd == Decimal("20.00")
    mock_update_money_fields.assert_called_once()


@patch("hope.apps.payment.celery_tasks.PaymentPlanFlow")
@patch("hope.models.Payment.objects.bulk_update")
@patch("hope.apps.payment.celery_tasks.get_quantity_in_usd", return_value=Decimal("10.00"))
@patch("hope.apps.payment.celery_tasks.get_object_or_404")
def test_payment_plan_apply_custom_exchange_rate_action_bulk_updates_in_chunks(
    mock_get_object_or_404: Mock,
    mock_get_quantity_in_usd: Mock,
    mock_bulk_update: Mock,
    mock_flow_cls: Mock,
) -> None:
    bulk_update_calls: list[tuple[int, list[str], int | None]] = []
    payments = [Mock(entitlement_quantity=Decimal("100.00"), delivered_quantity=Decimal("40.00")) for _ in range(1000)]
    payment_plan = Mock()
    payment_plan.business_area.name = "Test BA"
    payment_plan.currency = "PLN"
    payment_plan.exchange_rate = Decimal("2.00")
    payment_plan.currency_exchange_date = timezone.now().date()
    payment_plan.eligible_payments.only.return_value.iterator.return_value = payments
    payment_plan.program_cycle = Mock()
    mock_get_object_or_404.return_value = payment_plan
    mock_bulk_update.side_effect = lambda objs, fields, batch_size=None: bulk_update_calls.append(
        (len(objs), fields, batch_size)
    )

    payment_plan_apply_custom_exchange_rate_async_task_action(Mock(config={"payment_plan_id": "payment-plan-id"}))

    mock_get_quantity_in_usd.assert_called()
    mock_bulk_update.assert_called_once()
    assert bulk_update_calls == [(1000, ["entitlement_quantity_usd", "delivered_quantity_usd"], 1000)]
    mock_flow_cls.return_value.background_action_status_none.assert_called_once()


@patch("hope.models.payment_plan.PaymentPlan.get_unore_exchange_rate")
@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
@patch("hope.apps.payment.celery_tasks.get_quantity_in_usd")
def test_payment_plan_apply_custom_exchange_rate_retry_on_error(
    mock_get_quantity_in_usd: Mock,
    mock_retry: Mock,
    mock_logger: Mock,
    mock_get_unore_exchange_rate: Mock,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.IN_REVIEW,
        currency="PLN",
        background_action_status=PaymentPlan.BackgroundActionStatus.APPLYING_CUSTOM_EXCHANGE_RATE,
        custom_exchange_rate=True,
    )
    PaymentFactory(parent=payment_plan, status=Payment.STATUS_PENDING, currency="PLN")
    mock_retry.side_effect = Retry("retry")
    mock_get_quantity_in_usd.side_effect = Exception("exchange error")

    with pytest.raises(Retry):
        queue_and_run_retry_task(payment_plan_apply_custom_exchange_rate_async_task, payment_plan)

    payment_plan.refresh_from_db(fields=["background_action_status"])
    assert (
        payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.APPLYING_CUSTOM_EXCHANGE_RATE_ERROR
    )
    mock_get_unore_exchange_rate.assert_not_called()
    mock_logger.exception.assert_called_once_with("PaymentPlan Apply Custom Exchange Rate Error")
    mock_retry.assert_called_once()


@patch("hope.models.payment_plan.PaymentPlan.get_unore_exchange_rate")
@patch("hope.apps.payment.celery_tasks.get_quantity_in_usd")
@patch("hope.models.payment_plan.PaymentPlan.update_money_fields")
def test_update_exchange_rate_on_release_payments_uses_custom_exchange_rate(
    mock_update_money_fields: Mock,
    mock_get_quantity_in_usd: Mock,
    mock_get_unore_exchange_rate: Mock,
) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        currency="PLN",
        exchange_rate=Decimal("1.25000000"),
        custom_exchange_rate=True,
    )
    payment = PaymentFactory(parent=payment_plan, entitlement_quantity=100)
    mock_get_quantity_in_usd.return_value = 80.0

    queue_and_run_retry_task(update_exchange_rate_on_release_payments_async_task, payment_plan=payment_plan)

    payment_plan.refresh_from_db(fields=["exchange_rate"])
    payment.refresh_from_db()
    assert payment_plan.exchange_rate == Decimal("1.25000000")
    assert payment.entitlement_quantity_usd == 80.0
    mock_get_unore_exchange_rate.assert_not_called()
    mock_update_money_fields.assert_called_once()


def test_prepare_payment_plan_task_queues_payment_retry_job() -> None:
    payment_plan = PaymentPlanFactory()
    prepare_payment_plan_async_task(payment_plan)

    job = AsyncRetryJob.objects.latest("pk")
    assert job.type == AsyncJobModel.JobType.JOB_TASK
    assert job.program == payment_plan.program
    assert job.content_object == payment_plan
    assert job.action == "hope.apps.payment.celery_tasks.prepare_payment_plan_async_task_action"
    assert job.config == {"payment_plan_id": str(payment_plan.pk)}
    assert job.group_key == f"prepare_payment_plan_async_task:{payment_plan.pk}"
    assert job.description == f"Prepare payment plan {payment_plan.pk}"


def test_send_to_payment_gateway_queues_async_job() -> None:
    payment_plan = PaymentPlanFactory()
    user = UserFactory()

    send_to_payment_gateway_async_task(payment_plan, str(user.pk))

    job = AsyncJob.objects.latest("pk")
    assert job.type == AsyncJobModel.JobType.JOB_TASK
    assert job.program == payment_plan.program
    assert job.content_object == payment_plan
    assert job.action == "hope.apps.payment.celery_tasks.send_to_payment_gateway_async_task_action"
    assert job.config == {"payment_plan_id": str(payment_plan.pk), "user_id": str(user.pk)}
    assert job.group_key == f"send_to_payment_gateway_async_task:{payment_plan.pk}:{user.pk}"
    assert job.description == f"Send payment plan {payment_plan.pk} to payment gateway"


def test_create_payment_verification_plan_xlsx_queues_retry_job() -> None:
    payment_verification_plan = PaymentVerificationPlanFactory()
    user = UserFactory()

    with patch("hope.apps.payment.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        create_payment_verification_plan_xlsx_async_task(payment_verification_plan, str(user.pk))

    job = AsyncRetryJob.objects.latest("pk")
    assert job.type == AsyncJobModel.JobType.JOB_TASK
    assert job.program == payment_verification_plan.get_program
    assert job.action == "hope.apps.payment.celery_tasks.create_payment_verification_plan_xlsx_async_task_action"
    assert job.config == {"payment_verification_plan_id": str(payment_verification_plan.pk), "user_id": str(user.pk)}
    assert job.group_key == f"create_payment_verification_plan_xlsx_async_task:{payment_verification_plan.pk}:{user.pk}"
    assert job.description == f"Create payment verification plan xlsx for {payment_verification_plan.pk}"
    mock_queue.assert_called_once()


@patch("hope.apps.payment.services.payment_gateway.PaymentGatewayService")
def test_periodic_sync_payment_gateway_records_action_runs_service(mock_service_cls: Mock) -> None:
    periodic_sync_payment_gateway_records_async_task_action()

    mock_service_cls.return_value.sync_records.assert_called_once()


def test_periodic_sync_payment_gateway_records_queues_retry_job() -> None:
    with patch("hope.apps.payment.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        periodic_sync_payment_gateway_records_async_task()

    job = AsyncRetryJob.objects.latest("pk")
    assert job.type == AsyncJobModel.JobType.JOB_TASK
    assert job.action == "hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_records_async_task_action"
    assert job.config == {}
    assert job.group_key == "periodic_sync_payment_gateway_records_async_task"
    assert job.description == "Periodic sync payment gateway records"
    mock_queue.assert_called_once()


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.send_reconciliation_overdue_emails")
def test_payment_async_job_task_clears_stale_job_errors_on_success(
    mock_send_reconciliation_overdue_emails: Mock,
) -> None:
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.payment.celery_tasks.periodic_send_payment_plan_reconciliation_overdue_emails_async_task_action",
        config={},
        errors={"exception": "stale failure", "start_flow_error": "keep me"},
    )

    async_retry_job_task.run(job.pk, job.version)

    job.refresh_from_db()
    assert job.errors == {"start_flow_error": "keep me"}
    mock_send_reconciliation_overdue_emails.assert_called_once()


@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.send_reconciliation_overdue_emails")
def test_async_retry_job_task_sets_job_errors_before_retry(
    mock_send_reconciliation_overdue_emails: Mock,
    mock_retry: Mock,
) -> None:
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.payment.celery_tasks.periodic_send_payment_plan_reconciliation_overdue_emails_async_task_action",
        config={},
    )
    mock_send_reconciliation_overdue_emails.side_effect = Exception("sync failed")
    mock_retry.side_effect = Retry("retry")

    with pytest.raises(Retry):
        async_retry_job_task.run(job.pk, job.version)

    job.refresh_from_db()
    assert job.errors == {"exception": "sync failed"}
    mock_retry.assert_called_once()


@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.send_reconciliation_overdue_emails")
def test_async_retry_job_task_preserves_partial_errors_on_failure(
    mock_send_reconciliation_overdue_emails: Mock,
    mock_retry: Mock,
) -> None:
    job = AsyncRetryJob.objects.create(
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.payment.celery_tasks.periodic_send_payment_plan_reconciliation_overdue_emails_async_task_action",
        config={},
        errors={"start_flow_error": "keep me"},
    )
    mock_send_reconciliation_overdue_emails.side_effect = Exception("sync failed")
    mock_retry.side_effect = Retry("retry")

    with pytest.raises(Retry):
        async_retry_job_task.run(job.pk, job.version)

    job.refresh_from_db()
    assert job.errors == {"start_flow_error": "keep me", "exception": "sync failed"}
    mock_retry.assert_called_once()
