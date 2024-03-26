from django.urls import include, path

from rest_framework.routers import SimpleRouter

from hct_mis_api.apps.payment.api.views import (
    PaymentPlanManagerialViewSet,
    PaymentPlanViewSet,
)

app_name = "payment"

program_unrelated_router = SimpleRouter()
program_unrelated_router.register(
    "payment-plans-managerial",
    PaymentPlanManagerialViewSet,
    basename="payment-plans-managerial",
)

program_related_router = SimpleRouter()
program_related_router.register(
    "payment-plans",
    PaymentPlanViewSet,
    basename="payment-plans",
)

urlpatterns = [
    path("", include(program_unrelated_router.urls)),
    path("programs/<str:program_id>/", include(program_related_router.urls)),
]
