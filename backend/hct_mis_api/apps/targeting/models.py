from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import UUIDModel


class TargetPopulation(UUIDModel):
    STATUS_CHOICE = (
        ("IN_PROGRESS", _("In progress")),
        ("FINALIZED", _("Finalized")),
    )

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="target_populations",
        null=True,
    )
    rules = JSONField()
    households = models.ManyToManyField(
        "household.Household", related_name="target_populations"
    )
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICE, default=STATUS_CHOICE[0][0],
    )

    def __str__(self):
        return self.name
