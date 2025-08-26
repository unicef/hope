from typing import Any

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AnonymousUser, Permission
from django.core.cache import cache
from django.db.models import Model, Q
from django.utils import timezone

from hope.api.caches import get_or_create_cache_key
from hope.apps.account.caches import (
    get_user_permissions_cache_key,
    get_user_permissions_version_key,
)
from hope.models.user import User
from hope.models.role_assignment import RoleAssignment
from hope.models.role import Role
from hope.models.business_area import BusinessArea
from hope.models.program import Program


class PermissionsBackend(BaseBackend):
    """Custom permissions backend that fetches permissions from the User's Groups and the RoleAssignments.

    for the User or their Partner.
    """

    def get_all_permissions(self, user: User, obj: Model | None = None) -> set[str]:  # type: ignore
        filters: dict[str, Any]
        if not obj:
            program = None
            business_area = None
            filters = {}
        elif isinstance(obj, BusinessArea):
            program = None
            business_area = obj
            filters = {"business_area": business_area}
        elif isinstance(obj, Program):
            program = obj
            business_area = obj.business_area
            filters = {
                "business_area": business_area,
                "program": program,
            }
        elif hasattr(obj, "program"):
            program = obj.program
            business_area = obj.business_area
            filters = {"business_area": business_area, "program": program}
        elif hasattr(obj, "business_area"):
            program = None
            business_area = obj.business_area
            filters = {"business_area": business_area}
        else:
            return set()

        user_version = get_or_create_cache_key(get_user_permissions_version_key(user), 1)
        cache_key = get_user_permissions_cache_key(user, user_version, business_area, program)

        cached_permissions = cache.get(cache_key)

        if cached_permissions:
            return cached_permissions

        # If permission is checked for a Program and User does not have access to it, return empty set
        if (
            program
            and not RoleAssignment.objects.filter(
                (Q(partner=user.partner) | Q(user=user))
                & Q(business_area=business_area)
                & (Q(program=None) | Q(program=program))
            )
            .exclude(expiry_date__lt=timezone.now())
            .exists()
        ):
            return set()

        """
        The permissions are fetched from:
        * the user's Groups
        * RoleAssignment - where they can be stored either on the Group or on the Role
          and assigned either to the User or to their Partner
        """

        # role assignments from the User or their Partner
        role_assignments = RoleAssignment.objects.filter(
            (Q(user=user) | Q(partner__user=user))
            & (Q(business_area=filters.get("business_area"), program=None) | Q(**filters))
        ).exclude(expiry_date__lt=timezone.now())

        if business_area and not role_assignments.exists():
            return set()

        permissions_set = set()

        # permissions from the RoleAssignments' Groups
        role_assignment_group_permissions = Permission.objects.filter(
            group__role_assignments__in=role_assignments
        ).values_list("content_type__app_label", "codename")
        permissions_set.update(f"{app}.{codename}" for app, codename in role_assignment_group_permissions)

        # permissions from RoleAssignment's Roles
        role_assignment_role_permissions = Role.objects.filter(
            role_assignments__in=role_assignments, permissions__isnull=False
        ).values_list("permissions", flat=True)
        permissions_set.update(
            permission for permission_list in role_assignment_role_permissions for permission in permission_list
        )

        # permissions from the User's Group
        user_group_permissions = Permission.objects.filter(group__user=user).values_list(
            "content_type__app_label", "codename"
        )
        permissions_set.update(f"{app}.{codename}" for app, codename in user_group_permissions)

        cache.set(cache_key, permissions_set, timeout=None)

        return permissions_set

    def has_perm(self, user_obj: User | AnonymousUser, perm: str, obj: Model | None = None) -> bool:  # type: ignore
        if user_obj.is_superuser:
            return True
        if isinstance(user_obj, AnonymousUser):
            return False
        return super().has_perm(user_obj, perm, obj)
