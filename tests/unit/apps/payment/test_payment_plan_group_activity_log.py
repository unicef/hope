from typing import Any, Callable

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.activity_log.utils import copy_model_object
from hope.apps.core.utils import nested_getattr
from hope.apps.payment.utils import log_payment_plan_group_change
from hope.models import LogEntry, PaymentPlanGroup

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="test-ba")


@pytest.fixture
def program(business_area: Any) -> Any:
    return ProgramFactory(business_area=business_area, cycle=False)


@pytest.fixture
def cycle(program: Any) -> Any:
    return ProgramCycleFactory(program=program)


@pytest.fixture
def group(cycle: Any) -> Any:
    return cycle.payment_plan_groups.first()


@pytest.fixture
def user() -> Any:
    return UserFactory(first_name="Group", last_name="Author")


@pytest.fixture
def client(api_client: Callable, user: Any) -> Any:
    return api_client(user)


def _list_url(ba_slug: str, program_code: str) -> str:
    return reverse(
        "api:payments:payment-plan-groups-list",
        kwargs={"business_area_slug": ba_slug, "program_code": program_code},
    )


def _detail_url(ba_slug: str, program_code: str, group_id: Any) -> str:
    return reverse(
        "api:payments:payment-plan-groups-detail",
        kwargs={"business_area_slug": ba_slug, "program_code": program_code, "pk": group_id},
    )


def _group_logs(group_id: Any) -> Any:
    return LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(PaymentPlanGroup),
        object_id=group_id,
    )


@pytest.mark.parametrize("field_path", sorted(PaymentPlanGroup.ACTIVITY_LOG_MAPPING.keys()))
def test_payment_plan_group_activity_log_mapping_keys_resolve(group: Any, field_path: str) -> None:
    nested_getattr(group, field_path)


@pytest.mark.enable_activity_log
def test_create_group_logs_create_entry(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_CREATE], business_area, program=program)

    response = client.post(_list_url(business_area.slug, program.code), {"name": "New Group", "cycle": str(cycle.id)})

    assert response.status_code == 201
    log = _group_logs(response.json()["id"]).get()
    assert log.action == LogEntry.CREATE
    assert log.user == user
    assert log.business_area == business_area
    assert log.changes["name"] == {"from": None, "to": "New Group"}
    assert list(log.programs.values_list("pk", flat=True)) == [program.pk]


@pytest.mark.enable_activity_log
def test_update_group_name_logs_update_entry(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE], business_area, program=program)

    response = client.put(_detail_url(business_area.slug, program.code, group.id), {"name": "Renamed Group"})

    assert response.status_code == 200
    log = _group_logs(group.id).get()
    assert log.action == LogEntry.UPDATE
    assert log.user == user
    assert log.changes == {"name": {"from": "Default Group", "to": "Renamed Group"}}


@pytest.mark.enable_activity_log
def test_delete_group_logs_delete_entry(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_DELETE], business_area, program=program)
    deletable_group = PaymentPlanGroupFactory(cycle=cycle, name="Deletable Group")

    response = client.delete(_detail_url(business_area.slug, program.code, deletable_group.id))

    assert response.status_code == 204
    log = _group_logs(deletable_group.id).get()
    assert log.action == LogEntry.DELETE
    assert log.user == user
    assert log.object_repr == str(deletable_group)
    assert log.changes is None
    assert list(log.programs.values_list("pk", flat=True)) == [program.pk]


@pytest.mark.enable_activity_log
def test_log_payment_plan_group_change_records_background_action_status(group: Any, user: Any, program: Any) -> None:
    old_group = copy_model_object(group)
    group.background_action_status = PaymentPlanGroup.BackgroundActionStatus.XLSX_EXPORT_ERROR
    group.save(update_fields=["background_action_status"])

    log_payment_plan_group_change(group, old_group, str(user.pk))

    log = _group_logs(group.id).get()
    assert log.action == LogEntry.UPDATE
    assert log.user == user
    assert log.changes == {"background_action_status": {"from": None, "to": "XLSX_EXPORT_ERROR"}}
    assert list(log.programs.values_list("pk", flat=True)) == [program.pk]


@pytest.mark.enable_activity_log
def test_log_payment_plan_group_change_without_user_for_system_run(group: Any) -> None:
    old_group = copy_model_object(group)
    group.background_action_status = PaymentPlanGroup.BackgroundActionStatus.XLSX_IMPORT_ERROR
    group.save(update_fields=["background_action_status"])

    log_payment_plan_group_change(group, old_group, None)

    log = _group_logs(group.id).get()
    assert log.user is None


@pytest.mark.enable_activity_log
def test_log_payment_plan_group_change_skips_log_when_no_mapped_field_changed(group: Any, user: Any) -> None:
    old_group = copy_model_object(group)

    log_payment_plan_group_change(group, old_group, str(user.pk))

    assert not _group_logs(group.id).exists()


@pytest.mark.enable_activity_log
def test_update_group_with_unchanged_name_logs_nothing(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE], business_area, program=program)

    response = client.put(_detail_url(business_area.slug, program.code, group.id), {"name": group.name})

    assert response.status_code == 200
    assert not _group_logs(group.id).exists()
