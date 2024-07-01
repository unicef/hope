from typing import Any

from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from hct_mis_api.apps.core.models import DataCollectingType


@receiver(m2m_changed, sender=DataCollectingType.compatible_types.through)
def validate_compatible_types(
    sender: Any, instance: DataCollectingType, action: str, pk_set: set, **kwargs: Any
) -> None:
    if action == "pre_add":
        incompatible_dcts = DataCollectingType.objects.filter(pk__in=pk_set).exclude(type=instance.type)
        if incompatible_dcts.exists():
            raise ValidationError("DCTs of different types cannot be compatible with each other.")
