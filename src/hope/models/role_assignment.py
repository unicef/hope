from typing import Any

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from natural_keys import NaturalKeyModel

from hope.models.utils import TimeStampedUUIDModel


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
        app_label = "account"
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
