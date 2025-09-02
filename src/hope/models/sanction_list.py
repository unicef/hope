from typing import TYPE_CHECKING

from django.db import models
from strategy_field.fields import StrategyField

from hope.apps.sanction_list.strategies import registry
from hope.models.utils import TimeStampedModel, TimeStampedUUIDModel

if TYPE_CHECKING:
    from hope.apps.sanction_list.strategies._base import BaseSanctionList


class SanctionList(TimeStampedModel):
    strategy: "BaseSanctionList"
    name = models.CharField(max_length=255)
    config = models.JSONField(default=dict, blank=True)
    strategy = StrategyField(registry=registry, unique=True)

    class Meta:
        app_label = "sanction_list"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def refresh(self) -> None:
        self.strategy.refresh()


class UploadedXLSXFile(TimeStampedUUIDModel):
    selected_lists = models.ManyToManyField(SanctionList)
    file = models.FileField()
    associated_email = models.EmailField()

    class Meta:
        app_label = "sanction_list"
