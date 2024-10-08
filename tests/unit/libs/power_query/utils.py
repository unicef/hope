import operator
from functools import reduce
from typing import Any

from django.contrib.auth.models import Group, Permission
from django.db.models import Q

from hct_mis_api.apps.account.models import User, UserGroup
from hct_mis_api.apps.core.models import BusinessArea


class user_grant_office_permission(object):
    def __init__(self, user: User, office: BusinessArea, permissions: Any) -> None:
        self.user = user
        self.office = office
        if isinstance(permissions, str):
            self.permissions = [permissions]
        else:
            self.permissions = permissions

    def __enter__(self) -> None:
        if hasattr(self.user, "_group_perm_cache"):
            del self.user._group_perm_cache

        if hasattr(self.user, "_perm_cache"):
            del self.user._perm_cache

        key = f"_perm_{self.office.slug}"
        if hasattr(self.user, key):
            delattr(self.user, key)

        or_queries = []
        if self.permissions:
            self.group, _ = Group.objects.get_or_create(name="context_group")

            for permission in self.permissions:
                app, perm = permission.split(".")
                or_queries.append(Q(**{"codename": perm, "content_type__app_label": app}))
            self.group.permissions.set(Permission.objects.filter(reduce(operator.or_, or_queries)))
            self.group.save()
            self.user_group, _ = UserGroup.objects.get_or_create(
                user=self.user, group=self.group, business_area=self.office
            )

    def __exit__(self, e_typ: Any = None, e_val: Any = None, trcbak: Any = None) -> None:
        if all((e_typ, e_val, trcbak)):
            raise e_typ(e_val) from e_val
        if self.group:
            self.user_group.delete()
            self.group.delete()

    def start(self) -> None:
        """Activate a patch, returning any created mock."""
        self.__enter__()

    def stop(self) -> None:
        """Stop an active patch."""
        return self.__exit__()
