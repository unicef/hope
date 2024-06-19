from typing import Any

from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.bits import KeyBitBase
from rest_framework_extensions.key_constructor.constructors import KeyConstructor

from hct_mis_api.api.caches import BusinessAreaVersionKeyBit, get_or_create_cache_key
from hct_mis_api.apps.core.utils import decode_id_string


class PDUTemplateListVersionsKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        business_area_slug = kwargs.get("business_area")
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)

        program_id = decode_id_string(kwargs.get("program_id"))

        version_key = f"{business_area_slug}:{business_area_version}:{program_id}:periodic_data_update_template_list"
        version = get_or_create_cache_key(version_key, 1)
        return str(version)


class PDUTemplateKeyConstructor(KeyConstructor):
    unique_method_id = bits.UniqueMethodIdKeyBit()
    periodic_data_update_template_list_versions = PDUTemplateListVersionsKeyBit()
    business_area_version = BusinessAreaVersionKeyBit()
    querystring = bits.QueryParamsKeyBit()
    params = bits.KwargsKeyBit()
    pagination = bits.PaginationKeyBit()
