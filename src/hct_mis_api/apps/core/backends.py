from typing import Optional, TYPE_CHECKING

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import Permission, AnonymousUser
from django.core.cache import cache
from django.db.models import Q, Model
from django.utils import timezone

from hct_mis_api.api.caches import get_or_create_cache_key
from hct_mis_api.apps.account.caches import get_user_permissions_version_key, get_user_permissions_cache_key
from hct_mis_api.apps.account.models import RoleAssignment, User
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.models import Program

if TYPE_CHECKING:
    from hct_mis_api.apps.account.models import User


class PermissionsBackend(BaseBackend):
    def get_all_permissions(self, user: "User", obj: "Model|None" = None) -> set[str]:
        if not obj:
            program = None
            business_area = None
            filters = {}
        else:
            if isinstance(obj, BusinessArea):
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

        # If user does not have access to program, return empty set
        if program and not RoleAssignment.objects.filter(
                partner=user.partner,
                program=program,
                expiry_date__gt=timezone.now()
        ).exists():
            return set()

        """
        The permissions are fetched from:
        * the user's Group
        * RoleAssignment - where they can be stored either on the Group or on the Role
          and assigned either to the User or to their Partner
        """
        permissions_set = set()

        # permissions from the User's Group
        user_group_permissions = Permission.objects.filter(
            group__users=user
        ).values_list("content_type__app_label", "codename")
        permissions_set.update(f"{app}.{codename}" for app, codename in user_group_permissions)

        # role assignments from the User or their Partner
        role_assignments = RoleAssignment.objects.filter(
            (Q(user=user) | Q(partner__user=user))
            & (Q(business_area=filters.get('business_area'), program=None) | Q(**filters))
        ).exclude(expiry_date__gt=timezone.now())

        # permissions from the RoleAssignments' Groups
        role_group_permissions = Permission.objects.filter(
            group__role_assignments__in=role_assignments
        ).values_list("content_type__app_label", "codename")
        permissions_set.update(f"{app}.{codename}" for app, codename in role_group_permissions)

        # permissions from RoleAssignment's Roles
        for role_assignment in role_assignments:
            role_permissions = role_assignment.role.permissions
            permissions_set.update(role_permissions)

        cache.set(cache_key, permissions_set, timeout=None)

        return permissions_set

    def has_perm(self, user_obj: "User|AnonymousUser", perm: str, obj: Optional[Model] = None) -> bool:
        if user_obj.is_superuser:
            return True
        if isinstance(user_obj, AnonymousUser):
            return False
        return super().has_perm(user_obj, perm, obj)
