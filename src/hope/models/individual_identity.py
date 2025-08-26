from django.db import models
from model_utils.models import TimeStampedModel

from hope.models.utils import SoftDeletableMergeStatusModel, PendingManager


class IndividualIdentity(SoftDeletableMergeStatusModel, TimeStampedModel):
    individual = models.ForeignKey("models.individual.Individual", related_name="identities", on_delete=models.CASCADE)
    partner = models.ForeignKey(
        "account.Partner",
        related_name="individual_identities",
        null=True,
        on_delete=models.PROTECT,
    )
    country = models.ForeignKey("geo.Country", null=True, on_delete=models.PROTECT)
    number = models.CharField(max_length=255)
    copied_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="copied_to",
        help_text="If this object was copied from another, this field will contain the object it was copied from.",
    )

    class Meta:
        app_label = "household"
        verbose_name_plural = "Individual Identities"

    def __str__(self) -> str:
        return f"{self.partner} {self.individual} {self.number}"


class PendingIndividualIdentity(IndividualIdentity):
    objects = PendingManager()

    class Meta:
        proxy = True
        verbose_name = "Imported Individual Identity"
        verbose_name_plural = "Imported Individual Identities"
