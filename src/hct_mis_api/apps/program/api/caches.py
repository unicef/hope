from typing import Any

from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.bits import KeyBitBase
from rest_framework_extensions.key_constructor.constructors import KeyConstructor

from hct_mis_api.api.caches import (
    KeyConstructorMixin,
    ProgramKeyBit,
    get_or_create_cache_key,
)
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.program.models import ProgramCycle


class ProgramCycleListVersionsKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        program_id = decode_id_string(kwargs.get("program_id"))
        program_cycle_qs = ProgramCycle.objects.filter(program_id=program_id)
        program_cycle_updated_at = program_cycle_qs.latest("updated_at").updated_at
        program_cycle_count = program_cycle_qs.count()

        version_key = f"{program_id}:{program_cycle_updated_at}:{program_cycle_count}"
        return str(version_key)


class ProgramCycleKeyConstructor(KeyConstructorMixin):
    program_id_version = ProgramKeyBit()
    program_cycle_list_versions = ProgramCycleListVersionsKeyBit()


class BeneficiaryGroupListVersionsKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        version = get_or_create_cache_key("beneficiary_group_list", 1)
        return str(version)


class BeneficiaryGroupKeyConstructor(KeyConstructor):
    beneficiary_group_list_versions = BeneficiaryGroupListVersionsKeyBit()
    unique_method_id = bits.UniqueMethodIdKeyBit()
    querystring = bits.QueryParamsKeyBit()
    params = bits.KwargsKeyBit()
    pagination = bits.PaginationKeyBit()
