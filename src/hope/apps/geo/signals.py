from typing import Any

from django.db import transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from hope.apps.geo.api.caches import increment_country_areas_version
from hope.models import Area, AreaType, Country


@receiver(post_save, sender=Country)
@receiver(pre_delete, sender=Country)
def increment_areas_country_version_by_country(sender: Any, instance: Country, **kwargs: dict) -> None:
    country_id = instance.id
    transaction.on_commit(lambda: increment_country_areas_version(country_id))


@receiver(post_save, sender=AreaType)
@receiver(pre_delete, sender=AreaType)
def increment_areas_country_version_by_area_type(sender: Any, instance: AreaType, **kwargs: dict) -> None:
    country_id = instance.country_id
    transaction.on_commit(lambda: increment_country_areas_version(country_id))


@receiver(post_save, sender=Area)
@receiver(pre_delete, sender=Area)
def increment_areas_country_version_by_area(sender: Any, instance: Area, **kwargs: dict) -> None:
    country_id = instance.area_type.country_id
    transaction.on_commit(lambda: increment_country_areas_version(country_id))
