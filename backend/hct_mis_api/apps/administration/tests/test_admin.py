from django.contrib.admin import site
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import reverse

import factory
from django_webtest import WebTest
from factory.base import FactoryMetaClass
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import User

EXCLUDED_MODELS = []

factories_registry = {}


class AutoRegisterFactoryMetaClass(FactoryMetaClass):
    def __new__(mcs, class_name, bases, attrs):
        new_class = super().__new__(mcs, class_name, bases, attrs)
        factories_registry[new_class._meta.model] = new_class
        return new_class


class ModelFactory(factory.django.DjangoModelFactory, metaclass=AutoRegisterFactoryMetaClass):
    pass


def get_factory_for_model(_model):
    class Meta:
        model = _model

    if _model in factories_registry:
        return factories_registry[_model]
    return type("AAA", (ModelFactory,), {"Meta": Meta})


def model_admins():
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

    def setUp(self):
        self.superuser: User = UserFactory(is_superuser=True, is_staff=True)

    @parameterized.expand(model_admins)
    def test_changelist(self, name, model_admin):
        url = reverse(admin_urlname(model_admin.model._meta, "changelist"))
        res = self.app.get(url, user=self.superuser)
        self.assertEqual(res.status_code, 200)
