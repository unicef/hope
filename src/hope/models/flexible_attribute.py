from typing import Any

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import JSONField, Q
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.models import SoftDeletableModel
import mptt
from mptt.fields import TreeForeignKey
from natural_keys import NaturalKeyModel

from hope.models.utils import SoftDeletionTreeManager, SoftDeletionTreeModel, TimeStampedUUIDModel


def label_contains_english_en_validator(data: dict) -> None:
    if "English(EN)" not in data:
        raise ValidationError('The "English(EN)" key is required in the label.')


class FlexibleAttribute(SoftDeletableModel, NaturalKeyModel, TimeStampedUUIDModel):
    STRING = "STRING"
    IMAGE = "IMAGE"
    INTEGER = "INTEGER"
    DECIMAL = "DECIMAL"
    SELECT_ONE = "SELECT_ONE"
    SELECT_MANY = "SELECT_MANY"
    DATE = "DATE"
    GEOPOINT = "GEOPOINT"
    PDU = "PDU"
    TYPE_CHOICE = Choices(
        (DATE, _("Date")),
        (DECIMAL, _("Decimal")),
        (IMAGE, _("Image")),
        (INTEGER, _("Integer")),
        (GEOPOINT, _("Geopoint")),
        (SELECT_ONE, _("Select One")),
        (SELECT_MANY, _("Select Many")),
        (STRING, _("String")),
        (PDU, _("PDU")),
    )

    ASSOCIATED_WITH_HOUSEHOLD = 0
    ASSOCIATED_WITH_INDIVIDUAL = 1
    ASSOCIATED_WITH_CHOICES: Any = (
        (ASSOCIATED_WITH_HOUSEHOLD, _("Household")),
        (ASSOCIATED_WITH_INDIVIDUAL, _("Individual")),
    )

    name = models.CharField(max_length=255)
    group = models.ForeignKey(
        "core.FlexibleAttributeGroup",
        on_delete=models.CASCADE,
        related_name="flex_attributes",
        null=True,
        blank=True,
    )
    type = models.CharField(max_length=16, choices=TYPE_CHOICE)
    associated_with = models.SmallIntegerField(choices=ASSOCIATED_WITH_CHOICES)
    program = models.ForeignKey(
        "program.Program",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="pdu_fields",
    )
    pdu_data = models.OneToOneField(
        "core.PeriodicFieldData",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="flex_field",
    )
    required = models.BooleanField(default=False)
    label = JSONField(default=dict, validators=[label_contains_english_en_validator])
    hint = JSONField(default=dict)

    class Meta:
        app_label = "core"
        constraints = [
            models.UniqueConstraint(fields=("name", "program"), name="unique_name_program"),
            models.UniqueConstraint(
                fields=("name",),
                condition=Q(program__isnull=True),
                name="unique_name_without_program",
            ),
        ]

    def clean(self) -> None:
        if (
            self.program
            and FlexibleAttribute.objects.filter(name=self.name, program__isnull=True).exclude(id=self.id).exists()
        ):
            raise ValidationError(f'Flex field with name "{self.name}" already exists without a program.')
        if (
            not self.program
            and FlexibleAttribute.objects.filter(name=self.name, program__isnull=False).exclude(id=self.id).exists()
        ):
            raise ValidationError(f'Flex field with name "{self.name}" already exists inside a program.')

        label_contains_english_en_validator(self.label)

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_flex_field(self) -> bool:
        return True

    def __str__(self) -> str:
        return f"type: {self.type}, name: {self.name}"


class FlexibleAttributeGroupManager(SoftDeletionTreeManager):
    def get_by_natural_key(self, name: str) -> "FlexibleAttributeGroup":
        return self.get(name=name)


class FlexibleAttributeGroup(SoftDeletionTreeModel):
    name = models.CharField(max_length=255, unique=True)
    label = JSONField(default=dict)
    required = models.BooleanField(default=False)
    repeatable = models.BooleanField(default=False)
    parent = TreeForeignKey(
        "self",
        verbose_name=_("Parent"),
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        on_delete=models.CASCADE,
    )
    objects = FlexibleAttributeGroupManager()

    def __str__(self) -> str:
        return f"name: {self.name}"

    def natural_key(self) -> tuple[str]:
        return (self.name,)

    class Meta:
        app_label = "core"


class FlexibleAttributeChoice(SoftDeletableModel, NaturalKeyModel, TimeStampedUUIDModel):
    class Meta:
        app_label = "core"
        unique_together = ["list_name", "name"]
        ordering = ("name",)

    list_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    label = JSONField(default=dict)
    flex_attributes = models.ManyToManyField("core.FlexibleAttribute", related_name="choices")

    def __str__(self) -> str:
        return f"list name: {self.list_name}, name: {self.name}"


class PeriodicFieldData(models.Model):
    """Additional data for PDU."""

    STRING = "STRING"
    DECIMAL = "DECIMAL"
    DATE = "DATE"
    BOOL = "BOOL"

    TYPE_CHOICES = Choices(
        (DATE, _("Date")),
        (DECIMAL, _("Number")),
        (STRING, _("Text")),
        (BOOL, _("Boolean (true/false)")),
    )

    subtype = models.CharField(max_length=16, choices=TYPE_CHOICES)
    rounds_names = ArrayField(models.CharField(max_length=255), default=list)
    number_of_rounds = models.IntegerField()

    class Meta:
        app_label = "core"
        verbose_name = "Periodic Field Data"
        verbose_name_plural = "Periodic Fields Data"

    def __str__(self) -> str:
        return f"Periodic Field Data: {self.pk}"


mptt.register(FlexibleAttributeGroup, order_insertion_by=["name"])
