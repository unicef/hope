import logging.config
from unittest.mock import Mock, patch

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.payment.celery_tasks import prepare_payment_plan_task
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.payment.utils import generate_cache_key
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestPaymentCeleryTask(TestCase):
    def setUp(self) -> None:
        create_afghanistan()
        self.program = ProgramFactory(name="Test AAA")

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
            program=self.program,
        )
        payment_plan.refresh_from_db()
        pp_id_str = str(payment_plan.pk)
        result = prepare_payment_plan_task(pp_id_str)

        self.assertFalse(result)
        mock_logger.info.assert_called_with("The Payment Plan must have the status PREPARING.")

    @patch("hct_mis_api.apps.payment.celery_tasks.logger")
    def test_prepare_payment_plan_task_already_running(self, mock_logger: Mock) -> None:
        payment_plan = PaymentPlanFactory(status=PaymentPlan.Status.PREPARING, program=self.program)
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
