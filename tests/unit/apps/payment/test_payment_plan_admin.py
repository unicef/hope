from decimal import Decimal
import os
from unittest.mock import PropertyMock, patch

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    CurrencyFactory,
    DeliveryMechanismFactory,
    FileTempFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    UserFactory,
)
from hope.admin.payment_plan import can_sync_with_payment_gateway
from hope.models import AsyncJob, AsyncJobModel, AsyncRetryJob, FinancialServiceProvider, PaymentPlan, PaymentPlanGroup

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def mock_payment_gateway_env_vars() -> None:
    with patch.dict(
        os.environ,
        {"PAYMENT_GATEWAY_API_KEY": "TEST", "PAYMENT_GATEWAY_API_URL": "TEST"},
    ):
        yield


@pytest.fixture
def admin_user():
    user = UserFactory(
        username="root",
        email="root@root.com",
        is_staff=True,
        is_superuser=True,
        is_active=True,
        status="ACTIVE",
    )
    user.set_password("password")
    user.save()
    return user


@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user, backend="django.contrib.auth.backends.ModelBackend")
    return client


@pytest.fixture
def staff_user():
    user = UserFactory(
        username="staff_user",
        email="staff@root.com",
        is_staff=True,
        is_superuser=False,
        is_active=True,
        status="ACTIVE",
    )
    user.set_password("password")
    user.save()
    return user


@pytest.fixture
def staff_client(client, staff_user):
    client.force_login(staff_user, backend="django.contrib.auth.backends.ModelBackend")
    return client


@pytest.fixture
def delivery_mechanism():
    return DeliveryMechanismFactory()


@pytest.fixture
def financial_service_provider(delivery_mechanism):
    return FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        payment_gateway_id="test123",
        delivery_mechanisms=[delivery_mechanism],
    )


@pytest.fixture
def payment_plan(financial_service_provider, delivery_mechanism):
    return PaymentPlanFactory(
        name="Test Plan",
        status=PaymentPlan.Status.ACCEPTED,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism,
    )


@pytest.fixture
def payment(payment_plan, delivery_mechanism, financial_service_provider):
    return PaymentFactory(
        parent=payment_plan,
        delivery_type=delivery_mechanism,
        financial_service_provider=financial_service_provider,
    )


@pytest.fixture
def file_temp():
    return FileTempFactory()


@pytest.fixture
def fsp_template(payment_plan):
    template = FinancialServiceProviderXlsxTemplateFactory(name="Test Template AAA")
    fsp = FinancialServiceProviderFactory()
    fsp.allowed_business_areas.add(payment_plan.business_area)
    fsp.xlsx_templates.add(template)
    return template


@pytest.fixture
def payment_gateway_fsp(delivery_mechanism):
    return FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        payment_gateway_id="pg-1",
        delivery_mechanisms=[delivery_mechanism],
    )


@patch("hope.apps.payment.services.payment_gateway.PaymentGatewayService.sync_payment_plan")
@patch("hope.admin.payment_plan.has_payment_plan_pg_sync_permission", return_value=True)
def test_payment_plan_post_sync_with_payment_gateway(mock_perm, mock_sync, admin_client, payment_plan) -> None:
    url = reverse(
        "admin:payment_paymentplan_sync_with_payment_gateway",
        args=[payment_plan.pk],
    )
    response = admin_client.post(url)

    mock_sync.assert_called_once()
    assert mock_sync.call_args[0][0] == payment_plan
    assert response.status_code == 302
    assert reverse("admin:payment_paymentplan_change", args=[payment_plan.pk]) in response["Location"]


@patch("hope.admin.payment_plan.has_payment_plan_pg_sync_permission", return_value=True)
def test_payment_plan_get_sync_with_payment_gateway_confirmation(mock_perm, admin_client, payment_plan) -> None:
    url = reverse(
        "admin:payment_paymentplan_sync_with_payment_gateway",
        args=[payment_plan.pk],
    )
    response = admin_client.get(url)

    assert response.status_code == 200
    assert "Do you confirm to Sync with Payment Gateway?" in response.content.decode("utf-8")


def test_payment_plan_get_recalculate_exchange_rate_confirmation(admin_client, payment_plan) -> None:
    payment_plan.exchange_rate = Decimal("2.00")
    payment_plan.save(update_fields=["exchange_rate"])
    url = reverse(
        "admin:payment_paymentplan_recalculate_exchange_rate",
        args=[payment_plan.pk],
    )
    response = admin_client.get(url)

    assert response.status_code == 200
    assert "Do you confirm to recalculate USD values based on provided exchange rate?" in response.content.decode(
        "utf-8"
    )


@patch("hope.admin.payment_plan.PaymentPlan.update_money_fields")
def test_payment_plan_post_recalculate_exchange_rate_with_permission(
    mock_update_money_fields,
    staff_user,
    staff_client,
    payment_plan,
    delivery_mechanism,
    financial_service_provider,
) -> None:
    content_type = ContentType.objects.get_for_model(PaymentPlan)
    permission, _ = Permission.objects.get_or_create(
        content_type=content_type,
        codename="recalculate_exchange_rate",
        defaults={"name": "Can recalculate USD values based on exchange rate"},
    )
    base_permissions = Permission.objects.filter(
        content_type=content_type,
        codename__in=["view_paymentplan", "change_paymentplan"],
    )
    staff_user.user_permissions.set([*base_permissions, permission])

    payment_plan.currency = CurrencyFactory(code="PLN", name="Polish Zloty")
    payment_plan.exchange_rate = Decimal("2.00")
    payment_plan.save(update_fields=["currency", "exchange_rate"])
    payment = PaymentFactory(
        parent=payment_plan,
        delivery_type=delivery_mechanism,
        financial_service_provider=financial_service_provider,
        entitlement_quantity=Decimal("100.00"),
        delivered_quantity=Decimal("40.00"),
        entitlement_quantity_usd=Decimal("1.00"),
        delivered_quantity_usd=Decimal("1.00"),
    )
    url = reverse(
        "admin:payment_paymentplan_recalculate_exchange_rate",
        args=[payment_plan.pk],
    )

    response = staff_client.post(url)
    payment.refresh_from_db()

    mock_update_money_fields.assert_called_once()
    assert payment.entitlement_quantity_usd == Decimal("50.00")
    assert payment.delivered_quantity_usd == Decimal("20.00")
    assert response.status_code == 302
    assert reverse("admin:payment_paymentplan_change", args=[payment_plan.pk]) in response["Location"]


@patch("hope.admin.payment_plan.PaymentPlan.update_money_fields")
def test_payment_plan_post_recalculate_exchange_rate_without_permission(
    mock_update_money_fields,
    staff_user,
    staff_client,
    payment_plan,
    delivery_mechanism,
    financial_service_provider,
) -> None:
    content_type = ContentType.objects.get_for_model(PaymentPlan)
    base_permissions = Permission.objects.filter(
        content_type=content_type,
        codename__in=["view_paymentplan", "change_paymentplan"],
    )
    staff_user.user_permissions.set(base_permissions)

    payment_plan.currency = CurrencyFactory(code="PLN", name="Polish Zloty")
    payment_plan.exchange_rate = Decimal("2.00")
    payment_plan.save(update_fields=["currency", "exchange_rate"])
    payment = PaymentFactory(
        parent=payment_plan,
        delivery_type=delivery_mechanism,
        financial_service_provider=financial_service_provider,
        entitlement_quantity=Decimal("100.00"),
        delivered_quantity=Decimal("40.00"),
        entitlement_quantity_usd=Decimal("1.00"),
        delivered_quantity_usd=Decimal("1.00"),
    )
    url = reverse(
        "admin:payment_paymentplan_recalculate_exchange_rate",
        args=[payment_plan.pk],
    )

    response = staff_client.post(url)
    payment.refresh_from_db()

    mock_update_money_fields.assert_not_called()
    assert payment.entitlement_quantity_usd == Decimal("1.00")
    assert payment.delivered_quantity_usd == Decimal("1.00")
    assert response.status_code == 403


def test_payment_plan_related_configs_button(admin_client, payment_plan) -> None:
    url = reverse("admin:payment_paymentplan_related_configs", args=[payment_plan.pk])
    response = admin_client.get(url)
    assert response.status_code == 302
    assert reverse("admin:payment_deliverymechanismconfig_changelist") in response["Location"]


def test_related_configs_warns_and_redirects_when_no_fsp(admin_client, delivery_mechanism) -> None:
    pp = PaymentPlanFactory(delivery_mechanism=delivery_mechanism, financial_service_provider=None)

    url = reverse("admin:payment_paymentplan_related_configs", args=[pp.pk])
    response = admin_client.get(url)

    assert response.status_code == 302
    assert response["Location"] == reverse("admin:payment_deliverymechanismconfig_changelist")
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "no delivery mechanism or financial service provider" in str(messages[0])


def test_related_configs_warns_and_redirects_when_no_delivery_mechanism(
    admin_client, financial_service_provider
) -> None:
    pp = PaymentPlanFactory(delivery_mechanism=None, financial_service_provider=financial_service_provider)

    url = reverse("admin:payment_paymentplan_related_configs", args=[pp.pk])
    response = admin_client.get(url)

    assert response.status_code == 302
    assert response["Location"] == reverse("admin:payment_deliverymechanismconfig_changelist")
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "no delivery mechanism or financial service provider" in str(messages[0])


@patch("hope.apps.payment.services.payment_gateway.PaymentGatewayService.add_missing_records_to_payment_instructions")
@patch("hope.admin.payment_plan.has_payment_plan_pg_sync_permission", return_value=True)
def test_payment_post_sync_missing_records_with_payment_gateway(
    mock_perm, mock_sync, admin_client, payment_plan
) -> None:
    url = reverse(
        "admin:payment_paymentplan_sync_missing_records_with_payment_gateway",
        args=[payment_plan.pk],
    )
    response = admin_client.post(url)

    mock_sync.assert_called_once_with(payment_plan)
    assert response.status_code == 302
    assert reverse("admin:payment_paymentplan_change", args=[payment_plan.pk]) in response["Location"]


@patch("hope.admin.payment_plan.has_payment_plan_pg_sync_permission", return_value=True)
def test_payment_get_sync_missing_records_with_payment_gateway(mock_perm, admin_client, payment_plan) -> None:
    url = reverse(
        "admin:payment_paymentplan_sync_missing_records_with_payment_gateway",
        args=[payment_plan.pk],
    )
    response = admin_client.get(url)

    assert response.status_code == 200
    assert "Do you confirm to Sync with Payment Gateway missing Records?" in response.content.decode("utf-8")


@pytest.mark.parametrize(
    ("pp_status", "use_payment_gateway", "expected"),
    [
        (PaymentPlan.Status.ACCEPTED, True, True),
        (PaymentPlan.Status.ACCEPTED, False, False),
        (PaymentPlan.Status.FINISHED, True, True),
        (PaymentPlan.Status.FINISHED, False, False),
        (PaymentPlan.Status.OPEN, True, False),
        (PaymentPlan.Status.OPEN, False, False),
    ],
)
def test_can_sync_with_payment_gateway(payment_plan, pp_status, use_payment_gateway, expected) -> None:
    payment_plan.status = pp_status
    payment_plan.use_payment_gateway = use_payment_gateway
    payment_plan.save(update_fields=["status", "use_payment_gateway"])

    assert can_sync_with_payment_gateway(payment_plan) is expected


@pytest.fixture
def group_with_exported_batch():
    group = PaymentPlanGroupFactory()
    file_temp = FileTempFactory()
    PaymentPlanFactory(
        payment_plan_group=group,
        program_cycle=group.cycle,
        status=PaymentPlan.Status.ACCEPTED,
        export_tag=1,
        export_file_delivery=file_temp,
    )
    return group


def test_can_reexport_batch_returns_true_when_batch_has_file_and_no_active_export(
    group_with_exported_batch,
) -> None:
    assert group_with_exported_batch.can_reexport_batch(1) is True


def test_can_reexport_batch_returns_false_when_export_in_progress(group_with_exported_batch) -> None:
    group = group_with_exported_batch
    group.background_action_status = PaymentPlanGroup.BackgroundActionStatus.XLSX_EXPORTING
    group.save(update_fields=["background_action_status"])

    assert group.can_reexport_batch(1) is False


def test_can_reexport_batch_returns_false_for_unknown_batch_tag(group_with_exported_batch) -> None:
    assert group_with_exported_batch.can_reexport_batch(99) is False


def test_reexport_batch_get_renders_form(admin_client, group_with_exported_batch) -> None:
    url = reverse("admin:payment_paymentplangroup_reexport_batch", args=[group_with_exported_batch.pk])

    response = admin_client.get(url)

    assert response.status_code == 200


@patch("hope.apps.payment.celery_tasks.export_payment_plan_group_delivery_xlsx_async_task")
def test_reexport_batch_post_sets_exporting_status_queues_task_and_redirects(
    mock_task, admin_client, group_with_exported_batch
) -> None:
    group = group_with_exported_batch
    url = reverse("admin:payment_paymentplangroup_reexport_batch", args=[group.pk])

    response = admin_client.post(url, {"export_tag": "1"})

    assert response.status_code == 302
    assert reverse("admin:payment_paymentplangroup_change", args=[group.pk]) in response["Location"]
    group.refresh_from_db()
    assert group.background_action_status == PaymentPlanGroup.BackgroundActionStatus.XLSX_EXPORTING
    mock_task.assert_called_once()
    called_group, called_user_id, called_template_id, called_tag = mock_task.call_args[0]
    assert called_group.pk == group.pk
    assert called_tag == 1
    assert called_template_id is None
    messages_list = list(get_messages(response.wsgi_request))
    assert any("Re-export started" in str(m) for m in messages_list)


@patch("hope.apps.payment.celery_tasks.export_payment_plan_group_delivery_xlsx_async_task")
def test_reexport_batch_post_blocked_when_no_export_file_for_batch(
    mock_task, admin_client, group_with_exported_batch
) -> None:
    group = group_with_exported_batch
    plan = group.payment_plans.get()
    plan.export_file_delivery = None
    plan.save(update_fields=["export_file_delivery"])
    url = reverse("admin:payment_paymentplangroup_reexport_batch", args=[group.pk])

    response = admin_client.post(url, {"export_tag": "1"})

    assert response.status_code == 302
    assert reverse("admin:payment_paymentplangroup_change", args=[group.pk]) in response["Location"]
    mock_task.assert_not_called()
    messages_list = list(get_messages(response.wsgi_request))
    assert any("cannot be re-exported" in str(m) for m in messages_list)


@patch("hope.apps.payment.celery_tasks.export_payment_plan_group_delivery_xlsx_async_task")
def test_reexport_batch_post_blocked_when_export_already_in_progress(
    mock_task, admin_client, group_with_exported_batch
) -> None:
    group = group_with_exported_batch
    group.background_action_status = PaymentPlanGroup.BackgroundActionStatus.XLSX_EXPORTING
    group.save(update_fields=["background_action_status"])
    url = reverse("admin:payment_paymentplangroup_reexport_batch", args=[group.pk])

    response = admin_client.post(url, {"export_tag": "1"})

    assert response.status_code == 302
    mock_task.assert_not_called()
    messages_list = list(get_messages(response.wsgi_request))
    assert any("cannot be re-exported" in str(m) for m in messages_list)


def test_reexport_batch_requires_restart_exporting_permission(
    staff_user, staff_client, group_with_exported_batch
) -> None:
    content_type = ContentType.objects.get_for_model(PaymentPlanGroup)
    base_permissions = Permission.objects.filter(
        content_type=content_type,
        codename__in=["view_paymentplangroup", "change_paymentplangroup"],
    )
    staff_user.user_permissions.set(base_permissions)
    url = reverse("admin:payment_paymentplangroup_reexport_batch", args=[group_with_exported_batch.pk])

    response = staff_client.get(url)

    assert response.status_code == 403


@pytest.fixture
def group_with_exporting_status():
    return PaymentPlanGroupFactory(
        background_action_status=PaymentPlanGroup.BackgroundActionStatus.XLSX_EXPORTING,
    )


def test_restart_exporting_delivery_xlsx_get_renders_confirmation(admin_client, group_with_exporting_status) -> None:
    url = reverse(
        "admin:payment_paymentplangroup_restart_exporting_delivery_xlsx",
        args=[group_with_exporting_status.pk],
    )

    response = admin_client.get(url)

    assert response.status_code == 200
    assert "Do you confirm to restart exporting delivery XLSX file task?" in response.content.decode("utf-8")


@patch("hope.apps.payment.celery_tasks.export_payment_plan_group_delivery_xlsx_async_task")
def test_restart_exporting_delivery_xlsx_post_when_no_active_job_shows_error(
    mock_task, admin_client, group_with_exporting_status
) -> None:
    url = reverse(
        "admin:payment_paymentplangroup_restart_exporting_delivery_xlsx",
        args=[group_with_exporting_status.pk],
    )

    response = admin_client.post(url)

    assert response.status_code == 302
    assert (
        reverse("admin:payment_paymentplangroup_change", args=[group_with_exporting_status.pk]) in response["Location"]
    )
    mock_task.assert_not_called()
    messages_list = list(get_messages(response.wsgi_request))
    assert any("There is no active export job" in str(m) for m in messages_list)


@patch("hope.apps.payment.celery_tasks.export_payment_plan_group_delivery_xlsx_async_task")
def test_restart_exporting_delivery_xlsx_post_terminates_and_requeues_initial_export(
    mock_task, admin_client, group_with_exporting_status
) -> None:
    group = group_with_exporting_status
    AsyncRetryJob.create_for_instance(
        group,
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        job_name="export_payment_plan_group_delivery_xlsx_async_task",
        action="hope.apps.payment.celery_tasks.export_payment_plan_group_delivery_xlsx_async_task_action",
        config={"payment_plan_group_id": str(group.pk), "user_id": "some-user-id"},
    )
    url = reverse(
        "admin:payment_paymentplangroup_restart_exporting_delivery_xlsx",
        args=[group.pk],
    )

    with (
        patch("hope.admin.payment_plan.AsyncJob.task_status", new_callable=PropertyMock, return_value=AsyncJob.STARTED),
        patch("hope.admin.payment_plan.AsyncJob.terminate", autospec=True) as mock_terminate,
    ):
        response = admin_client.post(url)

    assert response.status_code == 302
    assert reverse("admin:payment_paymentplangroup_change", args=[group.pk]) in response["Location"]
    mock_terminate.assert_called_once()
    mock_task.assert_called_once()
    called_group, called_user_id, called_template_id, called_tag = mock_task.call_args[0]
    assert called_group.pk == group.pk
    assert called_template_id is None
    assert called_tag is None
    messages_list = list(get_messages(response.wsgi_request))
    assert any("Successfully restarted" in str(m) for m in messages_list)


@patch("hope.apps.payment.celery_tasks.export_payment_plan_group_delivery_xlsx_async_task")
def test_restart_exporting_delivery_xlsx_post_terminates_and_requeues_batch_export(
    mock_task, admin_client, group_with_exporting_status
) -> None:
    group = group_with_exporting_status
    AsyncRetryJob.create_for_instance(
        group,
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        job_name="export_payment_plan_group_delivery_xlsx_async_task",
        action="hope.apps.payment.celery_tasks.export_payment_plan_group_delivery_xlsx_async_task_action",
        config={"payment_plan_group_id": str(group.pk), "user_id": "some-user-id", "export_tag": 2},
    )
    url = reverse(
        "admin:payment_paymentplangroup_restart_exporting_delivery_xlsx",
        args=[group.pk],
    )

    with (
        patch("hope.admin.payment_plan.AsyncJob.task_status", new_callable=PropertyMock, return_value=AsyncJob.STARTED),
        patch("hope.admin.payment_plan.AsyncJob.terminate", autospec=True) as mock_terminate,
    ):
        response = admin_client.post(url)

    assert response.status_code == 302
    assert reverse("admin:payment_paymentplangroup_change", args=[group.pk]) in response["Location"]
    mock_terminate.assert_called_once()
    mock_task.assert_called_once()
    called_group, called_user_id, called_template_id, called_tag = mock_task.call_args[0]
    assert called_group.pk == group.pk
    assert called_tag == 2
    assert called_template_id is None
    messages_list = list(get_messages(response.wsgi_request))
    assert any("Successfully restarted" in str(m) for m in messages_list)


@patch("hope.apps.payment.celery_tasks.export_payment_plan_group_delivery_xlsx_async_task")
def test_restart_exporting_delivery_xlsx_post_terminates_and_requeues_each_job_independently(
    mock_task, admin_client, group_with_exporting_status
) -> None:
    group = group_with_exporting_status
    AsyncRetryJob.create_for_instance(
        group,
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        job_name="export_payment_plan_group_delivery_xlsx_async_task",
        action="hope.apps.payment.celery_tasks.export_payment_plan_group_delivery_xlsx_async_task_action",
        config={"payment_plan_group_id": str(group.pk), "user_id": "some-user-id", "export_tag": 3},
    )
    AsyncRetryJob.create_for_instance(
        group,
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        job_name="export_payment_plan_group_delivery_xlsx_async_task",
        action="hope.apps.payment.celery_tasks.export_payment_plan_group_delivery_xlsx_async_task_action",
        config={"payment_plan_group_id": str(group.pk), "user_id": "some-user-id", "export_tag": 7},
    )
    url = reverse(
        "admin:payment_paymentplangroup_restart_exporting_delivery_xlsx",
        args=[group.pk],
    )

    with (
        patch("hope.admin.payment_plan.AsyncJob.task_status", new_callable=PropertyMock, return_value=AsyncJob.STARTED),
        patch("hope.admin.payment_plan.AsyncJob.terminate", autospec=True) as mock_terminate,
    ):
        response = admin_client.post(url)

    assert response.status_code == 302
    assert reverse("admin:payment_paymentplangroup_change", args=[group.pk]) in response["Location"]
    assert mock_terminate.call_count == 2
    assert mock_task.call_count == 2
    requeued_tags = {call[0][3] for call in mock_task.call_args_list}
    assert requeued_tags == {3, 7}
    messages_list = list(get_messages(response.wsgi_request))
    assert any("Successfully restarted" in str(m) for m in messages_list)


def test_restart_exporting_delivery_xlsx_requires_permission(
    staff_user, staff_client, group_with_exporting_status
) -> None:
    content_type = ContentType.objects.get_for_model(PaymentPlanGroup)
    base_permissions = Permission.objects.filter(
        content_type=content_type,
        codename__in=["view_paymentplangroup", "change_paymentplangroup"],
    )
    staff_user.user_permissions.set(base_permissions)
    url = reverse(
        "admin:payment_paymentplangroup_restart_exporting_delivery_xlsx",
        args=[group_with_exporting_status.pk],
    )

    response = staff_client.get(url)

    assert response.status_code == 403


@pytest.fixture
def group_with_importing_status():
    group = PaymentPlanGroupFactory(
        background_action_status=PaymentPlanGroup.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
    )
    file_temp = FileTempFactory()
    group.delivery_import_file = file_temp
    group.save(update_fields=["delivery_import_file"])
    return group


def test_restart_import_reconciliation_get_renders_confirmation(admin_client, group_with_importing_status) -> None:
    url = reverse(
        "admin:payment_paymentplangroup_restart_importing_reconciliation_xlsx_file",
        args=[group_with_importing_status.pk],
    )

    response = admin_client.get(url)

    assert response.status_code == 200
    assert "Do you confirm to restart importing reconciliation XLSX file task?" in response.content.decode("utf-8")


def test_restart_import_reconciliation_post_when_no_file_shows_error(admin_client) -> None:
    group = PaymentPlanGroupFactory(
        background_action_status=PaymentPlanGroup.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
        delivery_import_file=None,
    )
    url = reverse(
        "admin:payment_paymentplangroup_restart_importing_reconciliation_xlsx_file",
        args=[group.pk],
    )

    response = admin_client.post(url)

    assert response.status_code == 302
    assert reverse("admin:payment_paymentplangroup_change", args=[group.pk]) in response["Location"]
    messages_list = list(get_messages(response.wsgi_request))
    assert any("There is no import file" in str(m) for m in messages_list)


@patch("hope.apps.payment.celery_tasks.import_payment_plan_group_delivery_from_xlsx_async_task")
def test_restart_import_reconciliation_post_when_no_active_job_shows_error(
    mock_task, admin_client, group_with_importing_status
) -> None:
    url = reverse(
        "admin:payment_paymentplangroup_restart_importing_reconciliation_xlsx_file",
        args=[group_with_importing_status.pk],
    )

    response = admin_client.post(url)

    assert response.status_code == 302
    mock_task.assert_not_called()
    messages_list = list(get_messages(response.wsgi_request))
    assert any("There is no current" in str(m) for m in messages_list)


@patch("hope.apps.payment.celery_tasks.import_payment_plan_group_delivery_from_xlsx_async_task")
def test_restart_import_reconciliation_post_terminates_active_job_and_requeues(
    mock_task, admin_client, group_with_importing_status
) -> None:
    group = group_with_importing_status
    AsyncRetryJob.create_for_instance(
        group,
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.payment.celery_tasks.import_payment_plan_group_delivery_from_xlsx_async_task_action",
        config={"payment_plan_group_id": str(group.pk)},
    )
    url = reverse(
        "admin:payment_paymentplangroup_restart_importing_reconciliation_xlsx_file",
        args=[group.pk],
    )

    with (
        patch("hope.admin.payment_plan.AsyncJob.task_status", new_callable=PropertyMock, return_value=AsyncJob.STARTED),
        patch("hope.admin.payment_plan.AsyncJob.terminate", autospec=True) as mock_terminate,
    ):
        response = admin_client.post(url)

    assert response.status_code == 302
    assert reverse("admin:payment_paymentplangroup_change", args=[group.pk]) in response["Location"]
    mock_terminate.assert_called_once()
    mock_task.assert_called_once_with(group)
    messages_list = list(get_messages(response.wsgi_request))
    assert any("Successfully restarted" in str(m) for m in messages_list)


def test_restart_import_reconciliation_requires_permission(
    staff_user, staff_client, group_with_importing_status
) -> None:
    content_type = ContentType.objects.get_for_model(PaymentPlanGroup)
    base_permissions = Permission.objects.filter(
        content_type=content_type,
        codename__in=["view_paymentplangroup", "change_paymentplangroup"],
    )
    staff_user.user_permissions.set(base_permissions)
    url = reverse(
        "admin:payment_paymentplangroup_restart_importing_reconciliation_xlsx_file",
        args=[group_with_importing_status.pk],
    )

    response = staff_client.get(url)

    assert response.status_code == 403
