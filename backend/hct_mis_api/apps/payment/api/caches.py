from typing import Any

from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.bits import KeyBitBase
from rest_framework_extensions.key_constructor.constructors import KeyConstructor

from hct_mis_api.api.caches import BusinessAreaVersionKeyBit, get_or_create_cache_key
from hct_mis_api.apps.core.models import BusinessArea


class ManagerialPaymentPlanListVersionsKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        business_area_slug = kwargs.get("business_area")
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)

        version_key = f"{business_area_slug}:{business_area_version}:management_payment_plans_list"
        version = get_or_create_cache_key(version_key, 1)
        return str(version)


class PaymentPlanProgramsPermissionsKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        business_area = BusinessArea.objects.get(slug=kwargs.get("business_area"))
        program_ids = request.user.partner.get_program_ids_for_business_area(str(business_area.id))
        program_ids.sort()
        return str(program_ids)


class PaymentPlanKeyConstructor(KeyConstructor):
    unique_method_id = bits.UniqueMethodIdKeyBit()
    managerial_payment_plan_list_versions = ManagerialPaymentPlanListVersionsKeyBit()
    permissions_to_programs = PaymentPlanProgramsPermissionsKeyBit()
    business_area_version = BusinessAreaVersionKeyBit()
    querystring = bits.QueryParamsKeyBit()
    params = bits.KwargsKeyBit()
    pagination = bits.PaginationKeyBit()
