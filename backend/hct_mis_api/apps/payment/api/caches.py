from typing import Any

from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.bits import KeyBitBase
from rest_framework_extensions.key_constructor.constructors import KeyConstructor

from hct_mis_api.api.caches import ModelVersionKeyBitMixin
from hct_mis_api.apps.core.models import BusinessArea


class PaymentPlanProgramVersionsKeyBit(ModelVersionKeyBitMixin, KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        business_area = BusinessArea.objects.get(slug=kwargs.get("business_area"))
        program_ids = request.user.partner.get_program_ids_for_business_area(str(business_area.id))
        program_ids.sort()
        program_ids_with_versions = {}
        for program_id in program_ids:
            program_id = str(program_id)
            program_ids_with_versions[program_id] = self.get_value_for_key(
                f"payment_plan_version_for_program_{program_id}"
            )
        return str(program_ids_with_versions)


class PaymentPlanKeyConstructor(KeyConstructor):
    unique_method_id = bits.UniqueMethodIdKeyBit()
    format = bits.FormatKeyBit()
    payment_plan_program_versions = PaymentPlanProgramVersionsKeyBit()
    querystring = bits.QueryParamsKeyBit()
    params = bits.KwargsKeyBit()
    pagination = bits.PaginationKeyBit()
