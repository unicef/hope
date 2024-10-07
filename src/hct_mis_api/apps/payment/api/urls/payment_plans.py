from django.urls import include, path

from rest_framework.routers import DefaultRouter

from hct_mis_api.apps.payment.api.views import PaymentPlanSupportingDocumentViewSet

app_name = "payment_plan"

router = DefaultRouter()
router.register("supporting-documents", PaymentPlanSupportingDocumentViewSet, basename="supporting_documents")

urlpatterns = [
    path("", include(router.urls)),
]
