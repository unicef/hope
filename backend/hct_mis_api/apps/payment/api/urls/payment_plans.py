from django.urls import path

from hct_mis_api.apps.payment.api.views import (
    PaymentPlanSupportingDocumentUploadView,
    PaymentPlanSupportingDocumentView,
)

app_name = "payment_plan"

urlpatterns = [
    path(
        "supporting-documents-upload/",
        PaymentPlanSupportingDocumentUploadView.as_view(),
        name="supporting_documents_upload",
    ),
    path(
        "supporting-documents/<int:file_id>/", PaymentPlanSupportingDocumentView.as_view(), name="supporting_documents"
    ),
]
