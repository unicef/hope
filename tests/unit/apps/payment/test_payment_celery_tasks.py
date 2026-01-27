import datetime
from decimal import Decimal
from tempfile import NamedTemporaryFile
from unittest.mock import Mock, PropertyMock, call, patch

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
from hope.apps.payment.celery_tasks import (
    create_payment_plan_payment_list_xlsx_per_fsp,
    import_payment_plan_payment_list_from_xlsx,
    import_payment_plan_payment_list_per_fsp_from_xlsx,
    payment_plan_apply_engine_rule,
    payment_plan_apply_steficon_hh_selection,
    payment_plan_full_rebuild,
    payment_plan_rebuild_stats,
    periodic_send_payment_plan_reconciliation_overdue_emails,
    periodic_sync_payment_plan_invoices_western_union_ftp,
    prepare_payment_plan_task,
    remove_old_cash_plan_payment_verification_xlsx,
    remove_old_payment_plan_payment_list_xlsx,
    send_payment_plan_payment_list_xlsx_per_fsp_password,
    send_payment_plan_reconciliation_overdue_email,
    send_qcf_report_email_notifications,
    update_exchange_rate_on_release_payments,
)
from hope.apps.payment.utils import generate_cache_key
from hope.models import (
    FileTemp,
    PaymentPlan,
    Rule,
)

pytestmark = pytest.mark.django_db


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


@patch("hope.apps.payment.celery_tasks.logger")
def test_prepare_payment_plan_task_wrong_pp_status(mock_logger: Mock) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
    )
    payment_plan.refresh_from_db()
    result = prepare_payment_plan_task(str(payment_plan.pk))

    assert result is False
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
            "task_name": "prepare_payment_plan_task",
            "payment_plan_id": str(payment_plan.id),
        }
    )
    cache.set(cache_key, True, timeout=300)
    result = prepare_payment_plan_task(pp_id_str)

    assert result is False
    mock_logger.info.assert_called_with(
        f"Task prepare_payment_plan_task with payment_plan_id {pp_id_str} already running."
    )


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.create_payments")
@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.apps.payment.celery_tasks.prepare_payment_plan_task.retry")
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
        prepare_payment_plan_task(payment_plan_id=str(payment_plan.pk))

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
    pp_id_str = str(payment_plan.pk)

    payment_plan_rebuild_stats(pp_id_str)

    payment_plan.refresh_from_db(fields=["build_status", "built_at"])
    assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK
    assert payment_plan.built_at is not None
    mock_update_population_count_fields.assert_called_once()
    mock_update_money_fields.assert_called_once()


@patch("hope.models.payment_plan.PaymentPlan.update_population_count_fields")
@patch("hope.apps.payment.celery_tasks.payment_plan_rebuild_stats.retry")
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
        payment_plan_rebuild_stats(str(payment_plan.pk))

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
    payment_plan_full_rebuild(str(payment_plan.pk))

    payment_plan.refresh_from_db(fields=["build_status", "built_at"])
    assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK
    assert payment_plan.built_at is not None
    mock_full_rebuild.assert_called_once()


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.full_rebuild")
@patch("hope.apps.payment.celery_tasks.payment_plan_full_rebuild.retry")
def test_payment_plan_full_rebuild_retry_exception_handling(mock_retry: Mock, mock_full_rebuild: Mock) -> None:
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        build_status=PaymentPlan.BuildStatus.BUILD_STATUS_OK,
    )
    PaymentFactory(parent=payment_plan)
    mock_full_rebuild.side_effect = Exception("test")
    mock_retry.side_effect = Retry("retry")
    with pytest.raises(Retry):
        payment_plan_full_rebuild(str(payment_plan.pk))

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

        create_payment_plan_payment_list_xlsx_per_fsp(str(payment_plan.pk), str(user.pk), str(fsp_template.pk))

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

        create_payment_plan_payment_list_xlsx_per_fsp(str(payment_plan.pk), str(user.pk), str(fsp_template.pk))
        payment_plan.refresh_from_db()
        file_obj = FileTemp.objects.get(object_id=payment_plan.id)

        assert payment_plan.background_action_status is None
        assert payment_plan.export_file_per_fsp == file_obj
        assert isinstance(file_obj.password, str)
        assert isinstance(file_obj.xlsx_password, str)
        assert len(file_obj.xlsx_password) == 12
        assert len(file_obj.password) == 12

        send_payment_plan_payment_list_xlsx_per_fsp_password(str(payment_plan.pk), str(user.pk))

        assert mock_mailjet_send.call_count == 3

    from hope.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import (
        XlsxPaymentPlanExportPerFspService,
    )

    assert XlsxPaymentPlanExportPerFspService._as_plain_text(memoryview(b"zip-pass")) == "zip-pass"
    assert XlsxPaymentPlanExportPerFspService._as_plain_text(b"xlsx-pass") == "xlsx-pass"


@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.models.User")
def test_send_payment_plan_payment_list_xlsx_per_fsp_password_failure(
    mock_get_user_model: Mock, mock_logger: Mock
) -> None:
    mock_get_user_model.objects.get.side_effect = Exception("User not found")
    with pytest.raises(Exception, match="User not found"):
        send_payment_plan_payment_list_xlsx_per_fsp_password("pp_id_123", "invalid-user-id-123")

    mock_logger.exception.assert_called_once_with("Send Payment Plan List XLSX Per FSP Password Error")


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

    update_exchange_rate_on_release_payments(payment_plan_id=str(payment_plan.pk))
    payment_plan.refresh_from_db()
    assert payment_plan.exchange_rate == 1.25

    payment.refresh_from_db()
    assert payment.entitlement_quantity_usd == 125.0

    mock_update_money_fields.assert_called_once()


@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.apps.payment.celery_tasks.update_exchange_rate_on_release_payments.retry")
def test_update_exchange_rate_on_release_payments_exception_triggers_retry(
    mock_retry: Mock, mock_logger: Mock, payment_plan
) -> None:
    mock_retry.side_effect = Retry("retry")

    with patch.object(PaymentPlan, "get_exchange_rate", side_effect=Exception("test")):
        with pytest.raises(Retry):
            update_exchange_rate_on_release_payments(payment_plan_id=str(payment_plan.pk))

    mock_logger.exception.assert_called_once_with("PaymentPlan Update Exchange Rate On Release Payments Error")
    mock_retry.assert_called_once()


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService")
def test_periodic_send_payment_plan_reconciliation_overdue_emails(
    mock_service_cls: Mock,
) -> None:
    periodic_send_payment_plan_reconciliation_overdue_emails()
    mock_service_cls.send_reconciliation_overdue_emails.assert_called_once()


@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.apps.payment.celery_tasks.periodic_send_payment_plan_reconciliation_overdue_emails.retry")
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
        periodic_send_payment_plan_reconciliation_overdue_emails()

    mock_logger.exception.assert_called_once_with(error)
    mock_retry.assert_called_once_with(exc=error)


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService")
def test_send_payment_plan_reconciliation_overdue_email(mock_service_cls: Mock, payment_plan: PaymentPlan) -> None:
    mock_service = mock_service_cls.return_value
    send_payment_plan_reconciliation_overdue_email(str(payment_plan.id))
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
    payment_plan_apply_engine_rule(str(payment_plan.id), str(rule.id))

    mock_logger.error.assert_called_once_with("PaymentPlan Run Engine Rule Error no RuleCommit")

    payment_plan.refresh_from_db(fields=["background_action_status"])
    assert payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.RULE_ENGINE_ERROR

    rule_commit.is_release = True
    rule_commit.save()
    rule_commit.refresh_from_db(fields=["is_release"])

    assert rule_commit.is_release is True
    payment_plan_apply_engine_rule(str(payment_plan.id), str(rule.id))

    payment_plan.refresh_from_db(fields=["background_action_status", "steficon_rule_id"])
    assert str(payment_plan.steficon_rule_id) == str(rule_commit.id)
    assert payment_plan.background_action_status is None


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
    import_payment_plan_payment_list_from_xlsx(str(payment_plan.pk))

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
@patch("hope.apps.payment.celery_tasks.import_payment_plan_payment_list_from_xlsx.retry")
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
        import_payment_plan_payment_list_from_xlsx(str(payment_plan.pk))

    mock_service_cls.assert_not_called()
    mock_logger.exception.assert_called_once_with("PaymentPlan Unexpected Error import from xlsx")
    mock_retry.assert_called_once()
    error = mock_retry.call_args.kwargs.get("exc")
    assert error is not None
    assert str(error).startswith("Error import from xlsx, file does not exist for Payment Plan ID")


@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.apps.payment.celery_tasks.import_payment_plan_payment_list_from_xlsx.retry")
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
        import_payment_plan_payment_list_from_xlsx(str(payment_plan.pk))

    payment_plan.refresh_from_db(fields=["background_action_status"])
    assert payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.XLSX_IMPORT_ERROR
    mock_service.open_workbook.assert_called_once()
    assert mock_logger.exception.call_count == 2
    mock_logger.exception.assert_has_calls(
        [
            call("PaymentPlan Error import from xlsx"),
            call("PaymentPlan Unexpected Error import from xlsx"),
        ]
    )
    assert mock_retry.call_count == 2


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
        import_payment_plan_payment_list_per_fsp_from_xlsx(str(payment_plan.pk))

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
        import_payment_plan_payment_list_per_fsp_from_xlsx(str(payment_plan.pk))

    payment_plan.refresh_from_db(fields=["status"])
    assert payment_plan.status == PaymentPlan.Status.ACCEPTED
    mock_service_cls.return_value.import_payment_list.assert_called_once()


@patch("hope.apps.payment.celery_tasks.logger")
@patch("hope.apps.payment.celery_tasks.import_payment_plan_payment_list_per_fsp_from_xlsx.retry")
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
        import_payment_plan_payment_list_per_fsp_from_xlsx(str(payment_plan.pk))

    payment_plan.refresh_from_db(fields=["background_action_status"])
    assert payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.XLSX_IMPORT_ERROR
    assert mock_logger.exception.call_count == 2
    assert mock_logger.exception.call_args_list[0].args[0] == "Unexpected error during xlsx per fsp import"
    assert isinstance(mock_logger.exception.call_args_list[1].args[0], Retry)
    assert mock_retry.call_count == 2


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

    payment_plan_apply_steficon_hh_selection(str(payment_plan.pk), str(engine_rule.id))

    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.TP_STEFICON_COMPLETED

    payment.refresh_from_db(fields=["vulnerability_score"])
    assert payment.vulnerability_score == Decimal("500.333")


@patch("hope.models.rule.RuleCommit.execute")
@patch("hope.apps.payment.celery_tasks.payment_plan_apply_steficon_hh_selection.retry")
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
        payment_plan_apply_steficon_hh_selection(str(payment_plan.pk), str(engine_rule.id))

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
    payment_plan_apply_steficon_hh_selection(str(payment_plan.id), str(rule.id))

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

    remove_old_cash_plan_payment_verification_xlsx()

    assert FileTemp.objects.all().count() == 0


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

    remove_old_payment_plan_payment_list_xlsx()

    assert FileTemp.objects.all().count() == 0


@patch("hope.apps.payment.services.qcf_reports_service.QCFReportsService")
def test_periodic_sync_payment_plan_invoices_western_union_ftp_runs_service_process_files_since(
    mock_service_cls: Mock,
) -> None:
    mock_service = mock_service_cls.return_value
    periodic_sync_payment_plan_invoices_western_union_ftp()
    mock_service.process_files_since.assert_called_once()


@patch("hope.apps.payment.celery_tasks.logger.exception")
@patch("hope.apps.payment.celery_tasks.periodic_sync_payment_plan_invoices_western_union_ftp.retry")
@patch("hope.apps.payment.services.qcf_reports_service.QCFReportsService")
def test_periodic_sync_payment_plan_invoices_western_union_ftp_retries_on_exception(
    mock_service_cls: Mock,
    mock_retry: Mock,
    mock_logger_exception: Mock,
) -> None:
    mock_service = mock_service_cls.return_value
    mock_service.process_files_since.side_effect = Exception("test")
    mock_retry.side_effect = Retry("retry")
    with pytest.raises(Retry):
        periodic_sync_payment_plan_invoices_western_union_ftp()
    mock_logger_exception.assert_called_once()
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
    send_qcf_report_email_notifications(qcf_report_id=qcf_report.id)
    assert bool(mock_service.send_notification_emails.call_count) == should_send
    qcf_report.refresh_from_db()
    assert qcf_report.sent is should_send


@patch("hope.apps.payment.celery_tasks.logger.exception")
@patch("hope.apps.payment.celery_tasks.send_qcf_report_email_notifications.retry")
@patch("hope.apps.payment.services.qcf_reports_service.QCFReportsService")
def test_send_qcf_report_email_notifications_retries_on_exception(
    mock_service_cls: Mock,
    mock_retry: Mock,
    mock_logger_exception: Mock,
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
        send_qcf_report_email_notifications(qcf_report_id=qcf_report.id)
    mock_logger_exception.assert_called_once()
    mock_retry.assert_called_once()
