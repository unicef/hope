import logging

from django.contrib.postgres.fields import IntegerRangeField
from django.contrib.postgres.validators import RangeMinValueValidator
from django.db import models
from psycopg2._range import NumericRange

from hope.models.utils import TimeStampedUUIDModel

logger = logging.getLogger(__name__)


class AcceptanceProcessThreshold(TimeStampedUUIDModel):
    business_area = models.ForeignKey(
        "core.BusinessArea",
        on_delete=models.PROTECT,
        related_name="acceptance_process_thresholds",
    )
    payments_range_usd = IntegerRangeField(
        default=NumericRange(0, None),
        validators=[
            RangeMinValueValidator(0),
        ],
    )
    approval_number_required = models.PositiveIntegerField(default=1)
    authorization_number_required = models.PositiveIntegerField(default=1)
    finance_release_number_required = models.PositiveIntegerField(default=1)

    class Meta:
        app_label = "payment"
        ordering = ("payments_range_usd",)

    def __str__(self) -> str:
        return (
            f"{self.payments_range_usd} USD, "
            f"Approvals: {self.approval_number_required} "
            f"Authorization: {self.authorization_number_required} "
            f"Finance Releases: {self.finance_release_number_required}"
        )
