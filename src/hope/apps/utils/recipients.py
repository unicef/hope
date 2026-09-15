from collections import defaultdict
from typing import TYPE_CHECKING, Any, TypeIs

from constance import config
from django.db.models import Q
from django.utils import timezone

from hope.models import RoleAssignment, User

if TYPE_CHECKING:
    from collections.abc import Collection, Sequence

    from django.db.models import QuerySet

    from hope.apps.account.permissions import Permissions
    from hope.models import BusinessArea


def is_mailable(user: User | None) -> TypeIs[User]:
    return user is not None and user.is_active and bool(user.email)


def _role_assignments(
    business_area: "BusinessArea",
    permissions: "Sequence[Permissions | str]",
    programs: "Collection[Any]" = (),
) -> "QuerySet[RoleAssignment]":
    permission_values = [getattr(permission, "value", permission) for permission in permissions]
    program_ids = [getattr(program, "pk", program) for program in programs]
    program_scope = Q(program__isnull=True) | Q(program__in=program_ids) if program_ids else Q()
    return (
        RoleAssignment.objects.filter(
            program_scope,
            role__permissions__overlap=permission_values,
            business_area=business_area,
        )
        .exclude(expiry_date__lt=timezone.now())
        .distinct()
    )


def users_with_permissions(
    business_area: "BusinessArea",
    permissions: "Sequence[Permissions | str]",
    programs: "Collection[Any]" = (),
    *,
    exclude_staff: bool = False,
) -> "QuerySet[User]":
    """Mailable users holding any of `permissions` in `business_area`, directly or through their partner.

    Deactivated users and users without an email address are always dropped. `programs` narrows role
    assignments to business-area-wide ones plus those scoped to the given programs; an empty value
    applies no program restriction. Unless `NOTIFY_INTERNAL_USERS` is on, superusers are dropped and
    `exclude_staff` additionally drops staff accounts.
    """
    role_assignments = _role_assignments(business_area, permissions, programs)
    users = (
        User.objects.filter(
            Q(role_assignments__in=role_assignments) | Q(partner__role_assignments__in=role_assignments)
        )
        .filter(is_active=True)
        .exclude(email="")
    )
    if not config.NOTIFY_INTERNAL_USERS:
        users = (
            users.exclude(Q(is_superuser=True) | Q(is_staff=True))
            if exclude_staff
            else users.exclude(is_superuser=True)
        )
    return users.distinct()


def users_with_permissions_by_program(
    business_area: "BusinessArea",
    permissions: "Sequence[Permissions | str]",
    programs: "Collection[Any]",
    *,
    exclude_staff: bool = False,
) -> dict[User, set[Any]]:
    """Map each user from `users_with_permissions` to which of `programs` they cover.

    Two queries regardless of how many programs are asked about, rather than one lookup per program.
    A business-area-wide role assignment covers every program in `programs`; a user holding no
    assignment over any of them is left out.
    """
    program_ids = {getattr(program, "pk", program) for program in programs}
    if not program_ids:
        return {}

    programs_by_user_id: dict[Any, set[Any]] = defaultdict(set)
    programs_by_partner_id: dict[Any, set[Any]] = defaultdict(set)
    for user_id, partner_id, program_id in _role_assignments(business_area, permissions, program_ids).values_list(
        "user_id", "partner_id", "program_id"
    ):
        covered = program_ids if program_id is None else {program_id}
        if user_id is not None:
            programs_by_user_id[user_id].update(covered)
        if partner_id is not None:
            programs_by_partner_id[partner_id].update(covered)

    scope_by_user = {}
    for user in users_with_permissions(business_area, permissions, program_ids, exclude_staff=exclude_staff):
        covered_by_user = programs_by_user_id.get(user.pk, set()) | programs_by_partner_id.get(user.partner_id, set())
        if covered_by_user:
            scope_by_user[user] = covered_by_user
    return scope_by_user
