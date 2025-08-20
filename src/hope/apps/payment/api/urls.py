from django.urls import include, path
from rest_framework_nested.routers import NestedSimpleRouter

from hope.apps.core.api.urls import get_business_area_nested_router
from hope.apps.payment.api.views import (
    PaymentGlobalViewSet,
    PaymentPlanManagerialViewSet,
    PaymentPlanSupportingDocumentViewSet,
    PaymentPlanViewSet,
    PaymentVerificationRecordViewSet,
    PaymentVerificationViewSet,
    PaymentViewSet,
    TargetPopulationViewSet,
    available_fsps_for_delivery_mechanisms,
)
from hope.apps.program.api.urls import program_base_router

app_name = "payment"

business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register(
    r"payments/payment-plans-managerial",
    PaymentPlanManagerialViewSet,
    basename="payment-plans-managerial",
)
business_area_nested_router.register(r"payments", PaymentGlobalViewSet, basename="payments-global")

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
    r"payment-plans/(?P<payment_plan_id>[^/.]+)/payments",
    PaymentViewSet,
    basename="payments",
)
program_nested_router.register(
    "payment-verifications",
    PaymentVerificationViewSet,
    basename="payment-verifications",
)
payment_verification_nested_router = NestedSimpleRouter(
    program_nested_router,
    r"payment-verifications",
    lookup="payment_verification",
)
payment_verification_nested_router.register(
    r"verifications",
    PaymentVerificationRecordViewSet,
    basename="verification-records",
)

urlpatterns = [
    path(
        "business-areas/<slug:business_area_slug>/available-fsps-for-delivery-mechanisms/",
        available_fsps_for_delivery_mechanisms,
        name="available-fsps",
    ),
    path("", include(business_area_nested_router.urls)),
    path("", include(program_nested_router.urls)),
    path("", include(payment_verification_nested_router.urls)),
]
