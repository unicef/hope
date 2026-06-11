from django.urls import path

from hope.contrib.vision.views import PaymentPlanCallbackView

app_name = "vision"

urlpatterns = [
    path(
        "payment-plan-callback/",
        PaymentPlanCallbackView.as_view(),
        name="payment-plan-callback",
    ),
]
