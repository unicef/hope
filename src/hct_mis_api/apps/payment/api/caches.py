from typing import Any, Optional

from django.db.models import QuerySet

from rest_framework_extensions.key_constructor.bits import KeyBitBase

from hct_mis_api.api.caches import (
    BusinessAreaAndProgramLastUpdatedKeyBit,
    BusinessAreaKeyBitMixin,
    KeyConstructorMixin,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import PaymentPlan


class ManagerialPaymentPlanListVersionsKeyBit(BusinessAreaKeyBitMixin):
    specific_view_cache_key = "management_payment_plans_list"


class PaymentPlanListKeyBit(BusinessAreaAndProgramLastUpdatedKeyBit):
    specific_view_cache_key = "payment_plan_list"

    def _get_queryset(self, business_area_slug: Optional[Any], program_slug: Optional[Any]) -> QuerySet:
        return PaymentPlan.objects.exclude(status__in=PaymentPlan.PRE_PAYMENT_PLAN_STATUSES).filter(
            program_cycle__program__slug=program_slug,
            business_area__slug=business_area_slug,
        )


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
    managerial_payment_plan_list_versions = ManagerialPaymentPlanListVersionsKeyBit()
    permissions_to_programs = PaymentPlanProgramsPermissionsKeyBit()
    payment_plan_list = PaymentPlanListKeyBit()
