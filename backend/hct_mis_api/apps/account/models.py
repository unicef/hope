from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from model_utils.models import UUIDModel

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
        return (
            self.roles.values("permissions__id")
            .annotate(counts=Count("permissions__id"))
            .values_list("permissions__id", "permissions__name", "permissions__write")
            .count()
        )

    def has_permission(self, permission, business_area, write=False):
        query = UserPermission.objects.filter(name=permission).filter(
            roles__user_roles__users__id=self.id, roles__user_roles__business_area=business_area
        )
        if write:
            query = query.filter(write=True)
        return query.count() > 0


class UserRole(TimeStampedUUIDModel):
    business_area = models.ForeignKey("core.BusinessArea", related_name="user_roles", on_delete=models.CASCADE)
    user = models.ForeignKey("account.User", related_name="user_roles", on_delete=models.CASCADE)
    role = models.ForeignKey("account.Role", related_name="user_roles", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} {self.role} in {self.business_area}"


class Role(TimeStampedUUIDModel):
    name = models.CharField(max_length=250)
    permissions = models.ManyToManyField("account.UserPermission", related_name="roles")

    def __str__(self):
        return self.name

    @classmethod
    def get_roles_as_choices(cls):
        return [(role.name, role.name) for role in cls.objects.all()]


class UserPermission(TimeStampedUUIDModel):
    PERMISSION_DASHBOARD = 1
    PERMISSION_RDI = 2
    PERMISSION_POPULATION = 3
    PERMISSION_PROGRAM_MANAGEMENT = 4
    PERMISSION_TARGETING = 5
    PERMISSION_PAYMENT_VERIFICATION = 6
    PERMISSION_GRIEVANCES = 7
    PERMISSION_REPORTING = 8
    PERMISSION_USER_MANAGEMENT = 9
    PERMISSION_SETTINGS = 10
    PERMISSIONS_CHOICES = (
        (PERMISSION_DASHBOARD, _("Dashboard")),
        (PERMISSION_RDI, _("Registration Data Import")),
        (PERMISSION_POPULATION, _("Population")),
        (PERMISSION_PROGRAM_MANAGEMENT, _("Program Management")),
        (PERMISSION_TARGETING, _("Targeting")),
        (PERMISSION_PAYMENT_VERIFICATION, _("Payment Verification")),
        (PERMISSION_GRIEVANCES, _("Grievances")),
        (PERMISSION_REPORTING, _("Reporting")),
        (PERMISSION_USER_MANAGEMENT, _("User Management")),
        (PERMISSION_SETTINGS, _("Settings")),
    )
    PERMISSIONS_CHOICES_DICT = dict(PERMISSIONS_CHOICES)
    name = models.CharField(max_length=250, choices=PERMISSIONS_CHOICES)
    write = models.BooleanField(default=False)

    def __str__(self):
        type_name = _("Read")
        if self.write:
            type_name = _("Write")
        return f"{UserPermission.PERMISSIONS_CHOICES_DICT.get(int(self.name))} {type_name} Permission"
