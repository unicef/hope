from typing import Any
from uuid import UUID

from hope.apps.core.mixins import LimitBusinessAreaModelMixin
from django.conf import settings
from django.contrib.postgres.fields import CICharField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from hope.apps.account.permissions import Permissions

from hope.apps.core.visibility_backends import VisibilityBackend
from hope.models.role_assignment import RoleAssignment
from hope.models.area import Area


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

    class Meta:
        app_label = "account"

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
        from hope.models.program import Program

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
        from hope.models.program import Program

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
