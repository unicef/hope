import logging.config
from unittest.mock import Mock, patch

from celery.exceptions import Retry
from django.conf import settings
from django.core.cache import cache
from django.test import TestCase
import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.steficon import RuleCommitFactory, RuleFactory
from hope.apps.payment.celery_tasks import (
    create_payment_plan_payment_list_xlsx_per_fsp,
    payment_plan_apply_steficon_hh_selection,
    payment_plan_full_rebuild,
    payment_plan_rebuild_stats,
    prepare_payment_plan_task,
    send_payment_plan_payment_list_xlsx_per_fsp_password,
)
from hope.apps.payment.utils import generate_cache_key
from hope.models.delivery_mechanism import DeliveryMechanism
from hope.models.file_temp import FileTemp
from hope.models.financial_service_provider import FinancialServiceProvider
from hope.models.payment_plan import PaymentPlan
from hope.models.rule import Rule


class TestPaymentCeleryTask(TestCase):
    def setUp(self) -> None:
        generate_delivery_mechanisms()
        self.ba = create_afghanistan()
        self.program = ProgramFactory(name="Test AAA")
        self.user = UserFactory()

        self.financial_service_provider = FinancialServiceProviderFactory(
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
            payment_gateway_id="test123",
        )
        self.dm_cash = DeliveryMechanism.objects.get(code="cash")

        logging.config.dictConfig(settings.LOGGING)
        self.TEST_LOGGING = {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                },
            },
            "loggers": {
                "hope.apps.payment.celery_tasks": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
        logging.config.dictConfig(self.TEST_LOGGING)

    @patch("hope.apps.payment.celery_tasks.logger")
    def test_prepare_payment_plan_task_wrong_pp_status(self, mock_logger: Mock) -> None:
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.TP_LOCKED,
            program_cycle=self.program.cycles.first(),
            build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
            created_by=self.user,
        )
        payment_plan.refresh_from_db()
        result = prepare_payment_plan_task(str(payment_plan.pk))

        assert result is False
        mock_logger.info.assert_called_with("The Payment Plan must have the status TP_OPEN.")

    @patch("hope.apps.payment.celery_tasks.logger")
    def test_prepare_payment_plan_task_already_running(self, mock_logger: Mock) -> None:
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.TP_OPEN,
            program_cycle=self.program.cycles.first(),
            build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
            created_by=self.user,
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
        self, mock_retry: Mock, mock_logger: Mock, mock_create_payments: Mock
    ) -> None:
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.TP_OPEN,
            program_cycle=self.program.cycles.first(),
            build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
            created_by=self.user,
        )
        payment_plan.refresh_from_db()
        assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_PENDING

        mock_create_payments.side_effect = Exception("Simulated exception just for test")
        mock_retry.side_effect = Retry("Simulated retry")
        with pytest.raises(Retry):
            prepare_payment_plan_task(payment_plan_id=str(payment_plan.pk))

        payment_plan.refresh_from_db()

        mock_logger.exception.assert_called_once_with("Prepare Payment Plan Error")
        mock_retry.assert_called_once_with(exc=mock_create_payments.side_effect)

        assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_FAILED

    def test_payment_plan_apply_steficon_hh_selection(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
            status=PaymentPlan.Status.TP_STEFICON_WAIT,
            steficon_rule_targeting=RuleCommitFactory(version=33),
        )
        PaymentFactory(parent=payment_plan)
        payment_plan.refresh_from_db()
        assert payment_plan.status == PaymentPlan.Status.TP_STEFICON_WAIT

        engine_rule = RuleFactory(name="Rule-test", type=Rule.TYPE_TARGETING)
        RuleCommitFactory(definition="result.value=Decimal('500')", rule=engine_rule, version=11)

        payment_plan_apply_steficon_hh_selection(str(payment_plan.pk), str(engine_rule.id))

        payment_plan.refresh_from_db()
        assert payment_plan.status == PaymentPlan.Status.TP_STEFICON_COMPLETED

    @patch("hope.apps.steficon.models.RuleCommit.execute")
    @patch("hope.apps.payment.celery_tasks.payment_plan_apply_steficon_hh_selection.retry")
    def test_payment_plan_apply_steficon_hh_selection_exception_handling(
        self, mock_retry: Mock, mock_rule_execute: Mock
    ) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
            status=PaymentPlan.Status.TP_STEFICON_WAIT,
        )
        PaymentFactory(parent=payment_plan)
        payment_plan.refresh_from_db()
        assert payment_plan.status == PaymentPlan.Status.TP_STEFICON_WAIT
        engine_rule = RuleFactory(name="Rule-test123", type=Rule.TYPE_TARGETING)
        RuleCommitFactory(definition="result.value=Decimal('123')", rule=engine_rule, version=2)

        mock_rule_execute.side_effect = Exception("Simulated exception just for test")
        mock_retry.side_effect = Retry("Simulated retry")
        with pytest.raises(Retry):
            payment_plan_apply_steficon_hh_selection(str(payment_plan.pk), str(engine_rule.id))

        mock_retry.assert_called_once()
        payment_plan.refresh_from_db()
        assert payment_plan.status == PaymentPlan.Status.TP_STEFICON_ERROR

    @patch(
        "hope.apps.payment.models.PaymentPlan.get_exchange_rate",
        return_value=2.0,
    )
    def test_payment_plan_rebuild_stats(self, get_exchange_rate_mock: Mock) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
            status=PaymentPlan.Status.TP_STEFICON_WAIT,
            build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
        )
        PaymentFactory(parent=payment_plan)
        pp_id_str = str(payment_plan.pk)

        payment_plan_rebuild_stats(pp_id_str)

    @patch("hope.apps.payment.models.PaymentPlan.update_population_count_fields")
    @patch("hope.apps.payment.celery_tasks.payment_plan_rebuild_stats.retry")
    def test_payment_plan_rebuild_stats_exception_handling(
        self, mock_retry: Mock, mock_update_population_count_fields: Mock
    ) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
            status=PaymentPlan.Status.TP_STEFICON_WAIT,
            build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
        )
        PaymentFactory(parent=payment_plan)
        mock_update_population_count_fields.side_effect = Exception("Simulated exception just for test")
        mock_retry.side_effect = Retry("Simulated retry")
        with pytest.raises(Retry):
            payment_plan_rebuild_stats(str(payment_plan.pk))

        mock_retry.assert_called_once()

    def test_payment_plan_full_rebuild(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
            status=PaymentPlan.Status.TP_OPEN,
            build_status=PaymentPlan.BuildStatus.BUILD_STATUS_FAILED,
            financial_service_provider=self.financial_service_provider,
            delivery_mechanism=self.dm_cash,
        )
        PaymentFactory(parent=payment_plan)
        payment_plan_full_rebuild(str(payment_plan.pk))

        payment_plan.refresh_from_db()
        assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK

    @patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.full_rebuild")
    @patch("hope.apps.payment.celery_tasks.payment_plan_full_rebuild.retry")
    def test_payment_plan_full_rebuild_retry_exception_handling(
        self, mock_retry: Mock, mock_full_rebuild: Mock
    ) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
            status=PaymentPlan.Status.TP_LOCKED,
            build_status=PaymentPlan.BuildStatus.BUILD_STATUS_OK,
        )
        PaymentFactory(parent=payment_plan)
        mock_full_rebuild.side_effect = Exception("Simulated exception just for test")
        mock_retry.side_effect = Retry("Simulated retry")
        with pytest.raises(Retry):
            payment_plan_full_rebuild(str(payment_plan.pk))

        mock_retry.assert_called_once()
        payment_plan.refresh_from_db()
        assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_FAILED

    def test_create_payment_plan_payment_list_xlsx_per_fsp(self) -> None:
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.ACCEPTED,
            background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
            financial_service_provider=self.financial_service_provider,
            delivery_mechanism=self.dm_cash,
        )
        fsp_template = FinancialServiceProviderXlsxTemplateFactory()
        # create zip file with passwords
        create_payment_plan_payment_list_xlsx_per_fsp(str(payment_plan.pk), str(self.user.pk), str(fsp_template.pk))

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

    @patch("hope.apps.payment.notifications.MailjetClient.send_email")
    def test_send_payment_plan_payment_list_xlsx_per_fsp_password(self, mock_mailjet_send: Mock) -> None:
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.FINISHED,
            background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
            financial_service_provider=self.financial_service_provider,
            delivery_mechanism=self.dm_cash,
        )
        fsp_template = FinancialServiceProviderXlsxTemplateFactory()
        # create zip file with passwords
        create_payment_plan_payment_list_xlsx_per_fsp(str(payment_plan.pk), str(self.user.pk), str(fsp_template.pk))
        payment_plan.refresh_from_db()
        file_obj = FileTemp.objects.get(object_id=payment_plan.id)

        assert payment_plan.background_action_status is None
        assert payment_plan.export_file_per_fsp == file_obj
        assert file_obj.password is not None
        assert file_obj.xlsx_password is not None

        send_payment_plan_payment_list_xlsx_per_fsp_password(str(payment_plan.pk), str(self.user.pk))

        # first call from > create_payment_plan_payment_list_xlsx_per_fsp
        # second call from > send_payment_plan_payment_list_xlsx_per_fsp_password
        assert mock_mailjet_send.call_count == 2

    @patch("hope.apps.payment.celery_tasks.logger")
    @patch("hope.apps.payment.celery_tasks.get_user_model")
    def test_send_payment_plan_payment_list_xlsx_per_fsp_password_failure(
        self, mock_get_user_model: Mock, mock_logger: Mock
    ) -> None:
        mock_get_user_model.objects.get.side_effect = Exception("User not found")
        with pytest.raises(Exception, match="“pp_id_123” is not a valid UUID."):
            send_payment_plan_payment_list_xlsx_per_fsp_password("pp_id_123", "invalid-user-id-123")

        mock_logger.exception.assert_called_once_with("Send Payment Plan List XLSX Per FSP Password Error")
