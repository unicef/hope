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
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    limit_to = models.ManyToManyField(
        to="core.BusinessArea",
        related_name="payment_plan_purposes",
        blank=True,
    )

    class Meta:
        app_label = "payment"
        verbose_name = _("Payment Plan Purpose")

    def __str__(self) -> str:
        return self.name

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
