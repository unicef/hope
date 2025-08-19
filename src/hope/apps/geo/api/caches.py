from typing import Any

from rest_framework_extensions.key_constructor.bits import KeyBitBase

from hope.api.caches import KeyConstructorMixin, get_or_create_cache_key


class AreaListVersionsKeyBit(KeyBitBase):
    specific_view_cache_key = "area_list"

    def get_data(
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Any,
        args: tuple,
        kwargs: dict,
    ) -> str:
        business_area_slug = kwargs.get("business_area_slug")
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
        countries_version = get_or_create_cache_key(f"{business_area_slug}:{business_area_version}:country_list", 1)
        area_types_version = get_or_create_cache_key(
            f"{business_area_slug}:{business_area_version}:country_list:{countries_version}:area_type_list",
            1,
        )
        version_key = f"{business_area_slug}:{business_area_version}:country_list:{countries_version}:area_type_list:{area_types_version}:{self.specific_view_cache_key}"
        version = get_or_create_cache_key(version_key, 1)
        return str(version)


class CountryListVersionsKeyBit(KeyBitBase):
    specific_view_cache_key = "country_list"

    def get_data(
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Any,
        args: tuple,
        kwargs: dict,
    ) -> str:
        business_area_slug = kwargs.get("business_area_slug")
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
        version_key = f"{business_area_slug}:{business_area_version}:{self.specific_view_cache_key}"
        version = get_or_create_cache_key(version_key, 1)
        return str(version)


class AreaTypeListVersionsKeyBit(KeyBitBase):
    specific_view_cache_key = "area_type_list"

    def get_data(
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Any,
        args: tuple,
        kwargs: dict,
    ) -> str:
        business_area_slug = kwargs.get("business_area_slug")
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
        countries_version = get_or_create_cache_key(f"{business_area_slug}:{business_area_version}:country_list", 1)
        version_key = f"{business_area_slug}:{business_area_version}:country_list:{countries_version}:{self.specific_view_cache_key}"
        version = get_or_create_cache_key(version_key, 1)
        return str(version)


class AreaKeyConstructor(KeyConstructorMixin):
    area_list_version = AreaListVersionsKeyBit()
    country_list_version = CountryListVersionsKeyBit()
    area_type_list_version = AreaTypeListVersionsKeyBit()
