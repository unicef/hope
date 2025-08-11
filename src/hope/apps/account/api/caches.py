from typing import Any

from django.db.models import Count, Max

from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.bits import KeyBitBase
from rest_framework_extensions.key_constructor.constructors import KeyConstructor

from hope.api.caches import get_or_create_cache_key


class UserListVersionsKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        business_area_slug = kwargs.get("business_area_slug")
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)

        queryset = view_instance.get_queryset().aggregate(
            latest_updated_at=Max("last_modify_date"), obj_count=Count("id")
        )
        latest_updated_at = queryset["latest_updated_at"]
        obj_count = queryset["obj_count"]

        return f"{business_area_slug}:{business_area_version}:user-list:{latest_updated_at}:{obj_count}"


class UserListKeyConstructor(KeyConstructor):
    user_list_version = UserListVersionsKeyBit()
    unique_method_id = bits.UniqueMethodIdKeyBit()
    querystring = bits.QueryParamsKeyBit()
    params = bits.KwargsKeyBit()
    pagination = bits.PaginationKeyBit()
