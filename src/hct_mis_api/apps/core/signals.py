from typing import Any

from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver

from hct_mis_api.apps.core.models import BusinessAreaPartnerThrough, DataCollectingType
from hct_mis_api.apps.program.models import ProgramPartnerThrough


@receiver(m2m_changed, sender=DataCollectingType.compatible_types.through)
def validate_compatible_types(
    sender: Any, instance: DataCollectingType, action: str, pk_set: set, **kwargs: Any
) -> None:
    if action == "pre_add":
        incompatible_dcts = DataCollectingType.objects.filter(pk__in=pk_set).exclude(type=instance.type)
        if incompatible_dcts.exists():
            raise ValidationError("DCTs of different types cannot be compatible with each other.")


@receiver(post_delete, sender=BusinessAreaPartnerThrough)
def partner_role_removed(sender: Any, instance: BusinessAreaPartnerThrough, **kwargs: Any) -> None:
    """If roles are revoked for a Partner from a whole Business Area, Partner looses access to all Programs in this Business Area."""
    partner = instance.partner
    business_area = instance.business_area
    programs_in_business_area = business_area.program_set.all()
    ProgramPartnerThrough.objects.filter(partner=partner, program__in=programs_in_business_area).delete()
