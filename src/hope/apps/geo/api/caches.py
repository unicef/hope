from django.core.cache import cache
from rest_framework_extensions.key_constructor.bits import KeyBitBase

from hope.api.caches import KeyConstructorMixin, get_or_create_cache_key

COUNTRY_AREAS_VERSION_KEY = "country_areas:{}:version"


def get_country_areas_version(country_id):
    return get_or_create_cache_key(COUNTRY_AREAS_VERSION_KEY.format(country_id), 0)


def increment_country_areas_version(country_id):
    key = COUNTRY_AREAS_VERSION_KEY.format(country_id)
    try:
        return cache.incr(key)
    except ValueError:
        cache.set(key, 0)
        return 0


class CountryAreasKeyBit(KeyBitBase):
    def get_data(self, params, view_instance, view_method, request, args, kwargs):
        ba = view_instance.business_area
        sorted_countries_ids = sorted([str(country.id) for country in ba.countries.all()])
        countries_versions = [get_country_areas_version(country_id) for country_id in sorted_countries_ids]
        return {
            "countries_versions": "-".join(str(v) for v in countries_versions),
        }


class AreasKeyConstructor(KeyConstructorMixin):
    country_areas = CountryAreasKeyBit()
