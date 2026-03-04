from django.core.validators import MaxLengthValidator, MinLengthValidator, ProhibitNullCharactersValidator
from django.db import models
from natural_keys import NaturalKeyModel

from hope.apps.account.fields import ChoiceArrayField
from hope.apps.account.permissions import Permissions
from hope.apps.utils.validators import DoubleSpaceValidator, StartEndSpaceValidator
from hope.models.utils import TimeStampedUUIDModel


class Role(NaturalKeyModel, TimeStampedUUIDModel):
    name = models.CharField(
        max_length=250,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(255),
            DoubleSpaceValidator,
            StartEndSpaceValidator,
            ProhibitNullCharactersValidator(),
        ],
        unique=True,
    )
    permissions = ChoiceArrayField(
        models.CharField(choices=Permissions.choices(), max_length=255),
        null=True,
        blank=True,
    )
    is_visible_on_ui = models.BooleanField(default=True)
    is_available_for_partner = models.BooleanField(default=True)

    class Meta:
        app_label = "account"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_roles_as_choices(cls) -> list:
        return [(role.id, role.name) for role in cls.objects.all()]
