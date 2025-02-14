from typing import Any

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from hct_mis_api.apps.core.utils import clear_cache_for_key
from hct_mis_api.contrib.aurora.caches import RegistrationListVersionsKeyBit, ProjectListVersionsKeyBit, \
    OrganizationListVersionsKeyBit
from hct_mis_api.contrib.aurora.models import Registration, Project, Organization


@receiver(post_save, sender=Registration)
@receiver(post_delete, sender=Registration)
def clear_registration_list_cache(sender: Any, instance: Registration, **kwargs: Any) -> None:
    cache_key = RegistrationListVersionsKeyBit.specific_view_cache_key
    clear_cache_for_key(cache_key)


@receiver(post_save, sender=Project)
@receiver(post_delete, sender=Project)
def clear_project_list_cache(sender: Any, instance: Project, **kwargs: Any) -> None:
    cache_key = ProjectListVersionsKeyBit.specific_view_cache_key
    clear_cache_for_key(cache_key)


@receiver(post_save, sender=Organization)
@receiver(post_delete, sender=Organization)
def clear_organization_list_cache(sender: Any, instance: Organization, **kwargs: Any) -> None:
    cache_key = OrganizationListVersionsKeyBit.specific_view_cache_key
    clear_cache_for_key(cache_key)
