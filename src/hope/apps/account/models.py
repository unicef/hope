import logging
from functools import lru_cache
from typing import Any
from uuid import UUID

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import AbstractUser, Group, Permission
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
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from natural_keys import NaturalKeyModel

from hope.apps.account.fields import ChoiceArrayField
from hope.apps.account.permissions import Permissions
from hope.apps.account.utils import test_conditional
from hope.apps.core.mixins import LimitBusinessAreaModelMixin
from hope.apps.core.models import BusinessArea
from hope.apps.core.visibility_backends import VisibilityBackend
from hope.apps.geo.models import Area
from hope.apps.utils.mailjet import MailjetClient
from hope.apps.utils.models import TimeStampedUUIDModel
from hope.apps.utils.validators import DoubleSpaceValidator, StartEndSpaceValidator

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

    def __str__(self) -> str:
        return f"{self.name} [Sub-Partner of {self.parent.name}]" if self.parent else self.name

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Partner cannot be a parent if it has RoleAssignments
        if self.parent:
            if RoleAssignment.objects.filter(partner=self.parent).exists():
                raise ValidationError(f"{self.parent} cannot become a parent as it has RoleAssignments.")
            if self.parent.user_set.exists():
                raise ValidationError(f"{self.parent} cannot become a parent as it has users.")
        super().save(*args, **kwargs)

    @property
    def is_child(self) -> bool:
        return self.parent is None

    @property
    def is_unicef_subpartner(self) -> bool:
        return self.parent and self.parent.is_unicef

    @property
    def is_parent(self) -> bool:
        return self.id in Partner.objects.exclude(parent__isnull=True).values_list("parent", flat=True)

    @classmethod
    def get_partners_as_choices(cls) -> list:
        return [(partner.id, partner.name) for partner in cls.objects.exclude(name=settings.DEFAULT_EMPTY_PARTNER)]

    @classmethod
    def get_partners_for_program_as_choices(cls, business_area_id: str, program_id: str | None = None) -> list:
        role_assignments = RoleAssignment.objects.filter(business_area_id=business_area_id)
        if program_id:
            role_assignments = role_assignments.filter(Q(program_id=program_id) | Q(program=None))
        partners = cls.objects.filter(role_assignments__in=role_assignments).order_by("name").distinct()

        return [(partner.id, partner.name) for partner in partners]

    @property
    def is_unicef(self) -> bool:
        return self.name == "UNICEF"

    @property
    def is_default(self) -> bool:
        return self.name == settings.DEFAULT_EMPTY_PARTNER

    @property
    def is_editable(self) -> bool:
        return not self.is_unicef and not self.is_default

    def get_program_ids_for_business_area(self, business_area_id: str) -> list[str]:
        from hope.apps.program.models import Program

        if not hasattr(self, "_program_ids_for_business_area_cache"):
            self._program_ids_for_business_area_cache = {}
        if business_area_id in self._program_ids_for_business_area_cache:
            return self._program_ids_for_business_area_cache[business_area_id]

        if self.role_assignments.filter(business_area_id=business_area_id, program=None).exists():
            programs_ids = (
                Program.objects.filter(business_area_id=business_area_id).order_by("id").values_list("id", flat=True)
            )
        else:
            programs_ids = (
                self.role_assignments.filter(business_area_id=business_area_id)
                .order_by("program_id")
                .values_list("program_id", flat=True)
            )
        program_ids_list = [str(program_id) for program_id in programs_ids]

        self._program_ids_for_business_area_cache[business_area_id] = program_ids_list

        return program_ids_list

    def get_program_ids_for_permissions_in_business_area(
        self, business_area_id: str, permissions: list[Permissions]
    ) -> list[str]:
        """Return list of program ids that the partner has permissions for in the given business area."""
        from hope.apps.program.models import Program

        permission_filter = Q(role__permissions__overlap=[perm.value for perm in permissions])

        if self.role_assignments.filter(permission_filter, business_area_id=business_area_id, program=None).exists():
            programs_ids = Program.objects.filter(business_area_id=business_area_id).values_list("id", flat=True)
        else:
            programs_ids = self.role_assignments.filter(
                permission_filter, business_area_id=business_area_id
            ).values_list("program_id", flat=True)
        return [str(program_id) for program_id in programs_ids]

    def has_area_access(self, area_id: str | UUID, program_id: str | UUID) -> bool:
        return VisibilityBackend.has_area_access(self, area_id, program_id)

    def get_area_limits_for_program(self, program_id: str | UUID) -> QuerySet[Area]:
        return VisibilityBackend.get_area_limits_for_program(self, program_id)

    def has_area_limits_in_program(self, program_id: str | UUID) -> bool:
        return VisibilityBackend.has_area_limits_in_program(self, program_id)

    def get_areas_for_program(self, program_id: str | UUID) -> QuerySet[Area]:
        return VisibilityBackend.get_areas_for_program(self, program_id)


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
        if self.partner and self.partner.is_parent:
            raise ValidationError(f"{self.partner} is a parent partner and cannot have users.")
        super().save(*args, **kwargs)

    def get_program_ids_for_business_area(self, business_area_id: str) -> list[str]:
        """Return list of program ids that the user (or user's partner) has access to in the given business area."""
        from hope.apps.program.models import Program

        if not hasattr(self, "_program_ids_for_business_area_cache"):
            self._program_ids_for_business_area_cache = {}
        if business_area_id in self._program_ids_for_business_area_cache:
            return self._program_ids_for_business_area_cache[business_area_id]

        if RoleAssignment.objects.filter(
            Q(user=self) | Q(partner__user=self),
            business_area_id=business_area_id,
            program=None,
        ).exists():
            programs_ids = (
                Program.objects.filter(business_area_id=business_area_id).order_by("id").values_list("id", flat=True)
            )
        else:
            programs_ids = (
                RoleAssignment.objects.filter(
                    Q(user=self) | Q(partner__user=self),
                    business_area_id=business_area_id,
                )
                .order_by("program_id")
                .values_list("program_id", flat=True)
            )

        program_ids_list = [str(program_id) for program_id in programs_ids]
        self._program_ids_for_business_area_cache[business_area_id] = program_ids_list
        return program_ids_list

    def get_program_ids_for_permissions_in_business_area(
        self, business_area_id: str, permissions: list[Permissions]
    ) -> list[str]:
        """Return list of program ids that the user (or user's partner) has permissions for in the given business area."""
        from hope.apps.program.models import Program

        permission_filter = Q(role__permissions__overlap=[perm.value for perm in permissions])

        if RoleAssignment.objects.filter(
            permission_filter,
            Q(user=self) | Q(partner__user=self),
            business_area_id=business_area_id,
            program=None,
        ).exists():
            programs_ids = Program.objects.filter(business_area_id=business_area_id).values_list("id", flat=True)
        else:
            programs_ids = RoleAssignment.objects.filter(
                permission_filter,
                Q(user=self) | Q(partner__user=self),
                business_area_id=business_area_id,
            ).values_list("program_id", flat=True)
        return [str(program_id) for program_id in programs_ids]

    def permissions_in_business_area(self, business_area_slug: str, program_id: UUID | str | None = None) -> set:
        """Return list of permissions for the given business area and program.

        retrieved from RoleAssignments of the user and their partner
        """
        if program_id:
            role_assignments = RoleAssignment.objects.filter(
                Q(
                    partner__user=self,
                    business_area__slug=business_area_slug,
                    program_id=program_id,
                )
                | Q(
                    partner__user=self,
                    business_area__slug=business_area_slug,
                    program=None,
                )
                | Q(
                    user=self,
                    business_area__slug=business_area_slug,
                    program_id=program_id,
                )
                | Q(user=self, business_area__slug=business_area_slug, program=None)
            ).exclude(expiry_date__lt=timezone.now())
        else:
            role_assignments = RoleAssignment.objects.filter(
                Q(partner__user=self, business_area__slug=business_area_slug)
                | Q(user=self, business_area__slug=business_area_slug)
            ).exclude(expiry_date__lt=timezone.now())

        permissions_set = set()
        # permissions from group field in RoleAssignment
        role_assignment_group_permissions = Permission.objects.filter(
            group__role_assignments__in=role_assignments
        ).values_list("content_type__app_label", "codename")
        permissions_set.update(f"{app}.{codename}" for app, codename in role_assignment_group_permissions)

        # permissions from role field in RoleAssignment
        role_assignment_role_permissions = Role.objects.filter(
            role_assignments__in=role_assignments, permissions__isnull=False
        ).values_list("permissions", flat=True)
        permissions_set.update(
            permission for permission_list in role_assignment_role_permissions for permission in permission_list
        )
        return permissions_set

    @property
    def business_areas(self) -> QuerySet[BusinessArea]:
        role_assignments = RoleAssignment.objects.filter(Q(user=self) | Q(partner__user=self)).exclude(
            expiry_date__lt=timezone.now()
        )
        return BusinessArea.objects.filter(role_assignments__in=role_assignments).exclude(active=False).distinct()

    @test_conditional(lru_cache())
    def cached_role_assignments(self) -> QuerySet["RoleAssignment"]:
        return self.role_assignments.all().select_related("business_area")

    def can_download_storage_files(self) -> bool:
        return any(
            self.has_perm(Permissions.DOWNLOAD_STORAGE_FILE.name, role.business_area)
            for role in self.cached_role_assignments()
        )

    def can_change_fsp(self) -> bool:
        return any(
            self.has_perm(
                Permissions.PM_ADMIN_FINANCIAL_SERVICE_PROVIDER_UPDATE.name,
                role.business_area,
            )
            for role in self.cached_role_assignments()
        )

    def can_add_business_area_to_partner(self) -> bool:
        return any(
            self.has_perm(Permissions.CAN_ADD_BUSINESS_AREA_TO_PARTNER.name, role.business_area)
            for role in self.cached_role_assignments()
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
            ("can_change_allowed_partners", "Can change allowed partners"),
            ("can_change_area_limits", "Can change area limits"),
            ("can_import_fixture", "Can import fixture"),
        )


class HorizontalChoiceArrayField(ArrayField):
    def formfield(
        self,
        form_class: Any | None = ...,
        choices_form_class: Any | None = ...,
        **kwargs: Any,
    ) -> Any:
        widget = FilteredSelectMultiple(self.verbose_name, False)
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "widget": widget,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class RoleAssignment(NaturalKeyModel, TimeStampedUUIDModel):
    """Model to represent the assignment of a role to a user or partner within a specific business area or program.

    When program is NULL, the role is assigned to the user or partner in all programs within the business area.
    This model also associates the role with an expiry date and a group, if applicable.
    """

    business_area = models.ForeignKey("core.BusinessArea", related_name="role_assignments", on_delete=models.CASCADE)
    user = models.ForeignKey(
        "account.User",
        related_name="role_assignments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    partner = models.ForeignKey(
        "account.Partner",
        related_name="role_assignments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    role = models.ForeignKey(
        "account.Role",
        related_name="role_assignments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    program = models.ForeignKey(
        "program.Program",
        related_name="role_assignments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    expiry_date = models.DateField(
        blank=True,
        null=True,
        help_text="After expiry date this Role Assignment will be inactive.",
    )
    group = models.ForeignKey(
        Group,
        related_name="role_assignments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            # Either user or partner should be assigned; not both
            models.CheckConstraint(
                check=Q(user__isnull=False, partner__isnull=True) | Q(user__isnull=True, partner__isnull=False),
                name="user_or_partner_not_both",
            ),
            # Unique constraint for user + role + business_area + program when program is NOT NULL
            models.UniqueConstraint(
                fields=["user", "role", "business_area", "program"],
                name="unique_user_role_business_area_program",
                condition=Q(user__isnull=False),
            ),
            # Unique constraint for user + role + business_area when program is NULL
            models.UniqueConstraint(
                fields=["user", "role", "business_area"],
                name="unique_user_role_business_area_no_program",
                condition=Q(user__isnull=False, program__isnull=True),
            ),
            # Unique constraint for partner + role + business_area + program when program is NOT NULL
            models.UniqueConstraint(
                fields=["partner", "role", "business_area", "program"],
                name="unique_partner_role_business_area_program",
                condition=Q(partner__isnull=False),
            ),
            # Unique constraint for partner + role + business_area when program is NULL
            models.UniqueConstraint(
                fields=["partner", "role", "business_area"],
                name="unique_partner_role_business_area_no_program",
                condition=Q(partner__isnull=False, program__isnull=True),
            ),
        ]

    def clean(self) -> None:
        super().clean()
        errors = []
        # Ensure either user or partner is set, but not both
        if bool(self.user) == bool(self.partner):
            errors.append("Either user or partner must be set, but not both.")
        # Ensure partner can only be assigned roles that have flag is_available_for_partner as True
        if (
            self.partner
            and not self.partner.is_unicef_subpartner
            and self.role
            and not self.role.is_available_for_partner
        ):
            errors.append("Partner can only be assigned roles that are available for partners.")
        if self.partner:
            # Validate that business_area is within the partner's allowed_business_areas
            if not self.partner.allowed_business_areas.filter(id=self.business_area.id).exists():
                errors.append(f"{self.business_area} is not within the allowed business areas for {self.partner}.")
            # Only partners that are not parents can have role assignments
            if self.partner.is_parent:
                errors.append(f"{self.partner} is a parent partner and cannot have role assignments.")

        if errors:
            raise ValidationError(errors)

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        role_holder = self.user or self.partner
        return f"{role_holder} {self.role} in {self.business_area}"


class AdminAreaLimitedTo(TimeStampedUUIDModel):
    """Model to limit the admin area access for a partner.

    Partners with full area access for a certain program will not have any area limits - no record in this model.
    """

    partner = models.ForeignKey("account.Partner", related_name="admin_area_limits", on_delete=models.CASCADE)
    program = models.ForeignKey("program.Program", related_name="admin_area_limits", on_delete=models.CASCADE)
    areas = models.ManyToManyField("geo.Area", related_name="admin_area_limits", blank=True)

    class Meta:
        unique_together = ("partner", "program")

    def clean(self) -> None:
        if self.program.partner_access != self.program.SELECTED_PARTNERS_ACCESS:
            raise ValidationError(f"Area limits cannot be set for programs with {self.program.partner_access} access.")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)


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
    is_visible_on_ui = models.BooleanField(default=True)
    is_available_for_partner = models.BooleanField(default=True)

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
    def validate_user_role(self, user: User, business_area: "BusinessArea", role: RoleAssignment) -> None:
        incompatible_roles = list(
            IncompatibleRoles.objects.filter(role_one=role).values_list("role_two", flat=True)
        ) + list(IncompatibleRoles.objects.filter(role_two=role).values_list("role_one", flat=True))
        incompatible_userroles = RoleAssignment.objects.filter(
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
    """Keep track of what roles are incompatible.

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
            logger.warning(f"Provided roles are the same role={self.role_one}")
            raise ValidationError(_("Choose two different roles."))
        failing_users = set()

        for role_pair in (
            (self.role_one, self.role_two),
            (self.role_two, self.role_one),
        ):
            for userrole in RoleAssignment.objects.filter(role=role_pair[0]):
                if RoleAssignment.objects.filter(
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
