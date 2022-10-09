import operator
from functools import reduce

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

import factory

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import User, UserGroup
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.power_query.defaults import SYSTEM_PARAMETRIZER
from hct_mis_api.apps.power_query.models import Formatter, Parametrizer, Query, Report


class GroupFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda x: "Group%s" % x)

    class Meta:
        model = Group
        django_get_or_create = ("name",)


class ContentTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = ContentType
        django_get_or_create = ("app_label", "model")


class QueryFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda x: "Query%s" % x)
    owner = factory.SubFactory(UserFactory, is_superuser=True, is_staff=True)
    target = factory.Iterator(ContentType.objects.filter(app_label="auth", model="permission"))
    code = "result=conn.all()"

    class Meta:
        model = Query
        # django_get_or_create = ("name",)


class FormatterFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda x: "Formatter%s" % x)
    content_type = "html"

    class Meta:
        model = Formatter
        django_get_or_create = ("name",)


class ReportFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda x: "Report%s" % x)
    query = factory.Iterator(Query.objects.all())
    formatter = factory.Iterator(Formatter.objects.all())
    owner = factory.SubFactory(UserFactory, is_superuser=True, is_staff=True, password="123")

    class Meta:
        model = Report
        django_get_or_create = ("name",)


class ParametrizerFactory(factory.DjangoModelFactory):
    code = "active-business-areas"
    name = factory.Sequence(lambda x: SYSTEM_PARAMETRIZER["active-business-areas"]["name"])
    value = factory.Sequence(lambda x: SYSTEM_PARAMETRIZER["active-business-areas"]["value"])

    class Meta:
        model = Parametrizer
        django_get_or_create = ("code",)


def get_group(name="Group1", permissions=None):
    group = GroupFactory(name)
    permission_names = permissions or []
    for permission_name in permission_names:
        try:
            app_label, codename = permission_name.split(".")
        except ValueError:
            raise ValueError("Invalid permission name `{0}`".format(permission_name))
    try:
        permission = Permission.objects.get(content_type__app_label=app_label, codename=codename)
    except Permission.DoesNotExist:
        raise Permission.DoesNotExist("Permission `{0}` does not exists", permission_name)

    group.permissions.add(permission)
    return group


class user_grant_permission:
    def __init__(self, user, permissions=None):
        self.user = user
        self.permissions = permissions
        self.group = None

    def __enter__(self):
        if hasattr(self.user, "_group_perm_cache"):
            del self.user._group_perm_cache
        if hasattr(self.user, "_officepermissionchecker"):
            del self.user._officepermissionchecker
        if hasattr(self.user, "_perm_cache"):
            del self.user._perm_cache
        self.group = get_group(permissions=self.permissions or [])
        self.user.groups.add(self.group)

    def __exit__(self, e_typ, e_val, trcbak):
        if all((e_typ, e_val, trcbak)):
            raise e_typ(e_val)
        if self.group:
            self.user.groups.remove(self.group)
            self.group.delete()

    def start(self):
        """Activate a patch, returning any created mock."""
        result = self.__enter__()
        return result

    def stop(self):
        """Stop an active patch."""
        return self.__exit__(None, None, None)


class user_grant_office_permission(object):
    def __init__(self, user: User, office: BusinessArea, permissions):
        self.user = user
        self.office = office
        if isinstance(permissions, str):
            self.permissions = [permissions]
        else:
            self.permissions = permissions

    def __enter__(self):
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

    def __exit__(self, e_typ, e_val, trcbak):
        if all((e_typ, e_val, trcbak)):
            raise e_typ(e_val) from e_val
        if self.group:
            self.user_group.delete()
            self.group.delete()

    def start(self):
        """Activate a patch, returning any created mock."""
        self.__enter__()

    def stop(self):
        """Stop an active patch."""
        return self.__exit__()
