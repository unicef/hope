from django.urls import include, path

from rest_framework.routers import SimpleRouter

from hct_mis_api.apps.core.api.urls import get_business_area_nested_router
from hct_mis_api.apps.payment.api.views import PaymentPlanManagerialViewSet
from hct_mis_api.apps.program.api.views import BeneficiaryGroupViewSet

app_name = "payment"


router = SimpleRouter()
router.register(r"beneficiary-groups", BeneficiaryGroupViewSet, basename="beneficiary-groups")

business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register(
    r"payments/payment-plans-managerial", PaymentPlanManagerialViewSet, basename="payment-plans-managerial"
)

urlpatterns = [
    path("", include(business_area_nested_router.urls)),
    path("", include(router.urls)),
]
