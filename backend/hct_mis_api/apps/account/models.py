import dataclasses
import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from django import forms
from django.conf import settings
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
from django.db.models import JSONField, Q, QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from model_utils.models import UUIDModel
from natural_keys import NaturalKeyModel

from hct_mis_api.apps.account.fields import ChoiceArrayField
from hct_mis_api.apps.account.permissions import (
    DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER,
    Permissions,
)
from hct_mis_api.apps.account.utils import test_conditional
from hct_mis_api.apps.core.mixins import LimitBusinessAreaModelMixin
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel
from hct_mis_api.apps.utils.validators import (
    DoubleSpaceValidator,
    StartEndSpaceValidator,
)
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

logger = logging.getLogger(__name__)

INVITED = "INVITED"
ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"
USER_STATUS_CHOICES = (
    (ACTIVE, _("Active")),
    (INACTIVE, _("Inactive")),
    (INVITED, _("Invited")),
)


@dataclasses.dataclass
class BusinessAreaPartnerPermission:
    business_area_id: str
    roles: List[str] = dataclasses.field(default_factory=list)
    programs: Dict[str, List[str]] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {"roles": self.roles or [], "programs": self.programs or {}}

    def in_program(self, program_id: str) -> Optional[List[str]]:
        return self.programs.get(program_id, None)

    def get_program_ids(self) -> List[str]:
        return list(self.programs.keys())

    def get_all_area_ids(self) -> List[str]:
        all_area_ids = []
        for _program_id, area_ids in self.programs.items():
            all_area_ids.extend(area_ids)
        return all_area_ids


class PartnerPermission:
    def __init__(self) -> None:
        self._permissions: Dict[str, BusinessAreaPartnerPermission] = {}
        self._available_business_areas = []

    @classmethod
    def from_dict(cls, data: Dict) -> "PartnerPermission":
        instance = cls()
        for business_area_id in data:
            instance._permissions[business_area_id] = BusinessAreaPartnerPermission(
                business_area_id=business_area_id,
                roles=data[business_area_id].get("roles", []),
                programs=data[business_area_id].get("programs", {}),
            )
        instance._available_business_areas.extend(instance._permissions.keys())
        return instance

    @classmethod
    def from_list(cls, data: List[BusinessAreaPartnerPermission]) -> "PartnerPermission":
        instance = cls()
        for permission in data:
            instance._permissions[permission.business_area_id] = permission
        instance._available_business_areas.extend(instance._permissions.keys())
        return instance

    def set_roles(self, business_area_id: str, roles: List[str]) -> None:
        permissions = self._permissions.get(business_area_id, BusinessAreaPartnerPermission(business_area_id))
        permissions.roles = roles
        self._permissions[business_area_id] = permissions

    def set_program_areas(self, business_area_id: str, program_id: str, areas_ids: List[str]) -> None:
        permissions = self._permissions.get(business_area_id, BusinessAreaPartnerPermission(business_area_id))
        permissions.programs[program_id] = areas_ids
        self._permissions[business_area_id] = permissions

    def remove_program_areas(self, business_area_id: str, program_id: str) -> None:
        permissions = self._permissions.get(business_area_id, BusinessAreaPartnerPermission(business_area_id))
        if program_id in permissions.programs:
            permissions.programs.pop(program_id)

    def to_dict(self) -> Dict:
        return {business_area_id: permission.to_dict() for business_area_id, permission in self._permissions.items()}

    def to_list(self) -> List[BusinessAreaPartnerPermission]:
        return list(self._permissions.values())

    def roles_for(self, business_area_id: str) -> List[str]:
        if business_area_id not in self._available_business_areas:
            return []
        return self._permissions[business_area_id].roles

    def areas_for(self, business_area_id: str, program_id: str) -> Optional[List[str]]:
        """
        if return None it means that no access into BA for this partner
        if return empty list [] it means that partner have access for all Areas
        """
        if business_area_id not in self._available_business_areas:
            return None
        return self._permissions[business_area_id].in_program(program_id)

    def all_areas_for(self, business_area_id: str) -> Optional[List[str]]:
        """
        return list for all Areas or None
        """
        if business_area_id not in self._available_business_areas:
            return None
        return self._permissions[business_area_id].get_all_area_ids()

    def business_area_ids(self) -> List[str]:
        # return only BA with roles NOT []
        return [ba_id for ba_id in self._available_business_areas if self._permissions[ba_id].roles]

    def program_ids(self) -> List[str]:
        ids = []
        for ba_perms in self._permissions.values():
            ids.extend(ba_perms.get_program_ids())
        return ids

    def get_programs_for_business_area(self, business_area_id: str) -> "Optional[BusinessAreaPartnerPermission]":
        if business_area_id not in self._available_business_areas:
            return None
        return self._permissions[business_area_id]


class Partner(LimitBusinessAreaModelMixin, MPTTModel):
    name = CICharField(max_length=100, unique=True)
    parent = TreeForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Parent"),
    )
    is_un = models.BooleanField(verbose_name="U.N.", default=False)
    """
        permissions structure
        {
            "business_area_id": {
                "roles": ["role_id_1", "role_id_2"],
                "programs": {"program_id":["admin_id"]}
            }
        }
    """
    permissions = JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.name} [Sub-Partner of {self.parent.name}]" if self.parent else self.name

    @property
    def is_child(self) -> bool:
        return self.parent is None

    @property
    def is_parent(self) -> bool:
        return self.id in Partner.objects.exclude(parent__isnull=True).values_list("parent", flat=True)

    def get_permissions(self) -> PartnerPermission:
        return PartnerPermission.from_dict(self.permissions)

    def set_permissions(self, partner_permission: PartnerPermission) -> None:
        self.permissions = partner_permission.to_dict()

    @classmethod
    def get_partners_as_choices(cls) -> List:
        return [(partner.id, partner.name) for partner in cls.objects.exclude(name=settings.DEFAULT_EMPTY_PARTNER)]

    @classmethod
    def get_partners_for_program_as_choices(cls, business_area_id: str, program_id: Optional[str] = None) -> List:
        partners = cls.objects.exclude(name=settings.DEFAULT_EMPTY_PARTNER)
        if program_id:
            return [
                (partner.id, partner.name)
                for partner in partners
                if program_id in partner.get_program_ids_for_business_area(business_area_id)
            ]
        else:
            return [
                (partner.id, partner.name)
                for partner in partners
                if partner.get_program_ids_for_business_area(business_area_id)
            ]

    @property
    def is_unicef(self) -> bool:
        return self.name == "UNICEF"

    @property
    def is_default(self) -> bool:
        return self.name == settings.DEFAULT_EMPTY_PARTNER

    @property
    def is_editable(self) -> bool:
        return not self.is_unicef and not self.is_default

    def has_complete_access_in_program(self, program_id: str, business_area_id: str) -> bool:
        return self.is_unicef or self.get_permissions().areas_for(business_area_id, program_id) == []

    @property
    def program_ids(self) -> List[str]:
        return self.get_permissions().program_ids()

    @property
    def business_area_ids(self) -> List[str]:
        return self.get_permissions().business_area_ids()

    def get_program_ids_for_business_area(self, business_area_id: str) -> List[str]:
        from hct_mis_api.apps.program.models import Program

        if self.is_unicef:
            return [
                str(program_id)
                for program_id in Program.objects.filter(business_area_id=business_area_id).values_list("id", flat=True)
            ]
        programs_for_business_area = self.get_permissions().get_programs_for_business_area(business_area_id)

        return programs_for_business_area.get_program_ids() if programs_for_business_area else []


class User(AbstractUser, NaturalKeyModel, UUIDModel):
    status = models.CharField(choices=USER_STATUS_CHOICES, max_length=10, default=INVITED)
    # TODO: in future will remove null=True after migrate prod data
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, null=True)
    email = models.EmailField(_("email address"), unique=True)
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
            self.partner, _ = Partner.objects.get_or_create(name=settings.DEFAULT_EMPTY_PARTNER)
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
        partner_role_ids = self.partner.get_permissions().roles_for(str(business_area_id))
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
        if program_id is in arguments need to check if user.partner.permissions json has program_id
        """
        has_program_access = True
        # Partner is_unicef has access to all Programs and check perms based on user perms
        if not self.partner.is_unicef:
            # check program access and partner roles permissions list
            if program_id:
                has_program_access = str(program_id) in self.get_partner_programs_areas_dict(
                    business_area_slug=business_area_slug
                )

            partner_role_ids_per_ba = self.get_partner_role_ids_list(business_area_slug=business_area_slug)

            all_partner_roles_permissions_list = list(
                Role.objects.filter(id__in=partner_role_ids_per_ba).values_list("permissions", flat=True)
            )
        else:
            # default perms for is_unicef partner
            all_partner_roles_permissions_list = [DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER]

        user_roles_query = UserRole.objects.filter(user=self, business_area__slug=business_area_slug).exclude(
            expiry_date__lt=timezone.now()
        )
        all_user_roles_permissions_list = list(
            Role.objects.filter(user_roles__in=user_roles_query).values_list("permissions", flat=True)
        )
        return (
            list(
                set(
                    [perm for perms in all_partner_roles_permissions_list for perm in perms]
                    + [perm for perms in all_user_roles_permissions_list if perms for perm in perms]
                )
            )
            if has_program_access
            else list()
        )

    @property
    def business_areas(self) -> QuerySet[BusinessArea]:
        return BusinessArea.objects.filter(
            Q(Q(user_roles__user=self) & ~Q(user_roles__expiry_date__lt=timezone.now()))
            | Q(id__in=self.partner.business_area_ids)
        ).distinct()

    @test_conditional(lru_cache())
    def cached_has_partner_roles_for_business_area_and_permission(
        self, business_area: BusinessArea, permission: str
    ) -> bool:
        return Role.objects.filter(
            id__in=self.get_partner_role_ids_list(business_area_id=business_area.pk), permissions__contains=[permission]
        ).exists()

    @test_conditional(lru_cache())
    def cached_has_user_roles_for_business_area_and_permission(
        self, business_area: BusinessArea, permission: str
    ) -> bool:
        user_roles_query = UserRole.objects.filter(user=self, business_area=business_area).exclude(
            expiry_date__lt=timezone.now()
        )
        return Role.objects.filter(
            user_roles__in=user_roles_query,
            permissions__contains=[permission],
        ).exists()

    def has_permission(
        self, permission: str, business_area: BusinessArea, program_id: Optional[UUID] = None, write: bool = False
    ) -> bool:
        has_program_access = True
        has_partner_roles = False

        if not self.partner.is_unicef:
            if program_id:
                has_program_access = str(program_id) in self.get_partner_programs_areas_dict(
                    business_area_id=business_area.pk
                )
            has_partner_roles = self.cached_has_partner_roles_for_business_area_and_permission(
                business_area=business_area,
                permission=permission,
            )

        has_user_roles = self.cached_has_user_roles_for_business_area_and_permission(
            business_area=business_area,
            permission=permission,
        )

        if self.partner.is_unicef:
            return has_program_access and (
                has_user_roles or permission in DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER
            )
        else:
            return has_program_access and (has_user_roles or has_partner_roles)

    def get_partner_areas_ids_per_program(self, program_id: UUID, business_area_id: UUID) -> List:
        partner_areas_ids_per_program = self.get_partner_programs_areas_dict(business_area_id=business_area_id).get(
            str(program_id), []
        )

        return partner_areas_ids_per_program

    @test_conditional(lru_cache())
    def cached_user_roles(self) -> QuerySet["UserRole"]:
        return self.user_roles.all().select_related("business_area")

    def can_download_storage_files(self) -> bool:
        return any(
            self.has_permission(Permissions.DOWNLOAD_STORAGE_FILE.name, role.business_area)
            for role in self.cached_user_roles()
        )

    def can_change_fsp(self) -> bool:
        return any(
            self.has_permission(Permissions.PM_ADMIN_FINANCIAL_SERVICE_PROVIDER_UPDATE.name, role.business_area)
            for role in self.cached_user_roles()
        )

    def can_add_business_area_to_partner(self) -> bool:
        return any(
            self.has_permission(Permissions.CAN_ADD_BUSINESS_AREA_TO_PARTNER.name, role.business_area)
            for role in self.cached_user_roles()
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
            ("restrict_help_desk", "Limit fields to be editable for help desk"),
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
    expiry_date = models.DateField(
        blank=True, null=True, help_text="After expiry date this User Role will be inactive."
    )

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
