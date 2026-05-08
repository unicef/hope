from django.db import models

from hope.models.file_temp import FileTemp


class WesternUnionData(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_ERROR = "ERROR"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_ERROR, "Error"),
    ]

    name = models.CharField(max_length=255, unique=True)
    date = models.DateField(null=True, blank=True)
    file = models.ForeignKey(
        FileTemp,
        related_name="+",
        help_text="WU QCF File",
        on_delete=models.DO_NOTHING,
        null=True,
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    error_msg = models.TextField(null=True, blank=True)

    class Meta:
        app_label = "payment"
        verbose_name = "Western Union Data"
        verbose_name_plural = "Western Union Data"
        ordering = ("id",)

    def __str__(self) -> str:
        return self.name
