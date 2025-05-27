from typing import Any

from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.bits import KeyBitBase
from rest_framework_extensions.key_constructor.constructors import \
    KeyConstructor

from hct_mis_api.api.caches import (BusinessAreaAndProgramLastUpdatedKeyBit,
                                    BusinessAreaVersionKeyBit,
                                    KeyConstructorMixin,
                                    get_or_create_cache_key)


class ProgramCycleListVersionsKeyBit(BusinessAreaAndProgramLastUpdatedKeyBit):
    specific_view_cache_key = "program_cycle_list"


class ProgramCycleKeyConstructor(KeyConstructorMixin):
    program_cycle_list_version = ProgramCycleListVersionsKeyBit()


class BeneficiaryGroupListVersionsKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        version = get_or_create_cache_key("beneficiary_group_list", 1)
        return str(version)


class BeneficiaryGroupKeyConstructor(KeyConstructor):
    beneficiary_group_list_version = BeneficiaryGroupListVersionsKeyBit()
    unique_method_id = bits.UniqueMethodIdKeyBit()
    querystring = bits.QueryParamsKeyBit()
    params = bits.KwargsKeyBit()
    pagination = bits.PaginationKeyBit()


class ProgramListVersionKeyBit(BusinessAreaVersionKeyBit):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        business_area_slug = kwargs.get("business_area_slug")
        business_area_version = super().get_data(params, view_instance, view_method, request, args, kwargs)
        version_key = f"{business_area_slug}:{business_area_version}:program_list"
        version = get_or_create_cache_key(version_key, 1)
        return str(version)


class AllowedProgramsKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        allowed_programs = ",".join(
            map(str, request.user.get_program_ids_for_business_area(view_instance.business_area.id))
        )
        return allowed_programs


class ProgramListKeyConstructor(KeyConstructorMixin):
    program_list_version = ProgramListVersionKeyBit()
    allowed_programs = AllowedProgramsKeyBit()
