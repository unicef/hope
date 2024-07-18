from typing import Any

from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from hct_mis_api.api.caches import get_or_create_cache_key
from hct_mis_api.apps.periodic_data_update.models import (
    PeriodicDataUpdateTemplate,
    PeriodicDataUpdateUpload,
)


@receiver(post_save, sender=PeriodicDataUpdateTemplate)
def increment_periodic_data_update_template_version_cache(
    sender: Any, instance: PeriodicDataUpdateTemplate, created: bool, **kwargs: dict
) -> None:
    business_area_slug = instance.business_area.slug
    business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
    program_id = instance.program.id

    version_key = f"{business_area_slug}:{business_area_version}:{program_id}:periodic_data_update_template_list"
    get_or_create_cache_key(version_key, 0)

    cache.incr(version_key)


@receiver(post_save, sender=PeriodicDataUpdateUpload)
def increment_periodic_data_update_upload_version_cache(
    sender: Any, instance: PeriodicDataUpdateTemplate, created: bool, **kwargs: dict
) -> None:
    business_area_slug = instance.template.business_area.slug
    business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
    program_id = instance.template.program.id

    version_key = f"{business_area_slug}:{business_area_version}:{program_id}:periodic_data_update_upload_list"
    get_or_create_cache_key(version_key, 0)

    cache.incr(version_key)
