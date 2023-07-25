from typing import Any, Dict, Iterable, Tuple

from django.contrib.admin import ModelAdmin, site
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import reverse

import factory
from django_webtest import WebTest
from factory.base import FactoryMetaClass
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import Role, User, UserRole
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea

EXCLUDED_MODELS = []

factories_registry = {}


class AutoRegisterFactoryMetaClass(FactoryMetaClass):
    def __new__(mcs, class_name: str, bases: object, attrs: Dict) -> object:
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
    databases = [
        "default",
        "cash_assist_datahub_ca",
        "cash_assist_datahub_erp",
        "cash_assist_datahub_mis",
        "registration_datahub",
    ]

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser: User = UserFactory(is_superuser=True, is_staff=True)
        cls.business_area = create_afghanistan()

    @staticmethod
    def create_user_role_with_permissions(
        user: "User", permissions: Iterable, business_area: "BusinessArea"
    ) -> UserRole:
        permission_list = [perm.value for perm in permissions]
        role, created = Role.objects.update_or_create(
            name="Role with Permissions", defaults={"permissions": permission_list}
        )
        user_role, _ = UserRole.objects.get_or_create(user=user, role=role, business_area=business_area)
        return user_role

    @parameterized.expand(model_admins)
    def test_changelist(self, name: str, model_admin: ModelAdmin) -> None:
        self.create_user_role_with_permissions(self.superuser, [Permissions.DOWNLOAD_STORAGE_FILE], self.business_area)
        url = reverse(admin_urlname(model_admin.model._meta, "changelist"))  # type: ignore # str vs SafeString
        res = self.app.get(url, user=self.superuser)
        self.assertEqual(res.status_code, 200)
