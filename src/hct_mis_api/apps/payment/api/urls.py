from django.urls import include, path

from hct_mis_api.apps.core.api.urls import get_business_area_nested_router
from hct_mis_api.apps.payment.api.views import (
    PaymentPlanManagerialViewSet,
    PaymentPlanSupportingDocumentViewSet,
)
from hct_mis_api.apps.program.api.urls import get_program_nested_router

app_name = "payment"

business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register(
    r"payments/payment-plans-managerial", PaymentPlanManagerialViewSet, basename="payment-plans-managerial"
)
program_nested_router = get_program_nested_router()
program_nested_router.register(
    "payment-plans/<str:payment_plan_id>/supporting-documents",
    PaymentPlanSupportingDocumentViewSet,
    basename="supporting_documents",
)

urlpatterns = [
    path("", include(business_area_nested_router.urls)),
    path("", include(program_nested_router.urls)),
]
