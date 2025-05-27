from typing import Any

from rest_framework_extensions.key_constructor.bits import KeyBitBase

from hct_mis_api.api.caches import (BusinessAreaAndProgramLastUpdatedKeyBit,
                                    BusinessAreaKeyBitMixin,
                                    KeyConstructorMixin)
from hct_mis_api.apps.core.models import BusinessArea


class ManagerialPaymentPlanListVersionsKeyBit(BusinessAreaKeyBitMixin):
    specific_view_cache_key = "management_payment_plans_list"


class PaymentPlanListKeyBit(BusinessAreaAndProgramLastUpdatedKeyBit):
    specific_view_cache_key = "payment_plans_list"


class PaymentVerificationListKeyBit(BusinessAreaAndProgramLastUpdatedKeyBit):
    specific_view_cache_key = "payment_verifications_list"


class TargetPopulationListKeyBit(BusinessAreaAndProgramLastUpdatedKeyBit):
    specific_view_cache_key = "target_populations_list"


class PaymentPlanProgramsPermissionsKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        business_area = BusinessArea.objects.get(slug=kwargs.get("business_area_slug"))
        program_ids = request.user.get_program_ids_for_permissions_in_business_area(
            str(business_area.id),
            view_instance.PERMISSIONS,
        )
        program_ids.sort()
        return str(program_ids)


class PaymentPlanKeyConstructor(KeyConstructorMixin):
    managerial_payment_plan_list_version = ManagerialPaymentPlanListVersionsKeyBit()
    permissions_to_programs = PaymentPlanProgramsPermissionsKeyBit()


class PaymentPlanListKeyConstructor(KeyConstructorMixin):
    payment_plan_list = PaymentPlanListKeyBit()


class TargetPopulationListKeyConstructor(KeyConstructorMixin):
    target_population_list = TargetPopulationListKeyBit()


class PaymentVerificationListKeyConstructor(KeyConstructorMixin):
    payment_verification_list = PaymentVerificationListKeyBit()
