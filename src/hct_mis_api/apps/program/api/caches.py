from typing import Any

from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.bits import KeyBitBase
from rest_framework_extensions.key_constructor.constructors import KeyConstructor

from hct_mis_api.api.caches import KeyConstructorMixin, get_or_create_cache_key
from hct_mis_api.apps.program.models import ProgramCycle


class ProgramCycleListVersionsKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        program_slug = kwargs.get("program_slug")
        business_area_slug = kwargs.get("business_area_slug")
        program_cycle_qs = ProgramCycle.objects.filter(
            program__slug=program_slug,
            program__business_area__slug=business_area_slug,
        )
        program_cycle_updated_at = program_cycle_qs.latest("updated_at").updated_at
        program_cycle_count = program_cycle_qs.count()

        business_area_slug = kwargs.get("business_area_slug")
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)

        version_key = (
            f"{business_area_slug}:{business_area_version}:{program_slug}:program_cycle_list:"
            f"{program_cycle_updated_at}:{program_cycle_count}"
        )
        return str(version_key)


class ProgramCycleKeyConstructor(KeyConstructorMixin):
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
