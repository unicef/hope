from typing import Any

from django.db import transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import Signal, receiver

from hope.api.caches import get_or_create_cache_key, increment_cache_key
from hope.models import RegistrationDataImport


@receiver(post_save, sender=RegistrationDataImport)
@receiver(pre_delete, sender=RegistrationDataImport)
def increment_registration_data_import_version_cache(
    sender: Any, instance: RegistrationDataImport, **kwargs: dict
) -> None:
    business_area_slug = instance.business_area.slug
    program_code = instance.program.code

    def _do_increment() -> None:
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
        version_key = f"{business_area_slug}:{business_area_version}:{program_code}:registration_data_import_list"
        increment_cache_key(version_key)

    transaction.on_commit(_do_increment)


rdi_merged = Signal()
