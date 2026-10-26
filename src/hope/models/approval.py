from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from hope.apps.account.actor_snapshot import JobTitleSource, actor_display
from hope.models.approval_process import ApprovalProcess
from hope.models.utils import LongNameIndex, TimeStampedUUIDModel


def get_approval_type_choices() -> tuple:
    return Approval.TYPE_CHOICES


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
        choices=get_approval_type_choices,
        default=APPROVAL,
        verbose_name=_("Approval type"),
    )
    comment = models.CharField(max_length=500, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    # Who signed off, as recorded at the moment
    created_by_name = models.CharField(max_length=301, blank=True, default="")
    created_by_job_title = models.CharField(max_length=255, blank=True, default="")
    created_by_job_title_source = models.CharField(
        max_length=16, blank=True, default="", choices=JobTitleSource.choices
    )
    approval_process = models.ForeignKey(ApprovalProcess, on_delete=models.CASCADE, related_name="approvals")

    class Meta:
        app_label = "payment"
        ordering = ("-created_at",)
        indexes = [
            LongNameIndex(fields=["created_at"], name="payment_approval_created_at_e97382ec"),
            LongNameIndex(fields=["updated_at"], name="payment_approval_updated_at_b0fc5def"),
        ]

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

        label = types_map.get(self.type, "")
        actor = actor_display(self, "created_by")
        return f"{label} by {actor}" if actor else label
