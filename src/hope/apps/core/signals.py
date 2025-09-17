from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from hope.apps.account.models import Partner, Role, RoleAssignment
from hope.apps.account.permissions import DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER
from hope.apps.core.celery_tasks import notify_hope_live
from hope.apps.core.models import BusinessArea, DataCollectingType
from hope.apps.core.services.hope_live import HopeLiveService
from hope.apps.payment.models import Payment, PaymentPlan
from hope.apps.payment.signals import payment_plan_approved_signal, payment_reconciled_signal
from hope.apps.program.models import Program
from hope.apps.program.signals import program_closed_signal, program_opened_signal
from hope.apps.registration_data.models import RegistrationDataImport
from hope.apps.registration_datahub.signals import rdi_merged


@receiver(m2m_changed, sender=DataCollectingType.compatible_types.through)
def validate_compatible_types(
    sender: Any, instance: DataCollectingType, action: str, pk_set: set, **kwargs: Any
) -> None:
    if action == "pre_add":
        incompatible_dcts = DataCollectingType.objects.filter(pk__in=pk_set).exclude(type=instance.type)
        if incompatible_dcts.exists():
            raise ValidationError("DCTs of different types cannot be compatible with each other.")


@receiver(post_save, sender=DataCollectingType)
def add_self_to_compatible_types(sender: Any, instance: DataCollectingType, created: bool, **kwargs: Any) -> None:
    if created:
        instance.compatible_types.add(instance)


@receiver(post_save, sender=BusinessArea)
def business_area_created(sender: Any, instance: BusinessArea, created: bool, **kwargs: Any) -> None:
    """Create new UNICEF subpartners for the new business area."""
    if created:
        unicef = Partner.objects.get(name="UNICEF")
        unicef_subpartner = Partner.objects.create(name=f"UNICEF Partner for {instance.slug}", parent=unicef)
        role_for_unicef_subpartners, _ = Role.objects.get_or_create(
            name="Role for UNICEF Partners",
            is_visible_on_ui=False,
            is_available_for_partner=False,
            defaults={"permissions": DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER},
        )
        unicef_subpartner.allowed_business_areas.add(instance)
        RoleAssignment.objects.create(
            user=None,
            partner=unicef_subpartner,
            role=role_for_unicef_subpartners,
            business_area=instance,
            program=None,
        )
        unicef_hq = Partner.objects.get(name=settings.UNICEF_HQ_PARTNER)
        unicef_hq.allowed_business_areas.add(instance)
        RoleAssignment.objects.create(
            user=None,
            partner=unicef_hq,
            role=Role.objects.filter(name="Role with all permissions").first(),
            business_area=instance,
            program=None,
        )


@receiver(rdi_merged)
def rdi_fully_merged(sender: Any, instance: RegistrationDataImport, **kwargs):
    data_dict = {
        "action": HopeLiveService.ACTION_RDI_MERGED,
        "data": {
            "business_area": instance.business_area.slug,
            "program": instance.program.name,
            "number_of_hh": instance.number_of_households,
            "number_of_beneficiaries": instance.number_of_individuals,
        },
    }
    transaction.on_commit(lambda: notify_hope_live.delay(data_dict))


@receiver(payment_reconciled_signal)
def payment_reconciled(sender: Any, instance: Payment, **kwargs):
    data_dict = {
        "action": HopeLiveService.ACTION_PAYMENT_RECONCILED,
        "data": {
            "business_area": instance.business_area.slug,
            "program": instance.program.name,
            "amount": instance.delivered_quantity_usd,
            "household_admin_area": instance.household.admin_area.name,
        },
    }
    transaction.on_commit(lambda: notify_hope_live.delay(data_dict))


@receiver(payment_plan_approved_signal)
def payment_plan_approved(sender: Any, instance: PaymentPlan, **kwargs):
    data_dict = {
        "action": HopeLiveService.ACTION_PAYMENT_PLAN_APPROVED,
        "data": {
            "business_area": instance.business_area.slug,
            "program": instance.program.name,
            "amount": instance.total_entitled_quantity_usd,
            # "household_admin_area": "", TODO bulk send all payments?
        },
    }
    transaction.on_commit(lambda: notify_hope_live.delay(data_dict))


@receiver(program_opened_signal)
def program_opened(sender: Any, instance: Program, **kwargs):
    data_dict = {
        "action": HopeLiveService.ACTION_PROGRAM_OPENED,
        "data": {
            "business_area": instance.business_area.slug,
            "program": instance.name,
        },
    }
    transaction.on_commit(lambda: notify_hope_live.delay(data_dict))


@receiver(program_closed_signal)
def program_closed(sender: Any, instance: Program, **kwargs):
    data_dict = {
        "action": HopeLiveService.ACTION_PROGRAM_CLOSED,
        "data": {
            "business_area": instance.business_area.slug,
            "program": instance.name,
            "number_of_beneficiaries": instance.individual_count,
            "total_amount_paid": instance.get_total_amount_paid()["delivered_quantity_usd"],
        },
    }
    transaction.on_commit(lambda: notify_hope_live.delay(data_dict))
