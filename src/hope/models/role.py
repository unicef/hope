from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator, ProhibitNullCharactersValidator
from django.db import models
from natural_keys import NaturalKeyModel

from hope.apps.utils.validators import DoubleSpaceValidator, StartEndSpaceValidator

from hope.apps.account.fields import ChoiceArrayField

from hope.apps.account.permissions import Permissions
from hope.models.utils import TimeStampedUUIDModel


class Role(NaturalKeyModel, TimeStampedUUIDModel):
    API = "API"
    HOPE = "HOPE"
    KOBO = "KOBO"
    CA = "CA"
    SUBSYSTEMS = (
        (HOPE, "HOPE"),
        (KOBO, "Kobo"),
        (CA, "CashAssist"),
        (API, "API"),
    )

    name = models.CharField(
        max_length=250,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(255),
            DoubleSpaceValidator,
            StartEndSpaceValidator,
            ProhibitNullCharactersValidator(),
        ],
    )
    subsystem = models.CharField(choices=SUBSYSTEMS, max_length=30, default=HOPE)
    permissions = ChoiceArrayField(
        models.CharField(choices=Permissions.choices(), max_length=255),
        null=True,
        blank=True,
    )
    is_visible_on_ui = models.BooleanField(default=True)
    is_available_for_partner = models.BooleanField(default=True)

    def natural_key(self) -> tuple:
        return self.name, self.subsystem

    def clean(self) -> None:
        if self.subsystem != Role.HOPE and self.permissions:
            raise ValidationError("Only HOPE roles can have permissions")

    class Meta:
        app_label = "account"
        unique_together = ("name", "subsystem")
        ordering = ("subsystem", "name")

    def __str__(self) -> str:
        return f"{self.name} ({self.subsystem})"

    @classmethod
    def get_roles_as_choices(cls) -> list:
        return [(role.id, role.name) for role in cls.objects.all()]
