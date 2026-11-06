import datetime
from decimal import Decimal
from typing import Any

from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    ApprovalProcessFactory,
    CurrencyFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentHouseholdSnapshotFactory,
    PaymentListFactory,
    PaymentPlanFactory,
    RuleCommitFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.factories.targeting import TargetingCriteriaRuleFactory, TargetingCriteriaRuleFilterFactory
from hope.apps.account.permissions import Permissions
from hope.apps.payment.services.follow_up_instruction_service import FollowUpInstructionService
from hope.apps.payment.services.payment_list_services import PaymentListService
from hope.models import (
    BusinessArea,
    Currency,
    DeliveryMechanism,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    FollowUpInstruction,
    Payment,
    PaymentList,
    PaymentPlan,
    Program,
    ProgramCycle,
    Rule,
    User,
)

ENTITLEMENT_RULE_NAME = "Household Size Entitlement"
ENTITLEMENT_RULE_DEFINITION = 'result.value = context["household"].size * 10'
PM_VIEW_PERMISSIONS = (
    Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    Permissions.PM_VIEW_LIST,
    Permissions.PM_VIEW_DETAILS,
)


def payment_list_url(payment_list: PaymentList) -> str:
    return (
        f"/{payment_list.business_area.slug}/programs/{payment_list.program.code}"
        f"/payment-module/payment-lists/{payment_list.id}"
    )


def payment_plan_url(payment_list: PaymentList) -> str:
    return (
        f"/{payment_list.business_area.slug}/programs/{payment_list.program.code}"
        f"/payment-module/payment-plans/{payment_list.payment_plan_id}"
    )


def _group_with_plan(
    program_cycle: ProgramCycle, group_status: str, plan_status: str, **group_fields: Any
) -> PaymentPlan:
    group = PaymentPlanFactory(cycle=program_cycle, status=group_status, **group_fields)
    PaymentListFactory(
        business_area=program_cycle.program.business_area,
        program_cycle=program_cycle,
        payment_plan=group,
        status=plan_status,
        financial_service_provider=FinancialServiceProviderFactory(),
        delivery_mechanism=DeliveryMechanismFactory(),
    )
    return group


@pytest.fixture
def finished_group(program_cycle: ProgramCycle) -> PaymentPlan:
    return _group_with_plan(program_cycle, PaymentPlan.Status.FINISHED, PaymentList.Status.FINISHED)


@pytest.fixture
def locked_payment_plan(program_cycle: ProgramCycle) -> PaymentPlan:
    return _group_with_plan(program_cycle, PaymentPlan.Status.LOCKED, PaymentList.Status.LOCKED)


@pytest.fixture
def closed_group(program_cycle: ProgramCycle, create_super_user: Any) -> PaymentPlan:
    group = _group_with_plan(
        program_cycle,
        PaymentPlan.Status.CLOSED,
        PaymentList.Status.CLOSED,
        closed_by=create_super_user,
        status_date=timezone.now(),
    )
    ApprovalProcessFactory(payment_plan=group)
    return group


@pytest.fixture
def payment_list_for_pagination(business_area: BusinessArea) -> tuple[PaymentList, str, str]:
    """OPEN plan with 12 eligible payments -> 2 pages at the default page size of 10.

    Regression fixture for PR #6064 (https://github.com/unicef/hope/pull/6064). Returns
    (plan, page_one_marker_unicef_id, page_two_marker_unicef_id). created_at is assigned
    explicitly so the frontend's default ordering=-created_at deterministically keeps the
    newest payment on page 1 and the oldest on page 2.
    """
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    plan = PaymentListFactory(
        business_area=business_area,
        program_cycle=program.cycles.first(),
        status=PaymentList.Status.OPEN,
        financial_service_provider=FinancialServiceProviderFactory(),
        delivery_mechanism=DeliveryMechanismFactory(),
    )
    # Each payment needs a distinct household (unique constraint on parent + household);
    # PaymentFactory auto-builds one per payment, inheriting the plan's business area/program.
    payments = PaymentFactory.create_batch(12, parent=plan, program=program)
    base = timezone.now()
    for index, payment in enumerate(payments):
        # index 0 = newest (page 1), index 11 = oldest (page 2, last row).
        Payment.objects.filter(pk=payment.pk).update(created_at=base - datetime.timedelta(minutes=index))
    return plan, payments[0].unicef_id, payments[11].unicef_id


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
def payment_plan(program_cycle: ProgramCycle) -> PaymentPlan:
    return PaymentPlanFactory(cycle=program_cycle, name="Original Group Name")


@pytest.fixture
def second_payment_plan(program_cycle: ProgramCycle) -> PaymentPlan:
    return PaymentPlanFactory(cycle=program_cycle, name="Second Group")


@pytest.fixture
def fi_currency() -> Currency:
    # USD has an exchange rate of 1.0 in the committed exchange_rates.json, so
    # USD-denominated totals mirror the local-currency amounts and stay stable
    # when the follow-up workflow recalculates entitlement_quantity_usd.
    return CurrencyFactory(code="USD")


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
) -> tuple[PaymentPlan, PaymentPlan]:
    """Two FINISHED source plans in separate cycles/groups with failed payments.

    hh_a: failed payments in BOTH plans (demonstrates >1 failed payment per household).
    hh_b: failed payment in plan_one only.
    hh_c: failed payment in plan_two only.

    Returns (group_one, group_two).
    """
    ba = fi_program.business_area
    cycle_one = ProgramCycleFactory(program=fi_program)
    cycle_two = ProgramCycleFactory(program=fi_program)
    group_one = cycle_one.payment_plans.first()
    group_two = cycle_two.payment_plans.first()

    plan_one = PaymentListFactory(
        name="FI Source Plan One",
        program_cycle=cycle_one,
        payment_plan=group_one,
        business_area=ba,
        currency=fi_currency,
        delivery_mechanism=fi_delivery_mechanism,
        financial_service_provider=fi_fsp,
        status=PaymentList.Status.FINISHED,
    )
    plan_two = PaymentListFactory(
        name="FI Source Plan Two",
        program_cycle=cycle_two,
        payment_plan=group_two,
        business_area=ba,
        currency=fi_currency,
        delivery_mechanism=fi_delivery_mechanism,
        financial_service_provider=fi_fsp,
        status=PaymentList.Status.FINISHED,
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
    fi_source_plans: tuple[PaymentPlan, PaymentPlan],
    fi_program: Program,
) -> FollowUpInstruction:
    """Follow-up instruction created at OPEN state from fi_source_plans."""
    group_one, group_two = fi_source_plans
    user = User.objects.get(username="superuser")
    service = FollowUpInstructionService(program=fi_program)
    return service.create(
        user=user,
        payment_plan_ids=[str(group_one.pk), str(group_two.pk)],
        dispersion_start_date=datetime.date(2027, 1, 1),
        dispersion_end_date=datetime.date(2027, 12, 31),
    )


def _entitlement_payment_list(
    business_area: BusinessArea,
    status: str,
    entitlements: tuple[Decimal | None, Decimal | None],
) -> PaymentList:
    program = ProgramFactory(name="Entitlement E2E Program", status=Program.ACTIVE, business_area=business_area)
    delivery_mechanism = DeliveryMechanismFactory(
        code="entitlement-e2e", name="Entitlement E2E", payment_gateway_id="entitlement-e2e"
    )
    fsp = FinancialServiceProviderFactory(name="Entitlement E2E Provider")
    fsp.delivery_mechanisms.add(delivery_mechanism)
    currency = CurrencyFactory(code="PLN", name="Polish Zloty")
    cycle = ProgramCycleFactory(program=program)
    group = PaymentPlanFactory(cycle=cycle, exchange_rate=Decimal("2.0"), currency=currency)
    payment_list = PaymentListFactory(
        name="Entitlement E2E Payment Plan",
        program_cycle=cycle,
        payment_plan=group,
        business_area=business_area,
        status=status,
        plan_type=PaymentList.PlanType.REGULAR,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        currency=currency,
    )
    for index, (size, entitlement) in enumerate(zip((1, 3), entitlements, strict=True), start=1):
        household = HouseholdFactory(size=size, business_area=business_area, program=program)
        payment = PaymentFactory(
            parent=payment_list,
            household=household,
            collector=household.head_of_household,
            head_of_household=household.head_of_household,
            program=program,
            unicef_id=f"RCPT-ENTITLEMENT-E2E-{index}",
            status=Payment.STATUS_PENDING,
            currency=currency,
            delivery_type=delivery_mechanism,
            financial_service_provider=fsp,
            entitlement_quantity=entitlement,
            entitlement_quantity_usd=entitlement / 2 if entitlement is not None else None,
            delivered_quantity=None,
            delivered_quantity_usd=None,
        )
        payment.save(update_fields=["unicef_id"])
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
    payment_list.update_money_fields()
    return payment_list


@pytest.fixture
def locked_entitlement_payment_list(business_area: BusinessArea) -> PaymentList:
    return _entitlement_payment_list(business_area, PaymentList.Status.LOCKED, (None, None))


@pytest.fixture
def entitled_locked_payment_list(business_area: BusinessArea) -> PaymentList:
    return _entitlement_payment_list(business_area, PaymentList.Status.LOCKED, (Decimal("10.00"), Decimal("30.00")))


@pytest.fixture
def entitled_open_payment_list(business_area: BusinessArea) -> PaymentList:
    return _entitlement_payment_list(business_area, PaymentList.Status.OPEN, (Decimal("100.00"), Decimal("300.00")))


@pytest.fixture
def household_size_entitlement_rule(business_area: BusinessArea) -> Rule:
    commit = RuleCommitFactory(
        rule__name=ENTITLEMENT_RULE_NAME,
        rule__type=Rule.TYPE_PAYMENT_LIST,
        rule__enabled=True,
        rule__definition=ENTITLEMENT_RULE_DEFINITION,
        definition=ENTITLEMENT_RULE_DEFINITION,
        enabled=True,
        is_release=True,
    )
    commit.rule.allowed_business_areas.add(business_area)
    return commit.rule


@pytest.fixture
def cycles_program(business_area: BusinessArea) -> Program:
    today = timezone.now().date()
    program = ProgramFactory(
        business_area=business_area,
        status=Program.ACTIVE,
        start_date=today - datetime.timedelta(days=30),
        end_date=today + datetime.timedelta(days=30),
        cycle=False,
    )
    ProgramCycleFactory(
        program=program,
        title="Default Programme Cycle",
        status=ProgramCycle.FINISHED,
        start_date=today - datetime.timedelta(days=25),
        end_date=today - datetime.timedelta(days=20),
    )
    return program


@pytest.fixture
def active_cycle(cycles_program: Program) -> ProgramCycle:
    today = timezone.now().date()
    cycle = ProgramCycleFactory(
        program=cycles_program,
        title="Test Programme Cycle 001",
        status=ProgramCycle.ACTIVE,
        start_date=today,
        end_date=today + datetime.timedelta(days=5),
    )
    ProgramCycleFactory(
        program=cycles_program,
        title="Programme Cycle in Draft",
        status=ProgramCycle.DRAFT,
        start_date=today + datetime.timedelta(days=6),
        end_date=today + datetime.timedelta(days=16),
    )
    return cycle


@pytest.fixture
def active_cycle_with_payment_lists(active_cycle: ProgramCycle) -> ProgramCycle:
    business_area = active_cycle.program.business_area
    PaymentListFactory(
        program_cycle=active_cycle, business_area=business_area, total_entitled_quantity_usd=Decimal("333.99")
    )
    PaymentListFactory(
        program_cycle=active_cycle, business_area=business_area, total_entitled_quantity_usd=Decimal("1500.00")
    )
    return active_cycle


LIFECYCLE_PAYMENT_LIST_NAME = "Lifecycle E2E Payment Plan"


def _lifecycle_payment_list(
    business_area: BusinessArea,
    group_status: str,
    plan_status: str,
    payments_count: int = 3,
    collectors_count: int | None = None,
) -> PaymentList:
    """Payment plan in a group with an FSP, a delivery mechanism, USD and `payments_count` payments.

    `collectors_count` makes payments share that many collectors, for split by collector.
    """
    program = ProgramFactory(name="Lifecycle E2E Program", status=Program.ACTIVE, business_area=business_area)
    delivery_mechanism = DeliveryMechanismFactory(
        code="lifecycle-e2e", name="Lifecycle E2E", payment_gateway_id="lifecycle-e2e"
    )
    fsp = FinancialServiceProviderFactory(name="Lifecycle E2E Provider")
    fsp.delivery_mechanisms.add(delivery_mechanism)
    fsp.allowed_business_areas.add(business_area)
    currency = CurrencyFactory(code="USD", name="United States Dollar")
    cycle = ProgramCycleFactory(program=program)
    group = PaymentPlanFactory(cycle=cycle, name="Lifecycle E2E Group", status=group_status)
    payment_list = PaymentListFactory(
        name=LIFECYCLE_PAYMENT_LIST_NAME,
        program_cycle=cycle,
        payment_plan=group,
        business_area=business_area,
        status=plan_status,
        plan_type=PaymentList.PlanType.REGULAR,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        currency=currency,
    )
    households = [HouseholdFactory(business_area=business_area, program=program) for _ in range(payments_count)]
    collectors = [household.head_of_household for household in households[: collectors_count or payments_count]]
    for index, household in enumerate(households):
        payment = PaymentFactory(
            parent=payment_list,
            household=household,
            collector=collectors[index % len(collectors)],
            head_of_household=household.head_of_household,
            program=program,
            status=Payment.STATUS_PENDING,
            currency=currency,
            delivery_type=delivery_mechanism,
            financial_service_provider=fsp,
            entitlement_quantity=Decimal("10.00"),
            entitlement_quantity_usd=Decimal("10.00"),
            delivered_quantity=None,
            delivered_quantity_usd=None,
        )
        PaymentHouseholdSnapshotFactory(payment=payment, snapshot_data={})
    if group_status in (PaymentPlan.Status.IN_APPROVAL, PaymentPlan.Status.IN_AUTHORIZATION):
        ApprovalProcessFactory(payment_plan=group)
    payment_list.update_money_fields()
    return payment_list


@pytest.fixture
def in_approval_group(business_area: BusinessArea) -> PaymentPlan:
    return _lifecycle_payment_list(
        business_area, PaymentPlan.Status.IN_APPROVAL, PaymentList.Status.IN_APPROVAL
    ).payment_plan


@pytest.fixture
def in_authorization_group(business_area: BusinessArea) -> PaymentPlan:
    return _lifecycle_payment_list(
        business_area, PaymentPlan.Status.IN_AUTHORIZATION, PaymentList.Status.IN_AUTHORIZATION
    ).payment_plan


@pytest.fixture
def locked_lifecycle_group(business_area: BusinessArea) -> PaymentPlan:
    return _lifecycle_payment_list(business_area, PaymentPlan.Status.LOCKED, PaymentList.Status.LOCKED_FSP).payment_plan


@pytest.fixture
def accepted_lifecycle_group(business_area: BusinessArea) -> PaymentPlan:
    return _lifecycle_payment_list(
        business_area, PaymentPlan.Status.ACCEPTED, PaymentList.Status.ACCEPTED, payments_count=25
    ).payment_plan


@pytest.fixture
def accepted_shared_collectors_group(business_area: BusinessArea) -> PaymentPlan:
    return _lifecycle_payment_list(
        business_area,
        PaymentPlan.Status.ACCEPTED,
        PaymentList.Status.ACCEPTED,
        payments_count=12,
        collectors_count=3,
    ).payment_plan


@pytest.fixture
def open_payment_list(business_area: BusinessArea) -> PaymentList:
    return _lifecycle_payment_list(business_area, PaymentPlan.Status.OPEN, PaymentList.Status.OPEN)


@pytest.fixture
def open_lifecycle_group(business_area: BusinessArea) -> PaymentPlan:
    """OPEN group whose plan is still in targeting, so its currency can still be changed."""
    return _lifecycle_payment_list(business_area, PaymentPlan.Status.OPEN, PaymentList.Status.TP_OPEN).payment_plan


@pytest.fixture
def aborted_targeted_group(business_area: BusinessArea) -> PaymentPlan:
    """ABORTED group whose plan's targeting matches the programme's 3 households, so Reactivate can rebuild it."""
    payment_list = _lifecycle_payment_list(
        business_area, PaymentPlan.Status.OPEN, PaymentList.Status.TP_OPEN, payments_count=0
    )
    rule = TargetingCriteriaRuleFactory(payment_list=payment_list)
    TargetingCriteriaRuleFilterFactory(targeting_criteria_rule=rule, comparison_method="RANGE", arguments=[1, 10])
    for size in (1, 3, 5):
        HouseholdFactory(size=size, business_area=business_area, program=payment_list.program)
    PaymentListService(payment_list).full_rebuild()
    payment_list.status = PaymentList.Status.ABORTED
    payment_list.build_status = PaymentList.BuildStatus.BUILD_STATUS_OK
    payment_list.abort_comment = "Aborted before the e2e run"
    payment_list.save(update_fields=["status", "build_status", "abort_comment"])
    group = payment_list.payment_plan
    group.status = PaymentPlan.Status.ABORTED
    group.abort_comment = "Aborted before the e2e run"
    group.save(update_fields=["status", "abort_comment"])
    return group
