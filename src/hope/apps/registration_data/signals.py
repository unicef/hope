from typing import Any

from django.db import transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import Signal, receiver

from hope.api.caches import get_or_create_cache_key, increment_cache_key
from hope.models import RegistrationDataImport


def invalidate_rdi_cache(business_area_slug: str, program_code: str) -> None:
    """Invalidate RDI list cache for a given business area and program.

    Call explicitly after RegistrationDataImport.objects.filter(...).update(...)
    since .update() bypasses post_save signals.
    """

    def _do_increment() -> None:
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
        version_key = f"{business_area_slug}:{business_area_version}:{program_code}:registration_data_import_list"
        increment_cache_key(version_key)

    transaction.on_commit(_do_increment)


@receiver(post_save, sender=RegistrationDataImport)
@receiver(pre_delete, sender=RegistrationDataImport)
def increment_registration_data_import_version_cache(
    sender: Any, instance: RegistrationDataImport, **kwargs: dict
) -> None:
    invalidate_rdi_cache(instance.business_area.slug, instance.program.code)


rdi_merged = Signal()
