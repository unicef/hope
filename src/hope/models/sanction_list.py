from typing import TYPE_CHECKING

from django.db import models
from strategy_field.fields import StrategyField

from hope.apps.sanction_list.strategies import registry
from hope.models.utils import TimeStampedModel, TimeStampedUUIDModel, UniqueUploadPath

if TYPE_CHECKING:
    from hope.apps.sanction_list.strategies._base import BaseSanctionList


class SanctionList(TimeStampedModel):
    name = models.CharField(max_length=255)
    config = models.JSONField(default=dict, blank=True)
    strategy: "BaseSanctionList" = StrategyField(registry=registry, unique=True)

    class Meta:
        app_label = "sanction_list"
        ordering = ["name"]
        permissions = (
            ("refresh_sanction_list", "Can Refresh Sanction List"),
            ("empty_sanction_list", "Can Empty Sanction List"),
        )

    def __str__(self) -> str:
        return self.name

    def refresh(self) -> None:
        self.strategy.refresh()


class UploadedXLSXFile(TimeStampedUUIDModel):
    selected_lists = models.ManyToManyField(SanctionList)
    file = models.FileField(upload_to=UniqueUploadPath("sanction_list_upload"), max_length=255)
    associated_email = models.EmailField()

    class Meta:
        app_label = "sanction_list"
