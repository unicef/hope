from django.db import models

from hope.models.utils import TimeStampedUUIDModel


class PayeeType(TimeStampedUUIDModel):
    name = models.CharField(max_length=255, unique=True)
    gl_code = models.CharField(max_length=32, blank=True, help_text="General Ledger code shown on the Program")
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True, help_text="Inactive Payee Types cannot be used in new programs")
    weight = models.PositiveSmallIntegerField(
        default=0, help_text="Ordering weight: types with a higher weight are listed first"
    )
    default_data_collecting_type = models.ForeignKey(
        "core.DataCollectingType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text="Data Collecting Type preselected when this Payee Type is chosen",
    )

    class Meta:
        app_label = "core"
        verbose_name = "Payee Type"
        verbose_name_plural = "Payee Types"
        ordering = ("-weight", "name")

    def __str__(self) -> str:
        return self.name
