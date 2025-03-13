from typing import Any

from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from hct_mis_api.api.caches import get_or_create_cache_key
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


@receiver(post_save, sender=RegistrationDataImport)
@receiver(pre_delete, sender=RegistrationDataImport)
def increment_registration_data_import_version_cache(
    sender: Any, instance: RegistrationDataImport, **kwargs: dict
) -> None:
    business_area_slug = instance.business_area.slug
    business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
    program_slug = instance.program.slug

    version_key = f"{business_area_slug}:{business_area_version}:{program_slug}:registration_data_import_list"
    get_or_create_cache_key(version_key, 0)

    cache.incr(version_key)
