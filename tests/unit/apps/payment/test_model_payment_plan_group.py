from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test.utils import CaptureQueriesContext
from flags.models import FlagState
import pytest

from extras.test_utils.factories import (
    FileTempFactory,
    FinancialServiceProviderFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    PaymentPlanSplitFactory,
    ProgramCycleFactory,
)
from hope.contrib.vision.choices import VisionStatus
from hope.models import PaymentPlan, PaymentPlanGroup

pytestmark = pytest.mark.django_db


@pytest.fixture
def cycle():
    return ProgramCycleFactory()


@pytest.fixture
def payment_plan_group(cycle):
    return PaymentPlanGroupFactory(cycle=cycle)


@pytest.fixture
def vision_managed_sendable_payment_plan(cycle, payment_plan_group):
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=payment_plan_group,
        status=PaymentPlan.Status.ACCEPTED,
        financial_service_provider=FinancialServiceProviderFactory(),
        use_payment_gateway=True,
        internal_data={"vision": {"status": VisionStatus.RELEASED.value}},
    )
    PaymentPlanSplitFactory(payment_plan=payment_plan, sent_to_payment_gateway=False)
    return payment_plan


@pytest.fixture
def vision_enabled_sendable_payment_plan(vision_managed_sendable_payment_plan):
    FlagState.objects.update_or_create(
        name="VISION_INTEGRATION_ACTIVE",
        condition="boolean",
        defaults={"value": "True"},
    )
    business_area = vision_managed_sendable_payment_plan.business_area
    business_area.vision_integration_active = True
    business_area.save(update_fields=["vision_integration_active"])
    return vision_managed_sendable_payment_plan


@pytest.fixture
def global_vision_disabled_sendable_payment_plan(vision_managed_sendable_payment_plan):
    FlagState.objects.update_or_create(
        name="VISION_INTEGRATION_ACTIVE",
        condition="boolean",
        defaults={"value": "False"},
    )
    business_area = vision_managed_sendable_payment_plan.business_area
    business_area.vision_integration_active = True
    business_area.save(update_fields=["vision_integration_active"])
    return vision_managed_sendable_payment_plan


@pytest.fixture
def business_area_vision_disabled_sendable_payment_plan(vision_managed_sendable_payment_plan):
    FlagState.objects.update_or_create(
        name="VISION_INTEGRATION_ACTIVE",
        condition="boolean",
        defaults={"value": "True"},
    )
    business_area = vision_managed_sendable_payment_plan.business_area
    business_area.vision_integration_active = False
    business_area.save(update_fields=["vision_integration_active"])
    return vision_managed_sendable_payment_plan


@pytest.fixture
def not_sent_to_vision_sendable_payment_plan(cycle, payment_plan_group):
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=payment_plan_group,
        status=PaymentPlan.Status.ACCEPTED,
        financial_service_provider=FinancialServiceProviderFactory(),
        use_payment_gateway=True,
        internal_data={"vision": {"status": VisionStatus.NOT_SENT.value}},
    )
    PaymentPlanSplitFactory(payment_plan=payment_plan, sent_to_payment_gateway=False)
    return payment_plan


def test_group_send_excludes_vision_managed_plan(
    payment_plan_group, vision_enabled_sendable_payment_plan, django_assert_num_queries
) -> None:
    with django_assert_num_queries(2):
        sendable_plan_ids = list(payment_plan_group.sendable_to_payment_gateway_plans().values_list("pk", flat=True))

    assert vision_enabled_sendable_payment_plan.pk not in sendable_plan_ids


def test_group_send_includes_vision_managed_plan_when_global_flag_is_disabled(
    payment_plan_group, global_vision_disabled_sendable_payment_plan, django_assert_num_queries
) -> None:
    with django_assert_num_queries(2):
        sendable_plan_ids = list(payment_plan_group.sendable_to_payment_gateway_plans().values_list("pk", flat=True))

    assert global_vision_disabled_sendable_payment_plan.pk in sendable_plan_ids


def test_group_send_includes_vision_managed_plan_when_business_area_flag_is_disabled(
    payment_plan_group, business_area_vision_disabled_sendable_payment_plan, django_assert_num_queries
) -> None:
    with django_assert_num_queries(2):
        sendable_plan_ids = list(payment_plan_group.sendable_to_payment_gateway_plans().values_list("pk", flat=True))

    assert business_area_vision_disabled_sendable_payment_plan.pk in sendable_plan_ids


def test_group_send_includes_plan_with_not_sent_vision_status(
    payment_plan_group, not_sent_to_vision_sendable_payment_plan, django_assert_num_queries
) -> None:
    with django_assert_num_queries(2):
        sendable_plan_ids = list(payment_plan_group.sendable_to_payment_gateway_plans().values_list("pk", flat=True))

    assert not_sent_to_vision_sendable_payment_plan.pk in sendable_plan_ids


def test_default_group_created_on_cycle_creation(cycle):
    assert PaymentPlanGroup.objects.filter(cycle=cycle, name="Default Group").exists()


def test_payment_plan_with_matching_group_saves_without_error(cycle, payment_plan_group):
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=payment_plan_group)


def test_payment_plan_group_cycle_must_match_plan_cycle(cycle, payment_plan_group):
    other_cycle = ProgramCycleFactory(program=cycle.program)
    plan = PaymentPlanFactory(program_cycle=cycle, payment_plan_group=payment_plan_group)

    plan.program_cycle = other_cycle

    with pytest.raises(ValidationError, match="aymentPlan's program_cycle must match its PaymentPlanGroup's cycle."):
        plan.save()


def test_default_group_not_created_again_on_cycle_update(cycle):
    group_count_before = PaymentPlanGroup.objects.filter(cycle=cycle).count()

    cycle.title = "Updated Title"
    cycle.save()

    assert PaymentPlanGroup.objects.filter(cycle=cycle).count() == group_count_before


def test_delete_only_group_in_cycle_raises(cycle):
    last_group = PaymentPlanGroup.objects.get(cycle=cycle)

    with pytest.raises(ValidationError, match="Cannot delete the last group in a cycle."):
        last_group.delete()


def test_delete_group_succeeds_when_another_remains(cycle, payment_plan_group):
    payment_plan_group.delete()

    assert PaymentPlanGroup.objects.filter(cycle=cycle).count() == 1


def test_delete_locks_cycle_groups_for_update(cycle, payment_plan_group):
    with CaptureQueriesContext(connection) as captured:
        payment_plan_group.delete()

    assert any("for update" in query["sql"].lower() for query in captured.captured_queries)


def test_get_batch_export_file_link_returns_url_when_file_present(cycle, payment_plan_group):
    file_temp = FileTempFactory(file=SimpleUploadedFile("batch-1.xlsx", b"data"))
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=payment_plan_group,
        export_tag=1,
        export_file_delivery=file_temp,
    )

    assert payment_plan_group.get_batch_export_file_link(1) == file_temp.file.url


def test_get_batch_export_file_link_returns_none_for_unknown_tag(cycle, payment_plan_group):
    assert payment_plan_group.get_batch_export_file_link(99) is None


def test_get_batch_export_file_link_returns_none_when_plan_has_no_file(cycle, payment_plan_group):
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=payment_plan_group,
        export_tag=1,
        export_file_delivery=None,
    )

    assert payment_plan_group.get_batch_export_file_link(1) is None
