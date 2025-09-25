from django.conf import settings
from django.db import models

from hope.models.payment_plan import PaymentPlan


class PaymentPlanSupportingDocument(models.Model):
    FILE_LIMIT = 10  # max 10 files per Payment Plan
    FILE_SIZE_LIMIT = 10 * 1024 * 1024  # 10 MB

    title = models.CharField(max_length=255)
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")

    class Meta:
        app_label = "payment"
        ordering = ["uploaded_at"]

    def __str__(self) -> str:
        return self.title
