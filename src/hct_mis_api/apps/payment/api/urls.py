from django.urls import include, path

from hct_mis_api.apps.core.api.urls import get_business_area_nested_router
from hct_mis_api.apps.payment.api.views import (
    PaymentPlanManagerialViewSet,
    PaymentPlanSupportingDocumentViewSet,
    PaymentPlanViewSet,
    PaymentVerificationViewSet,
    PaymentViewSet,
    TargetPopulationViewSet,
    TPHouseholdViewSet,
)
from hct_mis_api.apps.program.api.urls import program_base_router

app_name = "payment"

business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register(
    r"payments/payment-plans-managerial", PaymentPlanManagerialViewSet, basename="payment-plans-managerial"
)
program_nested_router = program_base_router.program_nested_router
program_nested_router.register(
    "payment-plans/(?P<payment_plan_id>[^/.]+)/supporting-documents",
    PaymentPlanSupportingDocumentViewSet,
    basename="supporting-documents",
)
program_nested_router.register(
    "payment-plans",
    PaymentPlanViewSet,
    basename="payment-plans",
)
program_nested_router.register(
    "target-populations",
    TargetPopulationViewSet,
    basename="target-populations",
)
program_nested_router.register(
    r"target-populations/(?P<target_population_id>[^/.]+)/households",
    TPHouseholdViewSet,
    basename="tp-households",
)
program_nested_router.register(
    r"payment-plans/(?P<payment_plan_id>[^/.]+)/payments",
    PaymentViewSet,
    basename="payments",
)
program_nested_router.register(
    "payment-verifications",
    PaymentVerificationViewSet,
    basename="payment-verifications",
)
# program_nested_router.register(
#     r"payment-verifications/(?P<payment_plan_id>[^/.]+)/verifications",
#     VerificationViewSet,
#     basename="verifications",
# )

urlpatterns = [
    path("", include(business_area_nested_router.urls)),
    path("", include(program_nested_router.urls)),
]
