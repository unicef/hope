from typing import Any

from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from hct_mis_api.api.caches import get_or_create_cache_key
from hct_mis_api.apps.geo.models import Area, AreaType, Country
from hct_mis_api.apps.program.models import ProgramPartnerThrough


@receiver(post_save, sender=Area)
def handle_add_area_to_full_area_access_program_partner(
    sender: Any, instance: Area, created: bool, **kwargs: Any
) -> None:
    if created:
        business_areas = instance.area_type.country.business_areas.all()
        for business_area in business_areas:
            for program_partner in ProgramPartnerThrough.objects.filter(
                full_area_access=True, program__in=business_area.program_set.all()
            ):
                program_partner.areas.add(instance)


@receiver(post_save, sender=Country)
@receiver(pre_delete, sender=Country)
def increment_country_version_cache(sender: Any, instance: Country, **kwargs: dict) -> None:
    for business_area_slug in instance.business_areas.values_list("slug", flat=True):
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)

        version_key = f"{business_area_slug}:{business_area_version}:country_list"
        get_or_create_cache_key(version_key, 0)

        cache.incr(version_key)


@receiver(post_save, sender=AreaType)
@receiver(pre_delete, sender=AreaType)
def increment_area_type_version_cache(sender: Any, instance: AreaType, **kwargs: dict) -> None:
    for business_area_slug in instance.country.business_areas.values_list("slug", flat=True):
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
        countries_version = get_or_create_cache_key(f"{business_area_slug}:{business_area_version}:country_list", 1)
        version_key = f"{business_area_slug}:{business_area_version}:country_list:{countries_version}:area_type_list"
        get_or_create_cache_key(version_key, 0)

        cache.incr(version_key)


@receiver(post_save, sender=Area)
@receiver(pre_delete, sender=Area)
def increment_area_version_cache(sender: Any, instance: Area, **kwargs: dict) -> None:
    for business_area_slug in instance.area_type.country.business_areas.values_list("slug", flat=True):
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
        countries_version = get_or_create_cache_key(f"{business_area_slug}:{business_area_version}:country_list", 1)
        area_types_version = get_or_create_cache_key(
            f"{business_area_slug}:{business_area_version}:country_list:{countries_version}:area_type_list", 1
        )
        version_key = f"{business_area_slug}:{business_area_version}:country_list:{countries_version}:area_type_list:{area_types_version}:area_list"
        get_or_create_cache_key(version_key, 0)

        cache.incr(version_key)
