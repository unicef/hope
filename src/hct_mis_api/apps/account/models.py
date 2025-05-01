import logging
from functools import lru_cache
from typing import Any, Optional
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
from hct_mis_api.apps.core.models import BusinessArea, BusinessAreaPartnerThrough
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.utils.mailjet import MailjetClient
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

    def __str__(self) -> str:
        return f"{self.name} [Sub-Partner of {self.parent.name}]" if self.parent else self.name

    @property
    def is_child(self) -> bool:
        return self.parent is None

    @property
    def is_parent(self) -> bool:
        return self.id in Partner.objects.exclude(parent__isnull=True).values_list("parent", flat=True)

    @classmethod
    def get_partners_as_choices(cls) -> list:
        return [(partner.id, partner.name) for partner in cls.objects.exclude(name=settings.DEFAULT_EMPTY_PARTNER)]

    @classmethod
    def get_partners_for_program_as_choices(cls, business_area_id: str, program_id: str | None = None) -> list:
        partners = cls.objects.exclude(name=settings.DEFAULT_EMPTY_PARTNER)
        if program_id:
            return [
                (partner.id, partner.name)
                for partner in partners
                if program_id in partner.get_program_ids_for_business_area(business_area_id)
            ]
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

    def has_full_area_access_in_program(self, program_id: str | UUID) -> bool:
        return self.is_unicef or (
            self.program_partner_through.filter(program_id=program_id).first()
            and self.program_partner_through.filter(program_id=program_id).first().full_area_access
        )

    def get_program_ids_for_business_area(self, business_area_id: str) -> list[str]:
        return [
            str(program_id)
            for program_id in self.programs.filter(business_area_id=business_area_id).values_list("id", flat=True)
        ]

    def has_program_access(self, program_id: str | UUID) -> bool:
        return self.is_unicef or self.programs.filter(id=program_id).exists()

    def has_area_access(self, area_id: str | UUID, program_id: str | UUID) -> bool:
        return self.is_unicef or self.get_program_areas(program_id).filter(id=area_id).exists()

    def get_program_areas(self, program_id: str | UUID) -> QuerySet[Area]:
        return Area.objects.filter(
            program_partner_through__partner=self, program_partner_through__program_id=program_id
        )

    def get_roles_for_business_area(
        self, business_area_slug: str | None = None, business_area_id: Optional["UUID"] = None
    ) -> QuerySet["Role"]:
        if not business_area_slug and not business_area_id:
            return Role.objects.none()

        if not business_area_id and business_area_slug:
            business_area_id = BusinessArea.objects.get(slug=business_area_slug).id

        return Role.objects.filter(
            business_area_partner_through__partner=self,
            business_area_partner_through__business_area_id=business_area_id,
        )

    def add_roles_in_business_area(self, business_area_id: str, roles: list["Role"]) -> None:
        business_area_partner_through, _ = BusinessAreaPartnerThrough.objects.get_or_create(
            partner=self,
            business_area_id=business_area_id,
        )
        business_area_partner_through.roles.add(*roles)


class User(AbstractUser, NaturalKeyModel, UUIDModel):
    status = models.CharField(choices=USER_STATUS_CHOICES, max_length=10, default=INVITED)
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT)
    email = models.EmailField(_("email address"), unique=True)
    custom_fields = JSONField(default=dict, blank=True)

    job_title = models.CharField(max_length=255, blank=True)
    ad_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True, editable=False)

    last_modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self) -> str:
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email or self.username

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.partner_id:
            self.partner, _ = Partner.objects.get_or_create(name=settings.DEFAULT_EMPTY_PARTNER)
        if not self.partner.pk:
            self.partner.save()
        super().save(*args, **kwargs)

    def permissions_in_business_area(self, business_area_slug: str, program_id: UUID | None = None) -> list:
        """Return list of permissions based on User Role BA and User Partner
        if program_id is in arguments need to check if partner has access to this program.
        """
        user_roles_query = UserRole.objects.filter(user=self, business_area__slug=business_area_slug).exclude(
            expiry_date__lt=timezone.now()
        )
        all_user_roles_permissions_list = list(
            Role.objects.filter(user_roles__in=user_roles_query).values_list("permissions", flat=True)
        )

        # Regular user, need to check access to the program
        if not self.partner.is_unicef:
            # Check program access
            if program_id and not self.partner.has_program_access(program_id):
                return []

            # Prepare partner permissions
            partner_roles_in_ba = self.partner.get_roles_for_business_area(business_area_slug=business_area_slug)
            all_partner_roles_permissions_list = [
                perm for perm in partner_roles_in_ba.values_list("permissions", flat=True) if perm
            ]
        elif all_user_roles_permissions_list:
            # Default partner permissions for UNICEF partner with access to business area
            all_partner_roles_permissions_list = [DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER]
        else:
            all_partner_roles_permissions_list = []
        return list(
            set(
                [perm for perms in all_partner_roles_permissions_list for perm in perms]
                + [perm for perms in all_user_roles_permissions_list if perms for perm in perms]
            )
        )

    @property
    def business_areas(self) -> QuerySet[BusinessArea]:
        return BusinessArea.objects.filter(
            Q(Q(user_roles__user=self) & ~Q(user_roles__expiry_date__lt=timezone.now())) | Q(partners=self.partner)
        ).distinct()

    def has_permission(
        self, permission: str, business_area: BusinessArea, program_id: UUID | None = None, write: bool = False
    ) -> bool:
        return permission in self.permissions_in_business_area(business_area.slug, program_id)

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

    def email_user(  # type: ignore
        self,
        subject: str,
        html_body: str | None = None,
        text_body: str | None = None,
        mailjet_template_id: int | None = None,
        body_variables: dict[str, Any] | None = None,
        from_email: str | None = None,
        from_email_display: str | None = None,
        ccs: list[str] | None = None,
    ) -> None:
        """Send email to this user via Mailjet."""
        email = MailjetClient(
            recipients=[self.email],
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            mailjet_template_id=mailjet_template_id,
            variables=body_variables,
            ccs=ccs,
            from_email=from_email,
            from_email_display=from_email_display,
        )
        email.send_email()

    class Meta:
        permissions = (
            ("can_load_from_ad", "Can load users from ActiveDirectory"),
            ("can_sync_with_ad", "Can synchronise user with ActiveDirectory"),
            ("can_create_kobo_user", "Can create users in Kobo"),
            ("can_import_from_kobo", "Can import and sync users from Kobo"),
            ("can_upload_to_kobo", "Can upload CSV file to Kobo"),
            ("can_debug", "Can access debug information"),
            ("can_inspect", "Can inspect objects"),
            ("quick_links", "Can see quick links in admin"),
            ("restrict_help_desk", "Limit fields to be editable for help desk"),
            ("can_reindex_programs", "Can reindex programs"),
            ("can_add_business_area_to_partner", "Can add business area to partner"),
            ("can_import_fixture", "Can import fixture"),
        )


class HorizontalChoiceArrayField(ArrayField):
    def formfield(self, form_class: Any | None = ..., choices_form_class: Any | None = ..., **kwargs: Any) -> Any:
        widget = FilteredSelectMultiple(self.verbose_name, False)
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "widget": widget,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class UserRole(NaturalKeyModel, TimeStampedUUIDModel):
    user = models.ForeignKey("account.User", related_name="user_roles", on_delete=models.CASCADE)
    role = models.ForeignKey("account.Role", related_name="user_roles", on_delete=models.CASCADE)
    business_area = models.ForeignKey("core.BusinessArea", related_name="user_roles", on_delete=models.CASCADE)
    expiry_date = models.DateField(
        blank=True, null=True, help_text="After expiry date this User Role will be inactive."
    )

    class Meta:
        unique_together = ("business_area", "user", "role")

    def __str__(self) -> str:
        return f"{self.user} {self.role} in {self.business_area}"


class UserGroup(NaturalKeyModel, models.Model):
    user = models.ForeignKey("account.User", related_name="user_groups", on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name="user_groups", on_delete=models.CASCADE)
    business_area = models.ForeignKey("core.BusinessArea", related_name="user_groups", on_delete=models.CASCADE)

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

    def natural_key(self) -> tuple:
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
    def get_roles_as_choices(cls) -> list:
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
    """Keeps track of what roles are incompatible:
    user cannot be assigned both of the roles in the same business area at the same time.
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
            logger.warning(f"Provided roles are the same role={self.role_one}")
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
            logger.warning(
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
            logger.warning(
                f"This combination of roles ({self.role_one}, {self.role_two}) already exists as incompatible pair."
            )
            raise ValidationError(_("This combination of roles already exists as incompatible pair."))
