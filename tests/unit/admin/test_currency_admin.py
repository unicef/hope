from django.contrib.admin.sites import AdminSite
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
import pytest

from hope.admin.currency import CurrencyAdmin
from hope.models import Currency


@pytest.fixture
def admin_instance():
    return CurrencyAdmin(Currency, AdminSite())


@pytest.fixture
def request_with_messages():
    request = RequestFactory().post("/")
    request.session = {}
    request._messages = FallbackStorage(request)
    return request


def _form_data(code, name, vision_code, active):
    return {
        "code": code,
        "name": name,
        "vision_code": vision_code,
        "active": active,
        "is_crypto": False,
        "number_of_decimals": 2,
    }


@pytest.mark.django_db
def test_deprecate_requires_exactly_two(admin_instance, request_with_messages):
    Currency.objects.create(code="TST", name="Test", vision_code="TST", active=True)

    admin_instance.deprecate_currency(request_with_messages, Currency.objects.filter(code="TST"))

    messages = [str(m) for m in get_messages(request_with_messages)]
    assert any("exactly two" in m for m in messages)


@pytest.mark.django_db
def test_deprecate_requires_same_code(admin_instance, request_with_messages):
    Currency.objects.create(code="AAA", name="A", vision_code="AAA", active=True)
    Currency.objects.create(code="BBB", name="B", vision_code="BBB", active=False)

    admin_instance.deprecate_currency(request_with_messages, Currency.objects.filter(code__in=["AAA", "BBB"]))

    messages = [str(m) for m in get_messages(request_with_messages)]
    assert any("same code" in m for m in messages)


@pytest.mark.django_db
def test_deprecate_requires_one_active_one_inactive(admin_instance, request_with_messages):
    # Two inactive rows sharing a code is allowed by the constraint but invalid for deprecation.
    Currency.objects.create(code="SYP", name="old", vision_code="SYP", active=False)
    Currency.objects.create(code="SYP", name="new", vision_code="SYP01", active=False)

    admin_instance.deprecate_currency(request_with_messages, Currency.objects.filter(code="SYP"))

    messages = [str(m) for m in get_messages(request_with_messages)]
    assert any("one selected currency must be active" in m for m in messages)


@pytest.mark.django_db
def test_deprecate_swaps_active_flag(admin_instance, request_with_messages):
    old = Currency.objects.create(code="SYP", name="Syrian pound Old", vision_code="SYP", active=True)
    new = Currency.objects.create(code="SYP", name="Syrian pound", vision_code="SYP01", active=False)

    admin_instance.deprecate_currency(request_with_messages, Currency.objects.filter(code="SYP"))

    old.refresh_from_db()
    new.refresh_from_db()
    assert old.active is False
    assert new.active is True
