"""Which grievance tickets a user may see: the global list, the detail view and the My Tasks email share it."""

from collections import defaultdict
from collections.abc import Collection, Sequence
from typing import TYPE_CHECKING, Any

from django.db.models import Exists, OuterRef, Q

from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import Program, RoleAssignment

if TYPE_CHECKING:
    from hope.models import BusinessArea, User

# all / as creator / as owner, non-sensitive first then sensitive - the order visible_tickets_q() reads
VIEW_LIST_PERMISSIONS = (
    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
)


def program_ids_by_permission(user: "User", business_area: "BusinessArea") -> dict[str, set[Any]]:
    """Return {permission: program ids} for the user's and their partner's role assignments in the business area.

    A role assignment without a program covers all programs of the business area, like
    User.get_program_ids_for_permissions_in_business_area. That method is one or two queries per permission;
    visible_tickets_q and the My Tasks tab scopes need up to 30 of them per request, so this resolves them all
    at once and caches the result on the user instance.
    """
    cache: dict[Any, dict[str, set[Any]]] = user.__dict__.setdefault("_grievance_program_ids_cache", {})
    if business_area.id not in cache:
        assignments = list(
            RoleAssignment.objects.filter(
                Q(user=user) | Q(partner__user=user), business_area=business_area
            ).values_list("program_id", "role__permissions")
        )
        every_program_id: set[Any] = set()
        if any(program_id is None for program_id, _ in assignments):
            every_program_id = set(Program.objects.filter(business_area=business_area).values_list("id", flat=True))
        by_permission: dict[str, set[Any]] = defaultdict(set)
        for program_id, permissions in assignments:
            for permission in permissions:
                by_permission[permission].update(every_program_id if program_id is None else {program_id})
        cache[business_area.id] = dict(by_permission)
    return cache[business_area.id]


def _program_ids_for(user: "User", business_area: "BusinessArea", permission: Permissions) -> set[Any]:
    return program_ids_by_permission(user, business_area).get(permission.value, set())


def in_programs_q(program_ids: Collection[Any]) -> Q:
    through_model = GrievanceTicket.programs.through
    return Q(Exists(through_model.objects.filter(grievanceticket=OuterRef("pk"), program_id__in=program_ids)))


def without_program_q() -> Q:
    through_model = GrievanceTicket.programs.through
    return ~Q(Exists(through_model.objects.filter(grievanceticket=OuterRef("pk"))))


def visible_tickets_q(user: "User", business_area: "BusinessArea", permissions: Sequence[Permissions]) -> Q:
    """Tickets `user` may see under a six-permission set (all / creator / owner, non-sensitive then sensitive).

    A programme-scoped grant covers that programme's tickets plus the ones in no programme.
    """
    is_sensitive = Q(category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE)
    scopes = (
        (permissions[0], Q(), ~is_sensitive),
        (permissions[1], Q(created_by=user), ~is_sensitive),
        (permissions[2], Q(assigned_to=user), ~is_sensitive),
        (permissions[3], Q(), is_sensitive),
        (permissions[4], Q(created_by=user), is_sensitive),
        (permissions[5], Q(assigned_to=user), is_sensitive),
    )
    visible = Q()
    for permission, role_scope, category_scope in scopes:
        program_ids = _program_ids_for(user, business_area, permission)
        if program_ids:
            visible |= (in_programs_q(program_ids) | without_program_q()) & role_scope & category_scope
    return visible
