from django.db import models

from hope.models.household import ROLE_CHOICE
from hope.models.utils import SoftDeletableMergeStatusModel, TimeStampedUUIDModel, AbstractSyncable, PendingManager


class IndividualRoleInHousehold(SoftDeletableMergeStatusModel, TimeStampedUUIDModel, AbstractSyncable):
    individual = models.ForeignKey(
        "household.Individual",
        on_delete=models.CASCADE,
        related_name="households_and_roles",
    )
    household = models.ForeignKey(
        "household.Household",
        on_delete=models.CASCADE,
        related_name="individuals_and_roles",
    )
    role = models.CharField(
        max_length=255,
        blank=True,
        choices=ROLE_CHOICE,
    )
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
        unique_together = [("role", "household"), ("household", "individual")]

    def __str__(self) -> str:
        return f"{self.individual.full_name} - {self.role}"


class PendingIndividualRoleInHousehold(IndividualRoleInHousehold):
    objects = PendingManager()

    class Meta:
        app_label = "household"
        proxy = True
        verbose_name = "Imported Individual Role In Household"
        verbose_name_plural = "Imported Individual Roles In Household"
