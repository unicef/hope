from typing import TYPE_CHECKING, Any

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from natural_keys import NaturalKeyModel

from hope.models.role_assignment import RoleAssignment
from hope.models.user import User, logger
from hope.models.utils import TimeStampedUUIDModel

if TYPE_CHECKING:
    from hope.models.business_area import BusinessArea


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
                        f"This role is incompatible with "
                        f"{', '.join([userrole.role.name for userrole in incompatible_userroles])}"
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
        app_label = "account"
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
