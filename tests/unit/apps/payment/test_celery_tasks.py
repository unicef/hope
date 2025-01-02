import logging.config
from unittest.mock import Mock, patch

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.payment.celery_tasks import (
    create_payment_plan_payment_list_xlsx_per_fsp,
    prepare_payment_plan_task,
    send_payment_plan_payment_list_xlsx_per_fsp_password,
)
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismPerPaymentPlanFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    PaymentPlanFactory,
)
from hct_mis_api.apps.payment.models import FinancialServiceProvider, PaymentPlan
from hct_mis_api.apps.payment.utils import generate_cache_key
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestPaymentCeleryTask(TestCase):
    def setUp(self) -> None:
        self.ba = create_afghanistan()
        self.program = ProgramFactory(name="Test AAA")
        self.user = UserFactory()

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
                "hct_mis_api.apps.payment.celery_tasks": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
        logging.config.dictConfig(self.TEST_LOGGING)

    @patch("hct_mis_api.apps.payment.celery_tasks.logger")
    def test_prepare_payment_plan_task_wrong_pp_status(self, mock_logger: Mock) -> None:
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
        )
        payment_plan.refresh_from_db()
        pp_id_str = str(payment_plan.pk)
        result = prepare_payment_plan_task(pp_id_str)

        self.assertFalse(result)
        mock_logger.info.assert_called_with("The Payment Plan must have the status PREPARING.")

    @patch("hct_mis_api.apps.payment.celery_tasks.logger")
    def test_prepare_payment_plan_task_already_running(self, mock_logger: Mock) -> None:
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.PREPARING,
            program_cycle=self.program.cycles.first(),
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

        self.assertFalse(result)
        mock_logger.info.assert_called_with(
            f"Task prepare_payment_plan_task with payment_plan_id {pp_id_str} already running."
        )

    def test_create_payment_plan_payment_list_xlsx_per_fsp(self) -> None:
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.ACCEPTED,
            background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
        )
        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=payment_plan,
            financial_service_provider__communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            created_by=self.user,
            sent_by=self.user,
        )
        fsp_template = FinancialServiceProviderXlsxTemplateFactory()
        # create zip file with passwords
        create_payment_plan_payment_list_xlsx_per_fsp(str(payment_plan.pk), str(self.user.pk), str(fsp_template.pk))

        payment_plan.refresh_from_db()
        file_obj = FileTemp.objects.get(object_id=payment_plan.id)

        self.assertIsNone(payment_plan.background_action_status)
        self.assertTrue(payment_plan.has_export_file)
        self.assertTrue(
            payment_plan.export_file_per_fsp.file.name.startswith(f"payment_plan_payment_list_{payment_plan.unicef_id}")
        )
        self.assertTrue(payment_plan.export_file_per_fsp.file.name.endswith(".zip"))
        self.assertIsNotNone(file_obj.password)
        self.assertIsNotNone(file_obj.xlsx_password)

    @patch("hct_mis_api.apps.payment.notifications.MailjetClient.send_email")
    def test_send_payment_plan_payment_list_xlsx_per_fsp_password(self, mock_mailjet_send: Mock) -> None:
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.FINISHED,
            background_action_status=PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
            program_cycle=self.program.cycles.first(),
            created_by=self.user,
        )
        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=payment_plan,
            financial_service_provider__communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            created_by=self.user,
            sent_by=self.user,
        )
        fsp_template = FinancialServiceProviderXlsxTemplateFactory()
        # create zip file with passwords
        create_payment_plan_payment_list_xlsx_per_fsp(str(payment_plan.pk), str(self.user.pk), str(fsp_template.pk))
        payment_plan.refresh_from_db()
        file_obj = FileTemp.objects.get(object_id=payment_plan.id)

        self.assertIsNone(payment_plan.background_action_status)
        self.assertEqual(payment_plan.export_file_per_fsp, file_obj)
        self.assertIsNotNone(file_obj.password)
        self.assertIsNotNone(file_obj.xlsx_password)

        send_payment_plan_payment_list_xlsx_per_fsp_password(str(payment_plan.pk), str(self.user.pk))

        # first call from > create_payment_plan_payment_list_xlsx_per_fsp
        # second call from > send_payment_plan_payment_list_xlsx_per_fsp_password
        self.assertEqual(
            mock_mailjet_send.call_count,
            2,
        )

    @patch("hct_mis_api.apps.payment.celery_tasks.logger")
    @patch("hct_mis_api.apps.payment.celery_tasks.get_user_model")
    def test_send_payment_plan_payment_list_xlsx_per_fsp_password_failure(
        self, mock_get_user_model: Mock, mock_logger: Mock
    ) -> None:
        mock_get_user_model.objects.get.side_effect = Exception("User not found")
        with self.assertRaises(Exception):  # noqa: B017
            send_payment_plan_payment_list_xlsx_per_fsp_password("pp_id_123", "invalid-user-id-123")

        mock_logger.exception.assert_called_once_with("Send Payment Plan List XLSX Per FSP Password Error")
