import datetime
from decimal import Decimal

import pytest

from extras.test_utils.factories import (
    CurrencyFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentHouseholdSnapshotFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.payment.services.follow_up_instruction_service import FollowUpInstructionService
from hope.models import (
    BusinessArea,
    Currency,
    DeliveryMechanism,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    FollowUpInstruction,
    Payment,
    PaymentPlan,
    PaymentPlanGroup,
    Program,
    ProgramCycle,
    User,
)


@pytest.fixture
def payment_module_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(
        name="Payment Module Program",
        status=Program.ACTIVE,
        business_area=business_area,
    )


@pytest.fixture
def program_cycle(payment_module_program: Program) -> ProgramCycle:
    return ProgramCycleFactory(program=payment_module_program)


@pytest.fixture
def payment_plan_group(program_cycle: ProgramCycle) -> PaymentPlanGroup:
    return PaymentPlanGroupFactory(cycle=program_cycle, name="Original Group Name")


@pytest.fixture
def group_with_payment_plan(program_cycle: ProgramCycle) -> PaymentPlanGroup:
    group = program_cycle.payment_plan_groups.first()
    PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=program_cycle.program.business_area,
        status=PaymentPlan.Status.OPEN,
    )
    return group


@pytest.fixture
def fi_currency() -> Currency:
    return CurrencyFactory(code="AFN")


@pytest.fixture
def fi_delivery_mechanism() -> DeliveryMechanism:
    return DeliveryMechanismFactory(code="dm-fi-cash", name="FI Cash", payment_gateway_id="dm-fi-cash")


@pytest.fixture
def fi_fsp(fi_delivery_mechanism: DeliveryMechanism) -> FinancialServiceProvider:
    fsp = FinancialServiceProviderFactory()
    fsp.delivery_mechanisms.add(fi_delivery_mechanism)
    return fsp


@pytest.fixture
def fi_xlsx_template(
    fi_fsp: FinancialServiceProvider,
    fi_delivery_mechanism: DeliveryMechanism,
) -> FinancialServiceProviderXlsxTemplate:
    tmpl = FinancialServiceProviderXlsxTemplateFactory(
        columns=["payment_id", "household_id", "entitlement_quantity", "delivered_quantity"],
        core_fields=[],
        flex_fields=[],
        document_types=[],
    )
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fi_fsp,
        delivery_mechanism=fi_delivery_mechanism,
        xlsx_template=tmpl,
    )
    return tmpl


@pytest.fixture
def fi_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(
        name="Follow-up Instruction E2E Program",
        status=Program.ACTIVE,
        business_area=business_area,
    )


@pytest.fixture
def fi_source_plans(
    fi_program: Program,
    fi_currency: Currency,
    fi_delivery_mechanism: DeliveryMechanism,
    fi_fsp: FinancialServiceProvider,
    fi_xlsx_template: FinancialServiceProviderXlsxTemplate,
) -> tuple[PaymentPlanGroup, PaymentPlanGroup]:
    """Two FINISHED source plans in separate cycles/groups with failed payments.

    hh_a: failed payments in BOTH plans (demonstrates >1 failed payment per household).
    hh_b: failed payment in plan_one only.
    hh_c: failed payment in plan_two only.

    Returns (group_one, group_two).
    """
    ba = fi_program.business_area
    cycle_one = ProgramCycleFactory(program=fi_program)
    cycle_two = ProgramCycleFactory(program=fi_program)
    group_one = cycle_one.payment_plan_groups.first()
    group_two = cycle_two.payment_plan_groups.first()

    plan_one = PaymentPlanFactory(
        program_cycle=cycle_one,
        payment_plan_group=group_one,
        business_area=ba,
        currency=fi_currency,
        delivery_mechanism=fi_delivery_mechanism,
        financial_service_provider=fi_fsp,
        status=PaymentPlan.Status.FINISHED,
    )
    plan_two = PaymentPlanFactory(
        program_cycle=cycle_two,
        payment_plan_group=group_two,
        business_area=ba,
        currency=fi_currency,
        delivery_mechanism=fi_delivery_mechanism,
        financial_service_provider=fi_fsp,
        status=PaymentPlan.Status.FINISHED,
    )

    hh_a = HouseholdFactory(business_area=ba, program=fi_program)
    hh_b = HouseholdFactory(business_area=ba, program=fi_program)
    hh_c = HouseholdFactory(business_area=ba, program=fi_program)

    for parent, household, entitlement in [
        (plan_one, hh_a, Decimal("100.00")),
        (plan_two, hh_a, Decimal("40.00")),
        (plan_one, hh_b, Decimal("60.00")),
        (plan_two, hh_c, Decimal("80.00")),
    ]:
        payment = PaymentFactory(
            parent=parent,
            household=household,
            collector=household.head_of_household,
            head_of_household=household.head_of_household,
            program=fi_program,
            currency=fi_currency,
            delivery_type=fi_delivery_mechanism,
            financial_service_provider=fi_fsp,
            entitlement_quantity=entitlement,
            entitlement_quantity_usd=entitlement,
            delivered_quantity=Decimal("0.00"),
            status=Payment.STATUS_ERROR,
        )
        PaymentHouseholdSnapshotFactory(
            payment=payment,
            snapshot_data={
                "unicef_id": household.unicef_id,
                "size": household.size,
                "primary_collector": {
                    "unicef_id": household.head_of_household.unicef_id,
                    "full_name": household.head_of_household.full_name,
                },
                "alternate_collector": {},
            },
        )

    return group_one, group_two


@pytest.fixture
def fi_instruction(
    fi_source_plans: tuple[PaymentPlanGroup, PaymentPlanGroup],
    fi_program: Program,
) -> FollowUpInstruction:
    """Follow-up instruction created at OPEN state from fi_source_plans."""
    group_one, group_two = fi_source_plans
    user = User.objects.get(username="superuser")
    service = FollowUpInstructionService(program=fi_program)
    return service.create(
        user=user,
        payment_plan_group_ids=[str(group_one.pk), str(group_two.pk)],
        dispersion_start_date=datetime.date(2027, 1, 1),
        dispersion_end_date=datetime.date(2027, 12, 31),
    )


@pytest.fixture
def fi_instruction_at_accepted(fi_instruction: FollowUpInstruction) -> FollowUpInstruction:
    """Follow-up instruction driven to ACCEPTED state without a browser."""
    user = User.objects.get(username="superuser")
    svc = FollowUpInstructionService(instruction=fi_instruction)
    for action in [
        PaymentPlan.Action.LOCK,
        PaymentPlan.Action.LOCK_FSP,
        PaymentPlan.Action.SEND_FOR_APPROVAL,
        PaymentPlan.Action.APPROVE,
        PaymentPlan.Action.AUTHORIZE,
        PaymentPlan.Action.REVIEW,
    ]:
        svc.execute_payment_plan_action(action, user)
    fi_instruction.refresh_from_db()
    return fi_instruction
