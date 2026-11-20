from django.contrib import admin
from django.test import RequestFactory
import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.payment import PaymentListFactory
from hope.admin.payment_plan import PaymentListAdmin
from hope.models import LogEntry, PaymentList, User
from hope.models.currency import Currency

pytestmark = pytest.mark.django_db


@pytest.fixture
def user() -> User:
    return UserFactory(first_name="Admin", last_name="Editor")


@pytest.fixture
def payment_list(currency_usd: Currency) -> PaymentList:
    return PaymentListFactory(currency=currency_usd, exclusion_reason="")


@pytest.mark.enable_activity_log
def test_admin_save_model_logs_mapped_field_change(payment_list, user) -> None:
    model_admin = PaymentListAdmin(PaymentList, admin.site)
    request = RequestFactory().post("/admin/")
    request.user = user
    payment_list.exclusion_reason = "Edited in admin"

    model_admin.save_model(request, payment_list, form=None, change=True)

    log = LogEntry.objects.filter(object_id=payment_list.pk, action=LogEntry.UPDATE).latest("timestamp")
    assert log.user == user
    assert log.changes["exclusion_reason"]["to"] == "Edited in admin"


@pytest.mark.enable_activity_log
def test_admin_save_model_skips_log_when_no_mapped_field_changed(payment_list, user) -> None:
    model_admin = PaymentListAdmin(PaymentList, admin.site)
    request = RequestFactory().post("/admin/")
    request.user = user
    # build_status is not part of ACTIVITY_LOG_MAPPING
    payment_list.build_status = PaymentList.BuildStatus.BUILD_STATUS_OK

    model_admin.save_model(request, payment_list, form=None, change=True)

    assert not LogEntry.objects.filter(object_id=payment_list.pk).exists()
