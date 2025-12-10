from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from hope.models.approval_process import ApprovalProcess
from hope.models.utils import TimeStampedUUIDModel


class Approval(TimeStampedUUIDModel):
    APPROVAL = "APPROVAL"
    AUTHORIZATION = "AUTHORIZATION"
    FINANCE_RELEASE = "FINANCE_RELEASE"
    REJECT = "REJECT"
    TYPE_CHOICES = (
        (APPROVAL, "Approval"),
        (AUTHORIZATION, "Authorization"),
        (FINANCE_RELEASE, "Finance Release"),
        (REJECT, "Reject"),
    )

    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        default=APPROVAL,
        verbose_name=_("Approval type"),
    )
    comment = models.CharField(max_length=500, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    approval_process = models.ForeignKey(ApprovalProcess, on_delete=models.CASCADE, related_name="approvals")

    class Meta:
        app_label = "payment"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.type or ""  # pragma: no cover

    @property
    def info(self) -> str:
        types_map = {
            self.APPROVAL: "Approved",
            self.AUTHORIZATION: "Authorized",
            self.FINANCE_RELEASE: "Released",
            self.REJECT: "Rejected",
        }

        return f"{types_map.get(self.type)} by {self.created_by}" if self.created_by else types_map.get(self.type, "")
