from django import forms
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from model_utils.models import UUIDModel

from account.permissions import PERMISSIONS_CHOICES
from utils.models import TimeStampedUUIDModel

INVITED = "INVITED"
ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"
USER_STATUS_CHOICES = (
    (INVITED, _("Invited")),
    (ACTIVE, _("Active")),
    (INACTIVE, _("Inactive")),
)
USER_PARTNER_CHOICES = Choices("UNHCR", "WFP", "UNICEF")


class User(AbstractUser, UUIDModel):
    status = models.CharField(choices=USER_STATUS_CHOICES, max_length=10, default=INVITED)
    partner = models.CharField(choices=USER_PARTNER_CHOICES, max_length=10, default=USER_PARTNER_CHOICES.UNICEF)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def all_permissions(self):
        return 

    def has_permissions(self, permissions, business_area, write=False):
        query = Role.objects.filter(
            permissions__contains=permissions, user_roles__user=self, user_roles__business_area=business_area
        )
        return query.count() > 0

    def has_permission(self, permission, business_area, write=False):
        query = Role.objects.filter(
            permissions__contains=[permission], user_roles__user=self, user_roles__business_area=business_area
        )
        return query.count() > 0


class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class UserRole(TimeStampedUUIDModel):
    business_area = models.ForeignKey("core.BusinessArea", related_name="user_roles", on_delete=models.CASCADE)
    user = models.ForeignKey("account.User", related_name="user_roles", on_delete=models.CASCADE)
    role = models.ForeignKey("account.Role", related_name="user_roles", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} {self.role} in {self.business_area}"


class Role(TimeStampedUUIDModel):
    name = models.CharField(max_length=250)
    permissions = ChoiceArrayField(models.CharField(choices=PERMISSIONS_CHOICES, max_length=255))

    def __str__(self):
        return self.name

    @classmethod
    def get_roles_as_choices(cls):
        return [(role.id, role.name) for role in cls.objects.all()]
