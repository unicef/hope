from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint, Q
from model_utils.models import TimeStampedModel


class DataCollectingType(TimeStampedModel):
    class Type(models.TextChoices):
        STANDARD = "STANDARD", "Standard"
        SOCIAL = "SOCIAL", "Social Workers"

    code = models.CharField(max_length=32)
    label = models.CharField(max_length=32, blank=True)
    type = models.CharField(choices=Type.choices, null=True, blank=True, max_length=32)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    deprecated = models.BooleanField(
        default=False,
        help_text="Cannot be used in new programs, totally hidden in UI, only admin have access",
    )
    individual_filters_available = models.BooleanField(default=False)
    household_filters_available = models.BooleanField(default=True)
    recalculate_composition = models.BooleanField(default=False)
    weight = models.PositiveSmallIntegerField(default=0)
    compatible_types = models.ManyToManyField("self", blank=True, symmetrical=False)
    limit_to = models.ManyToManyField(to="BusinessArea", related_name="data_collecting_types", blank=True)

    def __str__(self) -> str:
        return self.label

    class Meta:
        app_label = "core"
        constraints = [
            UniqueConstraint(
                fields=["label", "code"],
                name="unique_label_code_data_collecting_type",
            )
        ]
        ordering = ("-weight",)

    def clean(self) -> None:
        super().clean()
        if (
            self.pk
            and self.type
            and self.compatible_types.exists()
            and not getattr(self, "skip_type_validation", False)
        ):
            incompatible_dcts = self.compatible_types.exclude(Q(type=self.type) | Q(pk=self.pk))
            if incompatible_dcts.exists():
                raise ValidationError("Type of DCT cannot be changed if it has compatible DCTs of different type.")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
