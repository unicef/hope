from typing import Any

from django.db import transaction
from rest_framework_extensions.key_constructor.bits import KeyBitBase

from hope.api.caches import (
    BusinessAreaAndProgramKeyBitMixin,
    BusinessAreaKeyBitMixin,
    KeyConstructorMixin,
    get_or_create_cache_key,
    increment_business_area_and_program_version,
)
from hope.models import BusinessArea

PAYMENT_PLAN_LIST_CACHE_KEYS = (
    "payment_plans_list",
    "target_populations_list",
    "payment_verifications_list",
)
PAYMENT_VERIFICATION_LIST_CACHE_KEYS = ("payment_verifications_list",)


def invalidate_payment_plan_list_cache(
    business_area_slug: Any,
    program_code: Any,
    specific_view_cache_keys: tuple[str, ...] = PAYMENT_PLAN_LIST_CACHE_KEYS,
) -> None:
    """Invalidate the payment plan list caches for a program."""

    def _increment() -> None:
        for specific_view_cache_key in specific_view_cache_keys:
            increment_business_area_and_program_version(business_area_slug, program_code, specific_view_cache_key)

    transaction.on_commit(_increment)


class ManagerialPaymentPlanListVersionsKeyBit(BusinessAreaKeyBitMixin):
    specific_view_cache_key = "management_payment_plans_list"


class PaymentPlanListKeyBit(BusinessAreaAndProgramKeyBitMixin):
    specific_view_cache_key = "payment_plans_list"


class PaymentPlanGroupListKeyBit(BusinessAreaAndProgramKeyBitMixin):
    specific_view_cache_key = "payment_plan_groups_list"


class PaymentPlanPurposeListVersionsKeyBit(KeyBitBase):
    def get_data(  # noqa: PLR0913 – override of base method signature
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Any,
        args: tuple,
        kwargs: dict,
    ) -> str:
        version = get_or_create_cache_key("payment_plan_purposes_list", 1)
        return str(version)


class PaymentVerificationListKeyBit(BusinessAreaAndProgramKeyBitMixin):
    specific_view_cache_key = "payment_verifications_list"


class TargetPopulationListKeyBit(BusinessAreaAndProgramKeyBitMixin):
    specific_view_cache_key = "target_populations_list"


class PaymentPlanProgramsPermissionsKeyBit(KeyBitBase):
    def get_data(  # noqa: PLR0913 – override of base method signature
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Any,
        args: tuple,
        kwargs: dict,
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


class PaymentPlanGroupListKeyConstructor(KeyConstructorMixin):
    payment_plan_group_list = PaymentPlanGroupListKeyBit()


class PaymentPlanPurposeListKeyConstructor(KeyConstructorMixin):
    payment_plan_purpose_list = PaymentPlanPurposeListVersionsKeyBit()


class PaymentVerificationListKeyConstructor(KeyConstructorMixin):
    payment_verification_list = PaymentVerificationListKeyBit()
