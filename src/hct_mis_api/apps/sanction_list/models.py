from typing import Any, Dict, Tuple

from django.db import models

from strategy_field.fields import StrategyField

from hct_mis_api.apps.utils.models import TimeStampedUUIDModel

from .strategies import registry


class SanctionListIndividualQuerySet(models.QuerySet):
    def delete(self) -> Tuple[int, Dict[str, int]]:
        return (super().update(active=False), {})

    def hard_delete(self) -> Tuple[int, Dict[str, int]]:
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

    def hard_delete(self) -> Tuple[int, Dict[str, int]]:
        return self.get_queryset().hard_delete()


class SanctionList(TimeStampedUUIDModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    config = models.JSONField(default=dict)
    strategy = StrategyField(registry=registry, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class SanctionListIndividual(TimeStampedUUIDModel):
    first_name = models.CharField(max_length=85)
    second_name = models.CharField(max_length=85, blank=True, default="")
    third_name = models.CharField(max_length=85, blank=True, default="")
    fourth_name = models.CharField(max_length=85, blank=True, default="")
    full_name = models.CharField(max_length=255)
    name_original_script = models.CharField(max_length=255, blank=True, default="")
    list_type = models.CharField(max_length=50)
    un_list_type = models.CharField(max_length=100, blank=True, default="")
    reference_number = models.CharField(max_length=50, unique=True)
    listed_on = models.DateTimeField()
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

    sanction_list = models.ForeignKey(SanctionList, on_delete=models.CASCADE)
    objects = ActiveIndividualsManager()
    all_objects = ActiveIndividualsManager(active_only=False)

    class Meta:
        ordering = ["-listed_on"]
        verbose_name = "Individual"
        verbose_name_plural = "Individuals"


class SanctionListIndividualDocument(TimeStampedUUIDModel):
    individual = models.ForeignKey(
        "SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    type_of_document = models.CharField(max_length=255)
    document_number = models.CharField(max_length=255)
    date_of_issue = models.CharField(max_length=255, blank=True, null=True, default="")
    issuing_country = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    note = models.CharField(max_length=255, blank=True, default="")


class SanctionListIndividualNationalities(TimeStampedUUIDModel):
    nationality = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    individual = models.ForeignKey(
        "SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="nationalities",
    )


class SanctionListIndividualCountries(TimeStampedUUIDModel):
    country = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    individual = models.ForeignKey(
        "SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="countries",
    )


class SanctionListIndividualAliasName(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    individual = models.ForeignKey(
        "SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="alias_names",
    )


class SanctionListIndividualDateOfBirth(TimeStampedUUIDModel):
    date = models.DateField()
    individual = models.ForeignKey(
        "SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="dates_of_birth",
    )


class UploadedXLSXFile(TimeStampedUUIDModel):
    file = models.FileField()
    associated_email = models.EmailField()
