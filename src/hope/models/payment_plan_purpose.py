from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Exists, OuterRef, QuerySet
from django.utils.translation import gettext_lazy as _

from hope.models.payment_plan import PaymentPlan
from hope.models.utils import TimeStampedUUIDModel, UnicefIdentifiedModel

if TYPE_CHECKING:
    from hope.models.program import Program


class PaymentPlanPurpose(TimeStampedUUIDModel, UnicefIdentifiedModel):
    business_area = models.ForeignKey(
        "core.BusinessArea", on_delete=models.CASCADE, related_name="payment_plan_purposes"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        app_label = "core"
        verbose_name = _("Payment Plan Purpose")
        constraints = [
            models.UniqueConstraint(
                fields=["name", "business_area"],
                name="unique_paymentplanpurpose_name_business_area",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.business_area})"

    @staticmethod
    def annotate_usage_in_program(
        qs: QuerySet["PaymentPlanPurpose"], program: "Program"
    ) -> QuerySet["PaymentPlanPurpose"]:
        return qs.annotate(
            is_used_in_pp=Exists(
                PaymentPlan.objects.filter(
                    program_cycle__program=program,
                    payment_plan_purposes=OuterRef("pk"),
                )
            )
        )
