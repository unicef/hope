from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from hope.models import RoleAssignment, User

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import QuerySet

    from hope.apps.account.permissions import Permissions
    from hope.models import BusinessArea


def is_mailable(user: User | None) -> bool:
    return user is not None and user.is_active and bool(user.email)


def users_with_permissions(
    business_area: "BusinessArea",
    permissions: "Sequence[Permissions | str]",
    programs: "Sequence[Any]" = (),
    *,
    exclude_staff: bool = False,
) -> "QuerySet[User]":
    """Mailable users holding any of `permissions` in `business_area`, directly or through their partner.

    Deactivated users and users without an email address are always dropped. `programs` narrows role
    assignments to business-area-wide ones plus those scoped to the given programs; an empty value
    applies no program restriction. `exclude_staff` additionally drops staff accounts on prod, where
    superusers are always dropped.
    """
    permission_values = [getattr(permission, "value", permission) for permission in permissions]
    program_ids = [getattr(program, "pk", program) for program in programs]
    program_scope = Q(program__isnull=True) | Q(program__in=program_ids) if program_ids else Q()

    role_assignments = (
        RoleAssignment.objects.filter(
            program_scope,
            role__permissions__overlap=permission_values,
            business_area=business_area,
        )
        .exclude(expiry_date__lt=timezone.now())
        .distinct()
    )
    users = (
        User.objects.filter(
            Q(role_assignments__in=role_assignments) | Q(partner__role_assignments__in=role_assignments)
        )
        .filter(is_active=True)
        .exclude(email="")
    )
    if settings.ENV == "prod":
        users = (
            users.exclude(Q(is_superuser=True) | Q(is_staff=True))
            if exclude_staff
            else users.exclude(is_superuser=True)
        )
    return users.distinct()
