from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
import pytest

from extras.test_utils.factories import CurrencyFactory, UserFactory
from hope.admin.currency import CurrencyAdmin
from hope.models import Currency

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_instance() -> CurrencyAdmin:
    return CurrencyAdmin(Currency, AdminSite())


@pytest.fixture
def request_with_messages():
    request = RequestFactory().post("/")
    request.user = UserFactory()
    request.session = {}
    request._messages = FallbackStorage(request)
    return request


@pytest.fixture
def lone_currency() -> Currency:
    return CurrencyFactory(code="TST", name="Test", vision_code="TST", active=True)


@pytest.fixture
def currencies_with_different_codes() -> tuple[Currency, Currency]:
    active = CurrencyFactory(code="AAA", name="A", vision_code="AAA", active=True)
    inactive = CurrencyFactory(code="BBB", name="B", vision_code="BBB", active=False)
    return active, inactive


@pytest.fixture
def two_inactive_syp() -> tuple[Currency, Currency]:
    old = CurrencyFactory(code="SYP", name="old", vision_code="SYP", active=False)
    new = CurrencyFactory(code="SYP", name="new", vision_code="SYP01", active=False)
    return old, new


@pytest.fixture
def syp_awaiting_deprecation() -> tuple[Currency, Currency]:
    old = CurrencyFactory(code="SYP", name="Syrian pound Old", vision_code="SYP", active=True)
    new = CurrencyFactory(code="SYP", name="Syrian pound", vision_code="SYP01", active=False)
    return old, new


def test_deprecate_requires_exactly_two(
    admin_instance: CurrencyAdmin, request_with_messages, lone_currency: Currency, django_assert_num_queries
) -> None:
    with django_assert_num_queries(1):
        admin_instance.deprecate_currency(request_with_messages, Currency.objects.filter(code="TST"))

    messages = [str(m) for m in get_messages(request_with_messages)]
    assert any("exactly two" in m for m in messages)


def test_deprecate_requires_same_code(
    admin_instance: CurrencyAdmin,
    request_with_messages,
    currencies_with_different_codes: tuple[Currency, Currency],
    django_assert_num_queries,
) -> None:
    with django_assert_num_queries(1):
        admin_instance.deprecate_currency(request_with_messages, Currency.objects.filter(code__in=["AAA", "BBB"]))

    messages = [str(m) for m in get_messages(request_with_messages)]
    assert any("same code" in m for m in messages)


def test_deprecate_requires_one_active_one_inactive(
    admin_instance: CurrencyAdmin,
    request_with_messages,
    two_inactive_syp: tuple[Currency, Currency],
    django_assert_num_queries,
) -> None:
    # Two inactive rows sharing a code is allowed by the constraint but invalid for deprecation.
    with django_assert_num_queries(1):
        admin_instance.deprecate_currency(request_with_messages, Currency.objects.filter(code="SYP"))

    messages = [str(m) for m in get_messages(request_with_messages)]
    assert any("one selected currency must be active" in m for m in messages)


def test_deprecate_swaps_active_flag(
    admin_instance: CurrencyAdmin,
    request_with_messages,
    syp_awaiting_deprecation: tuple[Currency, Currency],
    django_assert_num_queries,
) -> None:
    old, new = syp_awaiting_deprecation
    # Warm the ContentType cache so the LogEntry writes cost a fixed number of queries.
    ContentType.objects.get_for_model(Currency)

    with django_assert_num_queries(7):
        admin_instance.deprecate_currency(request_with_messages, Currency.objects.filter(code="SYP"))

    old.refresh_from_db()
    new.refresh_from_db()
    assert old.active is False
    assert new.active is True


def test_deprecate_leaves_rows_untouched_when_selection_is_invalid(
    admin_instance: CurrencyAdmin, request_with_messages, two_inactive_syp: tuple[Currency, Currency]
) -> None:
    old, new = two_inactive_syp

    admin_instance.deprecate_currency(request_with_messages, Currency.objects.filter(code="SYP"))

    old.refresh_from_db()
    new.refresh_from_db()
    assert old.active is False
    assert new.active is False


def test_deprecate_logs_the_swap_on_both_rows(
    admin_instance: CurrencyAdmin,
    request_with_messages,
    syp_awaiting_deprecation: tuple[Currency, Currency],
) -> None:
    old, new = syp_awaiting_deprecation

    admin_instance.deprecate_currency(request_with_messages, Currency.objects.filter(code="SYP"))

    entries = LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(Currency), user=request_with_messages.user
    )
    assert {(e.object_id, e.action_flag, e.change_message) for e in entries} == {
        (str(old.pk), CHANGE, "Deprecated in favour of 'SYP01'."),
        (str(new.pk), CHANGE, "Activated in place of 'SYP'."),
    }


def test_deprecate_action_is_hidden_without_change_permission(admin_instance: CurrencyAdmin) -> None:
    request = RequestFactory().get("/")
    request.user = UserFactory()

    assert "deprecate_currency" not in admin_instance.get_actions(request)


def test_deprecate_action_is_offered_with_change_permission(admin_instance: CurrencyAdmin) -> None:
    request = RequestFactory().get("/")
    request.user = UserFactory()
    request.user.user_permissions.add(Permission.objects.get(codename="change_currency"))

    assert "deprecate_currency" in admin_instance.get_actions(request)
