from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Exists, OuterRef, QuerySet
from django.utils.translation import gettext_lazy as _

from hope.models.payment_plan import PaymentPlan
from hope.models.utils import LongNameIndex, TimeStampedUUIDModel, UnicefIdentifiedModel

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
        indexes = [
            LongNameIndex(fields=["created_at"], name="payment_paymentplanpurpose_created_at_d7aea5fa"),
            LongNameIndex(fields=["updated_at"], name="payment_paymentplanpurpose_updated_at_8d7cd301"),
            LongNameIndex(fields=["unicef_id"], name="payment_paymentplanpurpose_unicef_id_62d4c073"),
            LongNameIndex(
                fields=["unicef_id"],
                opclasses=["varchar_pattern_ops"],
                name="payment_paymentplanpurpose_unicef_id_62d4c073_like",
            ),
        ]

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
