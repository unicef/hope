from django.urls import include, path

from hct_mis_api.apps.payment.api.views import PaymentPlanSupportingDocumentViewSet
from hct_mis_api.apps.program.api.urls import get_program_nested_router

app_name = "payment_plan"

program_nested_router = get_program_nested_router()
program_nested_router.register(
    "payment-plans/<str:payment_plan_id>/supporting-documents",
    PaymentPlanSupportingDocumentViewSet,
    basename="supporting_documents",
)

urlpatterns = [
    path("", include(program_nested_router.urls)),
]
