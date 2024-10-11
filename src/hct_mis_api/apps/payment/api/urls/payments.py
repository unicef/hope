from django.urls import include, path

from rest_framework.routers import SimpleRouter

from hct_mis_api.apps.payment.api.views import PaymentPlanManagerialViewSet

app_name = "payment"

program_unrelated_router = SimpleRouter()
program_unrelated_router.register(
    "payment-plans-managerial",
    PaymentPlanManagerialViewSet,
    basename="payment-plans-managerial",
)

urlpatterns = [
    path("", include(program_unrelated_router.urls)),
]
