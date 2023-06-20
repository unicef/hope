from typing import TYPE_CHECKING, Any, Optional, Union

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission
from django.db.models import Model

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.power_query.models import Report, ReportDocument

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser, AnonymousUser


class PowerQueryBackend(ModelBackend):
    def get_office_permissions(self, user_obj: User, office_slug: str) -> Any:
        key = f"_perm_{office_slug}"
        if not hasattr(user_obj, key):
            permissions = Permission.objects.filter(
                group__user_groups__user=user_obj, group__user_groups__business_area__slug=office_slug
            )
            setattr(
                user_obj,
                key,
                {
                    f"{ct}.{name}"
                    for ct, name in permissions.values_list("content_type__app_label", "codename").order_by()
                },
            )
        return getattr(user_obj, key)

    def has_perm(
        self, user_obj: Union["AbstractBaseUser", "AnonymousUser"], perm: str, obj: Optional[Model] = None
    ) -> bool:
        if not isinstance(user_obj, User):
            return False
        if isinstance(obj, Report):
            if obj.owner == user_obj or obj.limit_access_to.filter(pk=user_obj.pk).exists():
                return True
        elif isinstance(obj, ReportDocument):
            if obj.report.owner == user_obj or obj.limit_access_to.filter(pk=user_obj.pk).exists():
                return True
            if "business_area" not in obj.arguments:
                return False
            if "business_area" in obj.arguments:
                ba = obj.arguments["business_area"]
                return user_obj.is_active and perm in self.get_office_permissions(user_obj, ba)
        return False
