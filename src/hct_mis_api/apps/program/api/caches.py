from typing import Any, Optional

from django.db.models import QuerySet

from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.bits import KeyBitBase
from rest_framework_extensions.key_constructor.constructors import KeyConstructor

from hct_mis_api.api.caches import (
    BusinessAreaAndProgramLastUpdatedKeyBit,
    KeyConstructorMixin,
    get_or_create_cache_key,
)
from hct_mis_api.apps.program.models import ProgramCycle


class ProgramCycleListVersionsKeyBit(BusinessAreaAndProgramLastUpdatedKeyBit):
    specific_view_cache_key = "program_cycle_list"

    def _get_queryset(self, business_area_slug: Optional[Any], program_slug: Optional[Any]) -> QuerySet:
        return ProgramCycle.objects.filter(
            program__slug=program_slug,
            program__business_area__slug=business_area_slug,
        )


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
