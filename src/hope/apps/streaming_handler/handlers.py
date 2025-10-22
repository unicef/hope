from typing import Any

from django.dispatch import receiver

from hope.apps.payment.models import Payment, PaymentPlan
from hope.apps.payment.signals import payment_plan_approved_signal, payment_reconciled_signal
from hope.apps.program.models import Program
from hope.apps.program.signals import program_closed_signal, program_opened_signal
from hope.apps.registration_data.models import RegistrationDataImport
from hope.apps.registration_datahub.signals import rdi_merged
from hope.apps.streaming_handler.hope_live import HopeLiveService


@receiver(rdi_merged)
def rdi_fully_merged(sender: Any, instance: RegistrationDataImport, **kwargs):
    HopeLiveService().notify(
        HopeLiveService.ACTION_RDI_MERGED,
        {
            "business_area": instance.business_area.slug,
            "program": instance.program.name,
            "number_of_hh": instance.number_of_households,
            "number_of_beneficiaries": instance.number_of_individuals,
        },
    )


@receiver(payment_reconciled_signal)
def payment_reconciled(sender: Any, instance: Payment, **kwargs):
    HopeLiveService().notify(
        HopeLiveService.ACTION_PAYMENT_RECONCILED,
        {
            "business_area": instance.business_area.slug,
            "program": instance.program.name,
            "amount": instance.delivered_quantity_usd,
            "household_admin_area": instance.household.admin_area.name,
        },
    )


@receiver(payment_plan_approved_signal)
def payment_plan_approved(sender: Any, instance: PaymentPlan, **kwargs):
    HopeLiveService().notify(
        HopeLiveService.ACTION_PAYMENT_PLAN_APPROVED,
        {
            "business_area": instance.business_area.slug,
            "program": instance.program.name,
            "amount": instance.total_entitled_quantity_usd,
            # "household_admin_area": "", TODO bulk send all payments?
        },
    )


@receiver(program_opened_signal)
def program_opened(sender: Any, instance: Program, **kwargs):
    HopeLiveService().notify(
        HopeLiveService.ACTION_PROGRAM_OPENED,
        {
            "business_area": instance.business_area.slug,
            "program": instance.name,
        },
    )


@receiver(program_closed_signal)
def program_closed(sender: Any, instance: Program, **kwargs):
    HopeLiveService().notify(
        HopeLiveService.ACTION_PROGRAM_CLOSED,
        {
            "business_area": instance.business_area.slug,
            "program": instance.name,
            "number_of_beneficiaries": instance.individual_count,
            "total_amount_paid": instance.get_total_amount_paid()["delivered_quantity_usd"],
        },
    )
