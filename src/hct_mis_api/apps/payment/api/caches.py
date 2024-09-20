from typing import Any

from rest_framework_extensions.key_constructor.bits import KeyBitBase

from hct_mis_api.api.caches import BusinessAreaKeyBit, KeyConstructorMixin
from hct_mis_api.apps.core.models import BusinessArea


class ManagerialPaymentPlanListVersionsKeyBit(BusinessAreaKeyBit):
    specific_view_cache_key = "management_payment_plans_list"


class PaymentPlanProgramsPermissionsKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        business_area = BusinessArea.objects.get(slug=kwargs.get("business_area"))
        program_ids = request.user.partner.get_program_ids_for_business_area(str(business_area.id))
        program_ids.sort()
        return str(program_ids)


class PaymentPlanKeyConstructor(KeyConstructorMixin):
    managerial_payment_plan_list_versions = ManagerialPaymentPlanListVersionsKeyBit()
    permissions_to_programs = PaymentPlanProgramsPermissionsKeyBit()
