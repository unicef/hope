"""
Admin smoke tests - automatically test all registered admin models.

These tests verify that the Django admin changelist, changeform, add, delete, and
button views all return expected HTTP status codes for a superuser, ensuring no
admin class is broken by configuration or import errors.
"""

import functools
from typing import TYPE_CHECKING, List
from unittest.mock import Mock

from _pytest.python import Metafunc
from admin_extra_buttons.handlers import ChoiceHandler
from django.contrib.admin.sites import site
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import reverse
from django_regex.utils import RegexList as _RegexList
import pytest

if TYPE_CHECKING:
    from _pytest.mark import Mark
    from django.db.models.options import Options


class RegexList(_RegexList):
    def extend(self, __iterable) -> None:
        for e in __iterable:
            self.append(e)


GLOBAL_EXCLUDED_MODELS = RegexList(
    [
        r"constance.Config",
        r"core.StorageFile",
        r"activity_log.LogEntry",
        r"admin.LogEntry",
        r"api.APILogEntry",
        r"django_celery_beat.",
        r"django_celery_results.",
        r"social_django.",
        # Third-party apps with admin registered but no HOPE business logic to test
        r"advanced_filters.AdvancedFilter",
        r"depot.StoredFilter",
        r"explorer.DatabaseConnection",
        r"explorer.ExplorerValue",
        r"explorer.Query",
        r"flags.FlagState",
    ]
)

GLOBAL_EXCLUDED_BUTTONS = RegexList(
    [
        r".*:publish",
        # External service integrations - require live connections
        r"account.UserAdmin:sync_multi",  # Active Directory sync
        r"account.UserAdmin:sync_single",  # Active Directory sync
        r"account.UserAdmin:load_ad_users",  # Active Directory
        r"account.UserAdmin:ad",  # Active Directory
        r"account.UserAdmin:sync_user",  # unicef_security: requires Azure AD
        r"account.UserAdmin:link_user_data",  # unicef_security: requires Azure AD
        r"core.BusinessAreaAdmin:_test_rapidpro_connection",  # RapidPro external
        r"payment.PaymentVerificationPlanAdmin:execute_sync_rapid_pro",  # RapidPro external
        r"sanction_list.SanctionListAdmin:refresh",  # fetches external sanction list
        # external Aurora service
        r"aurora.RecordAdmin:fetch_aurora",
        r"aurora.RecordAdmin:fetch",
        r"aurora.RecordAdmin:create_new_rdi",
        r"aurora.RecordAdmin:add_to_existing_rdi",
        r"aurora.RecordAdmin:extract_single",
    ]
)

KWARGS: dict = {}
pytestmark = pytest.mark.admin


def pytest_generate_tests(metafunc: Metafunc):  # noqa
    import django

    markers: List[Mark] = metafunc.definition.own_markers
    excluded_models = RegexList(GLOBAL_EXCLUDED_MODELS)
    excluded_buttons = RegexList(GLOBAL_EXCLUDED_BUTTONS)
    if "skip_models" in [m.name for m in markers]:
        skip_rule = list(filter(lambda m: m.name == "skip_models", markers))[0]
        excluded_models.extend(skip_rule.args)
    if "skip_buttons" in [m.name for m in markers]:
        skip_rule = list(filter(lambda m: m.name == "skip_buttons", markers))[0]
        excluded_buttons.extend(skip_rule.args)
    django.setup()
    if "button_handler" in metafunc.fixturenames:
        m = []
        ids = []
        for model, admin in site._registry.items():
            if hasattr(admin, "get_changelist_buttons"):
                name = model._meta.object_name
                _ = admin.urls  # force URL registration
                buttons = admin.extra_button_handlers.values()
                full_name = f"{model._meta.app_label}.{name}"
                admin_name = f"{model._meta.app_label}.{admin.__class__.__name__}"
                if full_name not in excluded_models:
                    for btn in buttons:
                        tid = f"{admin_name}:{btn.name}"
                        if tid not in excluded_buttons:
                            m.append([admin, btn])
                            ids.append(tid)
        metafunc.parametrize("modeladmin,button_handler", m, ids=ids)
    elif "modeladmin" in metafunc.fixturenames:
        m = []
        ids = []
        for model, admin in site._registry.items():
            name = model._meta.object_name
            full_name = f"{model._meta.app_label}.{name}"
            if full_name not in excluded_models:
                m.append(admin)
                ids.append(f"{admin.__class__.__name__}:{full_name}")
        metafunc.parametrize("modeladmin", m, ids=ids)


@functools.cache
def _build_factories_registry() -> dict:
    import factory as factory_lib

    from extras.test_utils import factories as factories_module

    registry: dict = {}
    for attr_name in dir(factories_module):
        attr = getattr(factories_module, attr_name, None)
        try:
            if (
                isinstance(attr, type)
                and issubclass(attr, factory_lib.django.DjangoModelFactory)
                and attr._meta.model is not None
            ):
                model = attr._meta.model
                if model not in registry or len(attr_name) < len(registry[model].__name__):
                    registry[model] = attr
        except (AttributeError, TypeError):
            continue
    return registry


def get_factory_for_model(model):
    return _build_factories_registry().get(model)


@pytest.fixture
def record(db, request):
    # TIPS: database access is forbidden in pytest_generate_tests
    modeladmin = request.getfixturevalue("modeladmin")
    instance = modeladmin.model.objects.first()
    if not instance:
        full_name = f"{modeladmin.model._meta.app_label}.{modeladmin.model._meta.object_name}"
        factory = get_factory_for_model(modeladmin.model)
        if factory is None:
            pytest.skip(f"No factory found for {full_name}")
        try:
            raw_kwargs = KWARGS.get(full_name, {})
            resolved_kwargs = {k: v() if callable(v) else v for k, v in raw_kwargs.items()}
            instance = factory(**resolved_kwargs)
        except Exception as e:
            raise Exception(f"Error creating fixture for {full_name}") from e
    return instance


@pytest.fixture
def app(django_app_factory, settings):
    from extras.test_utils.factories import UserFactory

    # Allow is_root() to return True for the smoke-test superuser
    root_token = "smoke-test-root-token"
    settings.ROOT_TOKEN = root_token

    admin_user = UserFactory(
        username="smoke_superuser",
        email="smoke_superuser@example.com",
        is_superuser=True,
        is_staff=True,
    )
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    django_app._root_token = root_token
    django_app.extra_environ["HTTP_X_ROOT_TOKEN"] = root_token
    return django_app


def _mock_request(app) -> Mock:
    """Build a mock request that passes is_root() checks."""
    return Mock(user=app._user, headers={"x-root-token": app._root_token})


@pytest.mark.django_db
def test_index(app):
    url = reverse("admin:index")
    res = app.get(url)
    assert res.status_code == 200


@pytest.mark.django_db
def test_applist(app):
    url = reverse("admin:app_list", kwargs={"app_label": "account"})
    res = app.get(url)
    assert res.status_code == 200


@pytest.mark.django_db
def test_changelist(app, modeladmin, record):
    opts: Options = modeladmin.model._meta
    url = reverse(admin_urlname(opts, "changelist"))
    res = app.get(url)
    assert res.status_code == 200, res.location
    assert str(opts.app_config.verbose_name) in str(res.content)


@pytest.mark.django_db
def test_changeform(app, modeladmin, record):
    opts: Options = modeladmin.model._meta
    url = reverse(admin_urlname(opts, "change"), args=[record.pk])

    res = app.get(url)
    assert res.status_code == 200
    assert str(opts.app_config.verbose_name) in res.body.decode()
    if modeladmin.has_change_permission(_mock_request(app)):
        res = res.forms[1].submit()
        assert res.status_code in [302, 200]


@pytest.mark.django_db
def test_add(app, modeladmin):
    opts: Options = modeladmin.model._meta
    url = reverse(admin_urlname(opts, "add"))
    if modeladmin.has_add_permission(_mock_request(app)):
        res = app.get(url)
        assert res.status_code == 200
        res = res.forms[1].submit()
        assert res.status_code in [200, 302]
    else:
        pytest.skip("No 'add' permission")


@pytest.mark.django_db
def test_delete(app, modeladmin, record):
    opts: Options = modeladmin.model._meta
    url = reverse(admin_urlname(opts, "delete"), args=[record.pk])
    if modeladmin.has_delete_permission(_mock_request(app)):
        res = app.get(url)
        assert res.status_code == 200
        res = res.forms[1].submit()
        assert res.status_code in [200, 302]
    else:
        pytest.skip("No 'delete' permission")


@pytest.mark.django_db
def test_buttons(app, modeladmin, button_handler, record):  # modeladmin is required by pytest parametrize pairing
    from admin_extra_buttons.handlers import LinkHandler

    if isinstance(button_handler, ChoiceHandler):
        pass
    elif isinstance(button_handler, LinkHandler):
        btn = button_handler.get_button({"original": record})
        button_handler.func(None, btn)
    else:
        if len(button_handler.func_args) == 2:
            url = reverse(f"admin:{button_handler.url_name}")
        else:
            url = reverse(f"admin:{button_handler.url_name}", args=[record.pk])

        res = app.get(url)
        assert res.status_code in [200, 302]
