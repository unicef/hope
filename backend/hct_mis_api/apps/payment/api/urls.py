from django.urls import include, path

from rest_framework.routers import SimpleRouter

from hct_mis_api.apps.payment.api.views import (
    PaymentPlanViewSet,
    PaymentVerificationListView,
)

app_name = "payment"

router = SimpleRouter()
router.register("payment-plans", PaymentPlanViewSet, basename="payment-plan")

urlpatterns = [
    path(
        "payment-verifications/",
        PaymentVerificationListView.as_view({"get": "list"}),
        name="payment-verifications-list",
    ),
    path("", include(router.urls)),
]
