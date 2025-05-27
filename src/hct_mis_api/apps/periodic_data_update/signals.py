from typing import Any

from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from hct_mis_api.api.caches import get_or_create_cache_key
from hct_mis_api.apps.core.models import FlexibleAttribute, PeriodicFieldData
from hct_mis_api.apps.periodic_data_update.models import (
    PeriodicDataUpdateTemplate, PeriodicDataUpdateUpload)


@receiver(post_save, sender=PeriodicDataUpdateTemplate)
@receiver(pre_delete, sender=PeriodicDataUpdateUpload)
def increment_periodic_data_update_template_version_cache(
    sender: Any, instance: PeriodicDataUpdateTemplate, **kwargs: dict
) -> None:
    business_area_slug = instance.business_area.slug
    program_slug = instance.program.slug
    increment_periodic_data_update_template_version_cache_function(business_area_slug, program_slug)


def increment_periodic_data_update_template_version_cache_function(business_area_slug: str, program_slug: str) -> None:
    business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
    version_key = f"{business_area_slug}:{business_area_version}:{program_slug}:periodic_data_update_template_list"
    get_or_create_cache_key(version_key, 0)

    cache.incr(version_key)


@receiver(post_save, sender=PeriodicDataUpdateUpload)
@receiver(pre_delete, sender=PeriodicDataUpdateUpload)
def increment_periodic_data_update_upload_version_cache(
    sender: Any, instance: PeriodicDataUpdateUpload, **kwargs: dict
) -> None:
    business_area_slug = instance.template.business_area.slug
    business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
    program_slug = instance.template.program.slug

    version_key = f"{business_area_slug}:{business_area_version}:{program_slug}:periodic_data_update_upload_list"
    get_or_create_cache_key(version_key, 0)

    cache.incr(version_key)


@receiver(post_save, sender=FlexibleAttribute)
@receiver(pre_delete, sender=FlexibleAttribute)
def increment_periodic_field_version_cache_for_flexible_attribute(
    sender: Any, instance: FlexibleAttribute, **kwargs: dict
) -> None:
    if instance.type == FlexibleAttribute.PDU and instance.program:
        business_area_slug = instance.program.business_area.slug
        program_slug = instance.program.slug
        increment_periodic_field_version_cache(business_area_slug, program_slug)


@receiver(post_save, sender=PeriodicFieldData)
@receiver(pre_delete, sender=PeriodicFieldData)
def increment_periodic_field_version_cache_for_periodic_field_data(
    sender: Any, instance: PeriodicFieldData, **kwargs: dict
) -> None:
    flex_field = getattr(instance, "flex_field", None)
    if flex_field:
        business_area_slug = flex_field.program.business_area.slug
        program_slug = flex_field.program.slug
        increment_periodic_field_version_cache(business_area_slug, program_slug)


def increment_periodic_field_version_cache(business_area_slug: str, program_slug: str) -> None:
    business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
    version_key = f"{business_area_slug}:{business_area_version}:{program_slug}:periodic_field_list"
    get_or_create_cache_key(version_key, 0)

    cache.incr(version_key)
