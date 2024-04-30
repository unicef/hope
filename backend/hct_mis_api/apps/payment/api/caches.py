from typing import Any

from django.core.cache import cache
# from django_redis import get_redis_connection
from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.bits import KeyBitBase
from rest_framework_extensions.key_constructor.constructors import KeyConstructor

from hct_mis_api.apps.core.models import BusinessArea

# redis_connection = get_redis_connection()


class ManagerialPaymentPlanListVersionsKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        business_area_slug = kwargs.get("business_area")
        version = cache.get(f"{business_area_slug}:management_payment_plans_list")
        # version = redis_connection.hget(business_area_slug, "management_payment_plans_list")
        if not version:
            version = cache.incr(f"{business_area_slug}:management_payment_plans_list")
            # redis_connection.hset(business_area_slug, "management_payment_plans_list", 1)
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
    querystring = bits.QueryParamsKeyBit()
    params = bits.KwargsKeyBit()
    pagination = bits.PaginationKeyBit()

    def prepare_key(self, key_dict):
        """
        Override default implementation just so the key is more readable
        """
        key = super().prepare_key(key_dict)
        return f"{key_dict['params']['business_area']}:{key}"
