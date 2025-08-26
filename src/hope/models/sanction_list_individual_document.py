from django.db import models

from hope.models.utils import TimeStampedUUIDModel


class SanctionListIndividualDocument(TimeStampedUUIDModel):
    individual = models.ForeignKey(
        "models.sanction_list_individual.SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    type_of_document = models.CharField(max_length=255)
    document_number = models.CharField(max_length=255)
    date_of_issue = models.CharField(max_length=255, blank=True, null=True, default="")
    issuing_country = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    note = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        app_label = "sanction_list"
        verbose_name = "Document"
        verbose_name_plural = "Documents"
