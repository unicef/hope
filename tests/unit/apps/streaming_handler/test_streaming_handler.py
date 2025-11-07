from typing import Any
from unittest import mock
from unittest.mock import ANY

from django.core.management import call_command
import pytest
from flags.models import FlagState

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.core.base_test_case import BaseTestCase
from hope.apps.geo.models import Country
from hope.apps.payment.signals import payment_plan_approved_signal, payment_reconciled_signal
from hope.apps.program.signals import program_closed_signal, program_opened_signal
from hope.apps.registration_datahub.signals import rdi_merged
from hope.apps.streaming_handler.hope_live import HopeLiveService

pytestmark = pytest.mark.django_db


@mock.patch(
    "hope.apps.streaming_handler.hope_live.manager",
)
@mock.patch(
    "hope.apps.streaming_handler.hope_live.make_event",
)
class TestStreamingHandler(BaseTestCase):
    databases = ("default",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        call_command("loadcountries")
        cls.flag_state = FlagState.objects.get_or_create(
            name="STREAMING_HANDLER_ENABLED",
            condition="boolean",
            value="True",
            required=False,
        )

    def test_rdi_merged(
        self,
        make_event_mock: Any,
        manager_mock: Any,
    ) -> None:
        instance = RegistrationDataImportFactory()
        rdi_merged.send(sender=instance.__class__, instance=instance)

        manager_mock.notify.assert_called_once_with(HopeLiveService.ACTION_RDI_MERGED, ANY)
        make_event_mock.assert_called_once_with(
            {
                "business_area": instance.business_area.slug,
                "program": instance.program.name,
                "number_of_hh": instance.number_of_households,
                "number_of_beneficiaries": instance.number_of_individuals,
            }
        )

    def test_payment_reconciled(
        self,
        make_event_mock: Any,
        manager_mock: Any,
    ) -> None:
        instance = PaymentFactory(program=ProgramFactory())
        country = Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        instance.household.admin4 = AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")
        payment_reconciled_signal.send(sender=instance.__class__, instance=instance)

        manager_mock.notify.assert_called_once_with(HopeLiveService.ACTION_PAYMENT_RECONCILED, ANY)
        make_event_mock.assert_called_once_with(
            {
                "business_area": instance.business_area.slug,
                "program": instance.program.name,
                "amount": instance.delivered_quantity_usd,
                "household_admin_area": instance.household.admin_area.name,
            }
        )

    def test_payment_plan_approved(
        self,
        make_event_mock: Any,
        manager_mock: Any,
    ) -> None:
        instance = PaymentPlanFactory()
        payment_plan_approved_signal.send(sender=instance.__class__, instance=instance)

        manager_mock.notify.assert_called_once_with(HopeLiveService.ACTION_PAYMENT_PLAN_APPROVED, ANY)
        make_event_mock.assert_called_once_with(
            {
                "business_area": instance.business_area.slug,
                "program": instance.program.name,
                "amount": instance.total_entitled_quantity_usd,
            }
        )

    def test_program_opened(
        self,
        make_event_mock: Any,
        manager_mock: Any,
    ) -> None:
        instance = ProgramFactory()
        program_opened_signal.send(sender=instance.__class__, instance=instance)

        manager_mock.notify.assert_called_once_with(HopeLiveService.ACTION_PROGRAM_OPENED, ANY)
        make_event_mock.assert_called_once_with(
            {
                "business_area": instance.business_area.slug,
                "program": instance.name,
            }
        )

    def test_program_closed(
        self,
        make_event_mock: Any,
        manager_mock: Any,
    ) -> None:
        instance = ProgramFactory()
        program_closed_signal.send(sender=instance.__class__, instance=instance)

        manager_mock.notify.assert_called_once_with(HopeLiveService.ACTION_PROGRAM_CLOSED, ANY)
        make_event_mock.assert_called_once_with(
            {
                "business_area": instance.business_area.slug,
                "program": instance.name,
                "number_of_beneficiaries": instance.individual_count,
                "total_amount_paid": instance.get_total_amount_paid()["delivered_quantity_usd"],
            }
        )
