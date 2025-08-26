import logging
from functools import lru_cache
from typing import Any
from uuid import UUID

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import JSONField, Q, QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.models import UUIDModel
from natural_keys import NaturalKeyModel

from hope.apps.account.permissions import Permissions
from hope.apps.account.utils import test_conditional
from hope.models.business_area import BusinessArea
from hope.apps.utils.mailjet import MailjetClient
from hope.models.partner import Partner
from hope.models.role import Role
from hope.models.role_assignment import RoleAssignment

logger = logging.getLogger(__name__)

INVITED = "INVITED"
ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"
USER_STATUS_CHOICES = (
    (ACTIVE, _("Active")),
    (INACTIVE, _("Inactive")),
    (INVITED, _("Invited")),
)


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
        from hope.models.program import Program

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
        from hope.models.program import Program

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
        app_label = "account"
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
