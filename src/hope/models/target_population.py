from typing import TYPE_CHECKING

from hope.models.payment_list import PaymentList
from hope.models.utils import SoftDeletableManager

if TYPE_CHECKING:
    from django.db.models import QuerySet


class TargetPopulationManager(SoftDeletableManager["TargetPopulation"]):
    def get_queryset(self) -> "QuerySet[TargetPopulation]":
        return super().get_queryset().filter(status__in=PaymentList.PRE_PAYMENT_LIST_STATUSES)


class TargetPopulation(PaymentList):
    objects: TargetPopulationManager = TargetPopulationManager()  # type: ignore[assignment]

    class Meta:
        app_label = "payment"
        proxy = True
        verbose_name = "Target Population"
        verbose_name_plural = "Target Populations"
