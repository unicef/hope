import importlib
from typing import Any

from django.apps.registry import Apps
from django.db import connection
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.loader import MigrationLoader
import pytest

from extras.test_utils.factories import PaymentListFactory, PaymentPlanFactory, ProgramCycleFactory
from extras.test_utils.factories.payment import FollowUpInstructionFactory
from hope.models import FollowUpInstruction, PaymentList, PaymentPlan, PaymentPlanSupportingDocument

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.payment.migrations.0084_migration")


@pytest.fixture
def schema_editor() -> BaseDatabaseSchemaEditor:
    return connection.schema_editor()


@pytest.fixture
def historical_apps(settings: Any) -> Apps:
    """The models the data step runs with: a document still points at its plan, and may have no owner yet."""
    settings.MIGRATION_MODULES = {}
    state = MigrationLoader(connection).project_state(("payment", "0083_migration"))
    with connection.cursor() as cursor:
        cursor.execute(
            'ALTER TABLE "payment_paymentplansupportingdocument" ADD COLUMN "payment_plan_id" uuid NULL, '
            'DROP CONSTRAINT "supporting_document_has_one_owner"'
        )
    return state.apps


@pytest.fixture
def cycle() -> Any:
    return ProgramCycleFactory()


@pytest.fixture
def group(cycle: Any) -> PaymentPlan:
    return PaymentPlanFactory(cycle=cycle)


@pytest.fixture
def instruction(cycle: Any) -> FollowUpInstruction:
    return FollowUpInstructionFactory(program=cycle.program)


@pytest.fixture
def grouped_plan(cycle: Any, group: PaymentPlan) -> PaymentList:
    return PaymentListFactory(program_cycle=cycle, payment_plan=group)


@pytest.fixture
def instruction_child(cycle: Any, instruction: FollowUpInstruction) -> PaymentList:
    return PaymentListFactory(
        program_cycle=cycle, follow_up_instruction=instruction, plan_type=PaymentList.PlanType.FOLLOW_UP
    )


@pytest.fixture
def removed_plan_without_group(cycle: Any, group: PaymentPlan) -> PaymentList:
    payment_list = PaymentListFactory(program_cycle=cycle, payment_plan=group)
    with connection.cursor() as cursor:
        cursor.execute(
            'UPDATE "payment_paymentplan" SET "payment_plan_group_id" = NULL, "is_removed" = true WHERE "id" = %s',
            [payment_list.pk],
        )
    return payment_list


@pytest.fixture
def document_of_grouped_plan(historical_apps: Apps, grouped_plan: PaymentList) -> Any:
    document_model = historical_apps.get_model("payment", "PaymentPlanSupportingDocument")
    return document_model.objects.create(title="grouped", file="grouped.pdf", payment_plan_id=grouped_plan.pk)


@pytest.fixture
def document_of_instruction_child(historical_apps: Apps, instruction_child: PaymentList) -> Any:
    document_model = historical_apps.get_model("payment", "PaymentPlanSupportingDocument")
    return document_model.objects.create(title="child", file="child.pdf", payment_plan_id=instruction_child.pk)


@pytest.fixture
def document_of_removed_plan(historical_apps: Apps, removed_plan_without_group: PaymentList) -> Any:
    document_model = historical_apps.get_model("payment", "PaymentPlanSupportingDocument")
    return document_model.objects.create(
        title="removed", file="removed.pdf", payment_plan_id=removed_plan_without_group.pk
    )


def test_document_moves_to_the_group_of_its_plan(
    historical_apps: Apps, schema_editor: BaseDatabaseSchemaEditor, group: PaymentPlan, document_of_grouped_plan: Any
) -> None:
    migration_module.move_documents_to_groups_and_instructions(historical_apps, schema_editor)

    document = PaymentPlanSupportingDocument.objects.get(pk=document_of_grouped_plan.pk)
    assert document.payment_plan == group
    assert document.follow_up_instruction is None


def test_document_moves_to_the_instruction_of_its_plan(
    historical_apps: Apps,
    schema_editor: BaseDatabaseSchemaEditor,
    instruction: FollowUpInstruction,
    document_of_instruction_child: Any,
) -> None:
    migration_module.move_documents_to_groups_and_instructions(historical_apps, schema_editor)

    document = PaymentPlanSupportingDocument.objects.get(pk=document_of_instruction_child.pk)
    assert document.follow_up_instruction == instruction
    assert document.payment_plan is None


def test_document_of_a_removed_plan_without_owner_is_deleted(
    historical_apps: Apps, schema_editor: BaseDatabaseSchemaEditor, document_of_removed_plan: Any
) -> None:
    migration_module.move_documents_to_groups_and_instructions(historical_apps, schema_editor)

    assert not PaymentPlanSupportingDocument.objects.filter(pk=document_of_removed_plan.pk).exists()
