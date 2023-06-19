from typing import Any, Dict, Tuple

from django.contrib.admin import ModelAdmin, site
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

import factory
from django_webtest import WebTest
from factory.base import FactoryMetaClass
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    RoleFactory,
    UserFactory,
)
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.account.permissions import Permissions

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
        business_area = BusinessAreaFactory(name="Afghanistan")
        perm = Permission.objects.create(
            name=Permissions.DOWNLOAD_STORAGE_FILE.name, content_type=ContentType.objects.first()
        )
        role = RoleFactory(subsystem="API", name="c", permissions=[perm.name])
        cls.superuser.user_roles.create(role=role, business_area=business_area)

    @parameterized.expand(model_admins)
    def test_changelist(self, name: str, model_admin: ModelAdmin) -> None:
        url = reverse(admin_urlname(model_admin.model._meta, "changelist"))  # type: ignore # str vs SafeString
        res = self.app.get(url, user=self.superuser)
        self.assertEqual(res.status_code, 200)
