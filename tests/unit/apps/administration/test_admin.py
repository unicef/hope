from typing import TYPE_CHECKING, Any, Dict, Iterable, Tuple

import factory
from django.contrib.admin import ModelAdmin, site
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import reverse
from django_webtest import WebTest
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from factory.base import FactoryMetaClass
from parameterized import parameterized

from hope.apps.account.models import Role, RoleAssignment, User
from hope.apps.account.permissions import Permissions

if TYPE_CHECKING:
    from hope.apps.core.models import BusinessArea

EXCLUDED_MODELS = []

factories_registry = {}


class AutoRegisterFactoryMetaClass(FactoryMetaClass):
    def __new__(mcs, class_name: str, bases: object, attrs: Dict) -> object:  # noqa
        new_class = super().__new__(mcs, class_name, bases, attrs)
        factories_registry[new_class._meta.model] = new_class
        return new_class


class ModelFactory(factory.django.DjangoModelFactory, metaclass=AutoRegisterFactoryMetaClass):
    pass


def get_factory_for_model(_model: Any) -> object:
    class Meta:
        model = _model

    if _model in factories_registry:
        return factories_registry[_model]
    return type("AAA", (ModelFactory,), {"Meta": Meta})


def model_admins() -> Tuple:
    m = []
    for model, admin in site._registry.items():
        if model.__name__ not in EXCLUDED_MODELS:
            m.append((model.__name__, admin))
    return tuple(m)


class TestAdminSite(WebTest):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.superuser: User = UserFactory(is_superuser=True, is_staff=True)
        cls.business_area = create_afghanistan()

    @staticmethod
    def create_user_role_with_permissions(
        user: "User", permissions: Iterable, business_area: "BusinessArea"
    ) -> RoleAssignment:
        permission_list = [perm.value for perm in permissions]
        role, created = Role.objects.update_or_create(
            name="Role with Permissions", defaults={"permissions": permission_list}
        )
        user_role, _ = RoleAssignment.objects.get_or_create(user=user, role=role, business_area=business_area)
        return user_role

    @parameterized.expand(model_admins)
    def test_changelist(self, name: str, model_admin: ModelAdmin) -> None:
        self.create_user_role_with_permissions(self.superuser, [Permissions.DOWNLOAD_STORAGE_FILE], self.business_area)
        url = reverse(admin_urlname(model_admin.model._meta, "changelist"))  # type: ignore # str vs SafeString
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200
