import dataclasses
import logging
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.postgres.fields import ArrayField, CICharField
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    ProhibitNullCharactersValidator,
)
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

from model_utils import Choices
from model_utils.models import UUIDModel
from natural_keys import NaturalKeyModel

from hct_mis_api.apps.account.fields import ChoiceArrayField
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel
from hct_mis_api.apps.utils.validators import (
    DoubleSpaceValidator,
    StartEndSpaceValidator,
)

logger = logging.getLogger(__name__)

INVITED = "INVITED"
ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"
USER_STATUS_CHOICES = (
    (ACTIVE, _("Active")),
    (INACTIVE, _("Inactive")),
    (INVITED, _("Invited")),
)
USER_PARTNER_CHOICES = Choices("UNICEF", "UNHCR", "WFP")


@dataclasses.dataclass(frozen=True)
class ProgramAreasList:
    program_id: UUID
    areas: List[UUID]


@dataclasses.dataclass(frozen=True)
class BusinessAreaPartnerPermissions:
    business_area_id: UUID
    roles: List[UUID]
    programs: ProgramAreasList

    @classmethod
    def from_dict(cls, data_permissions: Dict) -> List["BusinessAreaPartnerPermissions"]:
        """
        return: [BusinessAreaPartnerPermissions(
            business_area_id='uuid_ba',
            roles=['role_id_1', 'role_id_2'],
            programs={'program_id_1': ['area_1', 'area_2']}
        )]
        """
        ba_partner_perms_list: List = []
        for business_area_id in data_permissions:
            ba_partner_perms_list.append(
                cls(
                    business_area_id=business_area_id,
                    roles=data_permissions[business_area_id].get("roles", []),
                    programs=data_permissions[business_area_id].get("programs", {}),
                )
            )
        return ba_partner_perms_list


class Partner(models.Model):
    name = CICharField(max_length=100, unique=True)
    is_un = models.BooleanField(verbose_name="U.N.", default=False)
    """
        permissions structure
        {
            "business_area_id": {
                "roles": ["role_id_1", "role_id_2"]
                "programs": {"program_id":["admin_id"]}
            }
        }
    """
    permissions = JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_partners_as_choices(cls) -> List:
        return [(role.id, role.name) for role in cls.objects.all()]

    @property
    def is_unicef(self):
        return self.name == "UNICEF"


class User(AbstractUser, NaturalKeyModel, UUIDModel):
    status = models.CharField(choices=USER_STATUS_CHOICES, max_length=10, default=INVITED)
    # org = models.CharField(choices=USER_PARTNER_CHOICES, max_length=10, default=USER_PARTNER_CHOICES.UNICEF)
    # TODO: in future will remove null=True after migrate prod data
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, null=True)
    email = models.EmailField(_("email address"), blank=True, unique=True)
    available_for_export = models.BooleanField(
        default=True, help_text="Indicating if a User can be exported to CashAssist"
    )
    custom_fields = JSONField(default=dict, blank=True)

    job_title = models.CharField(max_length=255, blank=True)
    ad_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True, editable=False)

    # CashAssist DOAP fields
    last_modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_doap_sync = models.DateTimeField(
        default=None, null=True, blank=True, help_text="Timestamp of last sync with CA"
    )
    doap_hash = models.TextField(
        editable=False,
        default="",
        help_text="System field used to check if changes need to be sent to CA",
    )

    def __str__(self) -> str:
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email or self.username

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.partner:
            self.partner = Partner.objects.get(name="UNICEF")
        if not self.partner.pk:
            self.partner.save()
        super().save(*args, **kwargs)

    def get_partner_role_ids_list(
        self, business_area_slug: Optional[str] = None, business_area_id: Optional["UUID"] = None
    ) -> List:
        if not business_area_slug and not business_area_id:
            return list()

        if not business_area_id and business_area_slug:
            business_area_id = BusinessArea.objects.get(slug=business_area_slug).id
        partner_role_ids = self.partner.permissions.get(str(business_area_id), {}).get("roles", [])
        return partner_role_ids

    def get_partner_programs_areas_dict(
        self, business_area_slug: Optional[str] = None, business_area_id: Optional["UUID"] = None
    ) -> Dict:
        if not business_area_slug and not business_area_id:
            return dict()

        if not business_area_id and business_area_slug:
            business_area_id = BusinessArea.objects.get(slug=business_area_slug).id
        partner_programs_dict = self.partner.permissions.get(str(business_area_id), {}).get("programs", {})
        return partner_programs_dict

    def permissions_in_business_area(self, business_area_slug: str, program_id: Optional[UUID] = None) -> List:
        """
        return list of permissions based on User Role BA and User Partner
        if program_id in arguments need to check if user.partner.permissions json has program id
        """
        # TODO: MB remove in future 'has_program_access = True' or cross programs check will be without program_id ??
        has_program_access = True
        if program_id:
            if self.partner.is_unicef:
                has_program_access = True
            else:
                has_program_access = str(program_id) in self.get_partner_programs_areas_dict(
                    business_area_slug=business_area_slug
                )

        partner_role_ids_per_ba = self.get_partner_role_ids_list(business_area_slug=business_area_slug)

        all_partner_roles_permissions_list = list(
            Role.objects.filter(id__in=partner_role_ids_per_ba).values_list("permissions", flat=True)
        )
        all_user_roles_permissions_list = list(
            Role.objects.filter(
                user_roles__user=self,
                user_roles__business_area__slug=business_area_slug,
            ).values_list("permissions", flat=True)
        )
        return (
            list(
                set(
                    [perm for perms in all_partner_roles_permissions_list for perm in perms]
                    + [perm for perms in all_user_roles_permissions_list for perm in perms]
                )
            )
            if has_program_access
            else list()
        )

    def has_permission(
        self, permission: str, business_area: BusinessArea, program_id: Optional[UUID] = None, write: bool = False
    ) -> bool:
        # TODO: MB remove in future 'has_program_access = True' or cross programs check will be without program_id ??
        has_program_access = True
        if program_id:
            if self.partner.is_unicef:
                has_program_access = True
            else:
                has_program_access = program_id in self.get_partner_programs_areas_dict(
                    business_area_id=business_area.pk
                )

        partner_role_ids = self.get_partner_role_ids_list(business_area_id=business_area.pk)

        partner_roles = Role.objects.filter(
            id__in=partner_role_ids,
            permissions__contains=[permission],
        )

        user_roles = Role.objects.filter(
            permissions__contains=[permission],
            user_roles__user=self,
            user_roles__business_area=business_area,
        )
        return has_program_access and (user_roles.count() > 0 or partner_roles.count() > 0)

    def get_partner_areas_ids_per_program(self, program_id: UUID, business_area_id: UUID) -> List:
        partner_areas_ids_per_program = self.get_partner_programs_areas_dict(business_area_id=business_area_id).get(
            str(program_id), []
        )

        return partner_areas_ids_per_program

    def can_download_storage_files(self) -> bool:
        return any(
            self.has_permission(Permissions.DOWNLOAD_STORAGE_FILE.name, role.business_area)
            for role in self.user_roles.all()
        )

    def can_change_fsp(self) -> bool:
        return any(
            self.has_permission(Permissions.PM_ADMIN_FINANCIAL_SERVICE_PROVIDER_UPDATE.name, role.business_area)
            for role in self.user_roles.all()
        )

    class Meta:
        permissions = (
            ("can_load_from_ad", "Can load users from ActiveDirectory"),
            ("can_sync_with_ad", "Can synchronise user with ActiveDirectory"),
            ("can_create_kobo_user", "Can create users in Kobo"),
            ("can_import_from_kobo", "Can import and sync users from Kobo"),
            ("can_upload_to_kobo", "Can upload CSV file to Kobo"),
            ("can_debug", "Can access debug informations"),
            ("can_inspect", "Can inspect objects"),
            ("quick_links", "Can see quick links in admin"),
        )


class HorizontalChoiceArrayField(ArrayField):
    def formfield(self, form_class: Optional[Any] = ..., choices_form_class: Optional[Any] = ..., **kwargs: Any) -> Any:
        widget = FilteredSelectMultiple(self.verbose_name, False)
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "widget": widget,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class UserRole(NaturalKeyModel, TimeStampedUUIDModel):
    business_area = models.ForeignKey("core.BusinessArea", related_name="user_roles", on_delete=models.CASCADE)
    user = models.ForeignKey("account.User", related_name="user_roles", on_delete=models.CASCADE)
    role = models.ForeignKey("account.Role", related_name="user_roles", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("business_area", "user", "role")

    def __str__(self) -> str:
        return f"{self.user} {self.role} in {self.business_area}"


class UserGroup(NaturalKeyModel, models.Model):
    business_area = models.ForeignKey("core.BusinessArea", related_name="user_groups", on_delete=models.CASCADE)
    user = models.ForeignKey("account.User", related_name="user_groups", on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name="user_groups", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("business_area", "user", "group")

    def __str__(self) -> str:
        return f"{self.user} {self.group} in {self.business_area}"


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

    def natural_key(self) -> Tuple:
        return self.name, self.subsystem

    def clean(self) -> None:
        if self.subsystem != Role.HOPE and self.permissions:
            raise ValidationError("Only HOPE roles can have permissions")

    class Meta:
        unique_together = ("name", "subsystem")
        ordering = ("subsystem", "name")

    def __str__(self) -> str:
        return f"{self.name} ({self.subsystem})"

    @classmethod
    def get_roles_as_choices(cls) -> List:
        return [(role.id, role.name) for role in cls.objects.all()]


class IncompatibleRolesManager(models.Manager):
    def validate_user_role(self, user: User, business_area: "BusinessArea", role: UserRole) -> None:
        incompatible_roles = list(
            IncompatibleRoles.objects.filter(role_one=role).values_list("role_two", flat=True)
        ) + list(IncompatibleRoles.objects.filter(role_two=role).values_list("role_one", flat=True))
        incompatible_userroles = UserRole.objects.filter(
            business_area=business_area,
            role__id__in=incompatible_roles,
            user=user,
        )
        if user.id:
            incompatible_userroles = incompatible_userroles.exclude(id=user.id)
        if incompatible_userroles.exists():
            raise ValidationError(
                {
                    "role": _(
                        f"This role is incompatible with {', '.join([userrole.role.name for userrole in incompatible_userroles])}"
                    )
                }
            )


class IncompatibleRoles(NaturalKeyModel, TimeStampedUUIDModel):
    """
    Keeps track of what roles are incompatible:
    user cannot be assigned both of the roles in the same business area at the same time
    """

    role_one = models.ForeignKey("account.Role", related_name="incompatible_roles_one", on_delete=models.CASCADE)
    role_two = models.ForeignKey("account.Role", related_name="incompatible_roles_two", on_delete=models.CASCADE)

    objects = IncompatibleRolesManager()

    def __str__(self) -> str:
        return f"{self.role_one.name} and {self.role_two.name}"

    class Meta:
        verbose_name = "incompatible roles"
        verbose_name_plural = "incompatible roles"
        unique_together = ("role_one", "role_two")

    def clean(self) -> None:
        super().clean()
        if self.role_one == self.role_two:
            logger.error(f"Provided roles are the same role={self.role_one}")
            raise ValidationError(_("Choose two different roles."))
        failing_users = set()

        for role_pair in ((self.role_one, self.role_two), (self.role_two, self.role_one)):
            for userrole in UserRole.objects.filter(role=role_pair[0]):
                if UserRole.objects.filter(
                    user=userrole.user,
                    business_area=userrole.business_area,
                    role=role_pair[1],
                ).exists():
                    failing_users.add(userrole.user.email)

        if failing_users:
            logger.error(
                f"Users: [{', '.join(failing_users)}] have these roles assigned to them in the same business area. "
                "Please fix them before creating this incompatible roles pair."
            )
            raise ValidationError(
                _(
                    f"Users: [{', '.join(failing_users)}] have these roles assigned to them in the same business area. "
                    "Please fix them before creating this incompatible roles pair."
                )
            )

    def validate_unique(self, *args: Any, **kwargs: Any) -> None:
        super().validate_unique(*args, **kwargs)
        # unique_together will take care of unique couples only if order is the same
        # since it doesn't matter if role is one or two, we need to check for reverse uniqueness as well
        if IncompatibleRoles.objects.filter(role_one=self.role_two, role_two=self.role_one).exists():
            logger.error(
                f"This combination of roles ({self.role_one}, {self.role_two}) already exists as incompatible pair."
            )
            raise ValidationError(_("This combination of roles already exists as incompatible pair."))
