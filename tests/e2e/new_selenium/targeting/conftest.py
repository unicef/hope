import pytest

from extras.test_utils.factories import (
    HouseholdFactory,
    PaymentPlanGroupFactory,
    PaymentPlanPurposeFactory,
)
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentPlanFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.factories.steficon import RuleCommitFactory
from extras.test_utils.factories.targeting import TargetingCriteriaRuleFactory, TargetingCriteriaRuleFilterFactory
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.models import (
    BusinessArea,
    Household,
    PaymentPlan,
    PaymentPlanGroup,
    PaymentPlanPurpose,
    Program,
    ProgramCycle,
    Rule,
)

PURPOSE_NAME = "Test Purpose"
OTHER_PURPOSE_NAME = "Other Purpose"
GROUP_NAME = "Test Group"
CYCLE_TITLE = "Test Cycle"
SECOND_CYCLE_TITLE = "Second Cycle"
SECOND_GROUP_NAME = "Second Group"
BUILT_TP_NAME = "Built TP"
RULE_NAME = "Household Size Score"
RULE_DEFINITION = 'result.value = context["household"].size'


@pytest.fixture
def tp_purpose() -> PaymentPlanPurpose:
    return PaymentPlanPurposeFactory(name=PURPOSE_NAME)


@pytest.fixture
def targeting_program(business_area: BusinessArea, tp_purpose: PaymentPlanPurpose) -> Program:
    # Program.clean() requires at least one purpose before status=ACTIVE save
    prog = ProgramFactory(business_area=business_area, status=Program.DRAFT, cycle=False)
    prog.payment_plan_purposes.add(tp_purpose)
    prog.status = Program.ACTIVE
    prog.save()
    return prog


@pytest.fixture
def targeting_household(targeting_program: Program) -> Household:
    return HouseholdFactory(
        unicef_id="HH-22-0001.0001",
        business_area=targeting_program.business_area,
        program=targeting_program,
    )


@pytest.fixture
def targeting_cycle(targeting_program: Program) -> ProgramCycle:
    return ProgramCycleFactory(program=targeting_program, title=CYCLE_TITLE)


@pytest.fixture
def targeting_group(targeting_cycle: ProgramCycle) -> PaymentPlanGroup:
    return PaymentPlanGroupFactory(cycle=targeting_cycle, name=GROUP_NAME)


@pytest.fixture
def second_targeting_cycle(targeting_program: Program) -> ProgramCycle:
    return ProgramCycleFactory(program=targeting_program, title=SECOND_CYCLE_TITLE)


@pytest.fixture
def second_targeting_group(second_targeting_cycle: ProgramCycle) -> PaymentPlanGroup:
    return PaymentPlanGroupFactory(cycle=second_targeting_cycle, name=SECOND_GROUP_NAME)


@pytest.fixture
def targeting_tp(targeting_group: PaymentPlanGroup, tp_purpose: PaymentPlanPurpose) -> PaymentPlan:
    tp = PaymentPlanFactory(
        name="Test TP",
        program_cycle=targeting_group.cycle,
        payment_plan_group=targeting_group,
        status=PaymentPlan.Status.TP_OPEN,
        business_area=targeting_group.cycle.program.business_area,
    )
    tp.payment_plan_purposes.add(tp_purpose)
    rule = TargetingCriteriaRuleFactory(payment_plan=tp)
    TargetingCriteriaRuleFilterFactory(targeting_criteria_rule=rule, comparison_method="RANGE", arguments=[1, 10])
    # Remove any stale PPs in this cycle that could make targeting_tp appear non-latest
    PaymentPlan.objects.filter(program_cycle=targeting_group.cycle).exclude(id=tp.id).delete()
    return tp


@pytest.fixture
def other_purpose() -> PaymentPlanPurpose:
    return PaymentPlanPurposeFactory(name=OTHER_PURPOSE_NAME)


@pytest.fixture
def later_tp(targeting_tp: PaymentPlan, targeting_group: PaymentPlanGroup) -> PaymentPlan:
    return PaymentPlanFactory(
        program_cycle=targeting_tp.program_cycle,
        payment_plan_group=targeting_group,
        status=PaymentPlan.Status.TP_OPEN,
        business_area=targeting_tp.business_area,
    )


@pytest.fixture
def sized_households(targeting_program: Program) -> list[Household]:
    return [
        HouseholdFactory(
            unicef_id=f"HH-23-0000.000{size}",
            size=size,
            business_area=targeting_program.business_area,
            program=targeting_program,
        )
        for size in (1, 3, 5)
    ]


@pytest.fixture
def built_tp(
    targeting_group: PaymentPlanGroup,
    tp_purpose: PaymentPlanPurpose,
    sized_households: list[Household],
) -> PaymentPlan:
    tp = PaymentPlanFactory(
        name=BUILT_TP_NAME,
        program_cycle=targeting_group.cycle,
        payment_plan_group=targeting_group,
        status=PaymentPlan.Status.TP_OPEN,
        business_area=targeting_group.cycle.program.business_area,
    )
    tp.payment_plan_purposes.add(tp_purpose)
    rule = TargetingCriteriaRuleFactory(payment_plan=tp)
    TargetingCriteriaRuleFilterFactory(targeting_criteria_rule=rule, comparison_method="RANGE", arguments=[1, 10])
    PaymentPlanService(tp).full_rebuild()
    tp.build_status = PaymentPlan.BuildStatus.BUILD_STATUS_OK
    tp.save(update_fields=["build_status"])
    tp.refresh_from_db()
    return tp


@pytest.fixture
def locked_tp(built_tp: PaymentPlan) -> PaymentPlan:
    # Mark Ready needs an FSP and delivery mechanism on the target population.
    built_tp.status = PaymentPlan.Status.TP_LOCKED
    built_tp.financial_service_provider = FinancialServiceProviderFactory()
    built_tp.delivery_mechanism = DeliveryMechanismFactory()
    built_tp.save(update_fields=["status", "financial_service_provider", "delivery_mechanism"])
    return built_tp


@pytest.fixture
def household_size_rule(business_area: BusinessArea) -> Rule:
    commit = RuleCommitFactory(
        rule__name=RULE_NAME,
        rule__type=Rule.TYPE_TARGETING,
        rule__enabled=True,
        rule__definition=RULE_DEFINITION,
        definition=RULE_DEFINITION,
        enabled=True,
        is_release=True,
    )
    commit.rule.allowed_business_areas.add(business_area)
    return commit.rule
