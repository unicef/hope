from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from utils.models import TimeStampedUUIDModel


class RegistrationDataImport(TimeStampedUUIDModel):
    STATUS_CHOICE = (
        ("IN_REVIEW", _("In Review")),
        ("APPROVED", _("Approved")),
        ("MERGED", _("Merged")),
        ("MERGING", _("Merging")),
        ("IMPORTING", _("Importing")),
    )
    DATA_SOURCE_CHOICE = (
        ("XLS", "Excel"),
        ("3RD_PARTY", "3rd party"),
        ("XML", "XML"),
        ("OTHER", "Other"),
    )
    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=255, choices=STATUS_CHOICE, default="IN_REVIEW",
    )
    import_date = models.DateTimeField(auto_now_add=True)
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="registration_data_imports",
        on_delete=models.CASCADE,
    )
    data_source = models.CharField(max_length=255, choices=DATA_SOURCE_CHOICE,)
    number_of_individuals = models.PositiveIntegerField()
    number_of_households = models.PositiveIntegerField()
    datahub_id = models.UUIDField(null=True, default=None)

    business_area = models.ForeignKey(
        "core.BusinessArea", null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
