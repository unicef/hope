from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test.utils import CaptureQueriesContext
import pytest

from extras.test_utils.factories import (
    FileTempFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
)
from hope.models import PaymentPlanGroup

pytestmark = pytest.mark.django_db


@pytest.fixture
def cycle():
    return ProgramCycleFactory()


@pytest.fixture
def payment_plan_group(cycle):
    return PaymentPlanGroupFactory(cycle=cycle)


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
