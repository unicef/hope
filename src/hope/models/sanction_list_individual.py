from typing import Any

from django.db import models

from hope.models.sanction_list import SanctionList
from hope.models.utils import TimeStampedUUIDModel


class SanctionListIndividualQuerySet(models.QuerySet):
    def delete(self) -> tuple[int, dict[str, int]]:
        return (super().update(active=False), {})

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        return super().delete()

    def active(self) -> models.QuerySet:
        return self.filter(active=True)

    def inactive(self) -> models.QuerySet:
        return self.exclude(active=False)


class ActiveIndividualsManager(models.Manager):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.alive_only = kwargs.pop("active_only", True)
        super().__init__(*args, **kwargs)

    def get_queryset(self) -> models.QuerySet:
        if self.alive_only:
            return SanctionListIndividualQuerySet(self.model).active()
        return SanctionListIndividualQuerySet(self.model)

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        return self.get_queryset().hard_delete()


class SanctionListIndividual(TimeStampedUUIDModel):
    first_name = models.CharField(max_length=85)
    second_name = models.CharField(max_length=85, blank=True, default="")
    third_name = models.CharField(max_length=85, blank=True, default="")
    fourth_name = models.CharField(max_length=85, blank=True, default="")
    full_name = models.CharField(max_length=255)
    name_original_script = models.CharField(max_length=255, blank=True, default="")
    list_type = models.CharField(max_length=50)
    un_list_type = models.CharField(max_length=100, blank=True, default="")
    reference_number = models.CharField(max_length=50)
    listed_on = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True, default="")
    designation = models.TextField(blank=True, default="")
    street = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=255, blank=True, default="")
    state_province = models.CharField(max_length=255, blank=True, default="")
    address_note = models.CharField(max_length=255, blank=True, default="")
    data_id = models.PositiveIntegerField()
    version_num = models.PositiveIntegerField()
    country_of_birth = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)

    sanction_list = models.ForeignKey(SanctionList, on_delete=models.CASCADE, related_name="entries")
    objects = ActiveIndividualsManager()
    all_objects = ActiveIndividualsManager(active_only=False)

    class Meta:
        app_label = "sanction_list"
        ordering = ["-listed_on"]
        verbose_name = "Individual"
        verbose_name_plural = "Individuals"
        unique_together = ("sanction_list", "reference_number")

    def __str__(self) -> str:
        return self.full_name
