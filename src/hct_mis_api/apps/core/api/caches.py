from typing import Any

from django.db.models import Max

from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.bits import KeyBitBase
from rest_framework_extensions.key_constructor.constructors import KeyConstructor


class BusinessAreaListVersionKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        queryset = view_instance.get_queryset().aggregate(latest_updated_at=Max("updated_at"))
        latest_updated_at = queryset["latest_updated_at"]
        available_business_areas = queryset.order_by("id").values_list("id", flat=True)
        key = f"business_area_list:{latest_updated_at}:{available_business_areas}"
        return key


class BusinessAreaKeyConstructor(KeyConstructor):
    business_area_list = BusinessAreaListVersionKeyBit()
    unique_method_id = bits.UniqueMethodIdKeyBit()
    querystring = bits.QueryParamsKeyBit()
    params = bits.KwargsKeyBit()
    pagination = bits.PaginationKeyBit()
