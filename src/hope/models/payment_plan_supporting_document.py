from django.conf import settings
from django.db import models
from django.db.models import Q


class PaymentPlanSupportingDocument(models.Model):
    """A file attached to a Payment Plan Group, or to a Follow-Up Instruction for its plans."""

    FILE_LIMIT = 10  # max 10 files per group or instruction
    FILE_SIZE_LIMIT = 10 * 1024 * 1024  # 10 MB

    title = models.CharField(max_length=255)
    payment_plan_group = models.ForeignKey(
        "payment.PaymentPlanGroup", on_delete=models.CASCADE, null=True, blank=True, related_name="documents"
    )
    follow_up_instruction = models.ForeignKey(
        "payment.FollowUpInstruction", on_delete=models.CASCADE, null=True, blank=True, related_name="documents"
    )
    file = models.FileField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    class Meta:
        app_label = "payment"
        ordering = ["uploaded_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(payment_plan_group__isnull=False, follow_up_instruction__isnull=True)
                | Q(payment_plan_group__isnull=True, follow_up_instruction__isnull=False),
                name="supporting_document_has_one_owner",
            )
        ]

    def __str__(self) -> str:
        return self.title
