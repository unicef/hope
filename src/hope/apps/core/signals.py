from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from hope.apps.account.models import Partner, Role, RoleAssignment
from hope.apps.account.permissions import DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER
from hope.apps.core.models import BusinessArea, DataCollectingType


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
