from collections.abc import Generator
from datetime import UTC, timedelta
from decimal import Decimal
import logging
from typing import Any
from unittest import mock
from unittest.mock import patch
import uuid

from aniso8601 import parse_date
from constance.test import override_config
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.timezone import now
from flags.models import FlagState
from freezegun import freeze_time
import pytest
import requests_mock as requests_mock_lib
from rest_framework.exceptions import ValidationError
from viewflow.fsm import TransitionNotAllowed

from extras.test_utils.factories import (
    AccountFactory,
    AccountTypeFactory,
    ApprovalFactory,
    ApprovalProcessFactory,
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    CurrencyFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FollowUpInstructionFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentListFactory,
    PaymentListSplitFactory,
    PaymentPlanFactory,
    PaymentPlanPurposeFactory,
    ProgramCycleFactory,
    ProgramFactory,
    TargetingCriteriaRuleFactory,
    TargetingIndividualBlockRuleFilterFactory,
    TargetingIndividualRuleFilterBlockFactory,
    UserFactory,
)
from extras.test_utils.factories.steficon import RuleCommitFactory
from hope.apps.account.permissions import Permissions
from hope.apps.household.const import ROLE_PRIMARY
from hope.apps.payment.celery_tasks import (
    prepare_child_payment_list_async_task,
    prepare_payment_list_async_task,
)
from hope.apps.payment.flows import PaymentListFlow
from hope.apps.payment.services.payment_list_services import PaymentListService
from hope.models import (
    AccountType,
    BusinessArea,
    DeliveryMechanism,
    DeliveryMechanismConfig,
    FileTemp,
    FinancialServiceProvider,
    IndividualRoleInHousehold,
    LogEntry,
    Payment,
    PaymentList,
    PaymentListSplit,
    PaymentPlan,
    Program,
    ProgramCycle,
    Role,
    RoleAssignment,
    TargetingIndividualBlockRuleFilter,
    User,
)

pytestmark = pytest.mark.django_db


def test_update_delivery_mechanism_returns_false_when_not_open(business_area: Any, cycle: ProgramCycle) -> None:
    pp = PaymentListFactory(
        program_cycle=cycle,
        business_area=business_area,
        status=PaymentList.Status.LOCKED,
    )
    service = PaymentListService(payment_list=pp)
    result = service._update_delivery_mechanism(delivery_mechanism_code="some-code")
    assert result is False


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def dm_transfer_to_account() -> Any:
    return DeliveryMechanismFactory(
        code="transfer_to_account",
        name="Transfer to Account",
        payment_gateway_id="dm-transfer-account",
    )


@pytest.fixture
def dm_transfer_to_digital_wallet() -> Any:
    return DeliveryMechanismFactory(
        code="transfer_to_digital_wallet",
        name="Transfer to Digital Wallet",
        payment_gateway_id="dm-transfer-wallet",
        transfer_type=DeliveryMechanism.TransferType.DIGITAL,
    )


@pytest.fixture
def fsp(
    business_area: BusinessArea, dm_transfer_to_account: Any, dm_transfer_to_digital_wallet: Any
) -> FinancialServiceProvider:
    fsp = FinancialServiceProviderFactory(
        name="Test FSP 1",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
    )
    fsp.delivery_mechanisms.add(dm_transfer_to_account, dm_transfer_to_digital_wallet)
    fsp.allowed_business_areas.add(business_area)
    return fsp


@pytest.fixture
def account_type_bank() -> AccountType:
    return AccountTypeFactory(key="bank", label="Bank")


@pytest.fixture
def program(business_area: Any) -> Program:
    return ProgramFactory(status=Program.ACTIVE, business_area=business_area, cycle=False)


@pytest.fixture
def cycle(program: Program) -> ProgramCycle:
    return ProgramCycleFactory(status=ProgramCycle.ACTIVE, program=program)


@pytest.fixture
def lock_status_transition_context(
    user: User,
    business_area: BusinessArea,
    cycle: ProgramCycle,
) -> dict[str, Any]:
    purpose = PaymentPlanPurposeFactory()
    cycle.program.payment_plan_purposes.add(purpose)
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.OPEN,
    )
    payment_list.payment_plan_purposes.add(purpose)
    conflicting_plan = PaymentListFactory(
        program_cycle=cycle,
        business_area=business_area,
        status=PaymentList.Status.LOCKED,
    )
    conflicting_plan.payment_plan_purposes.add(purpose)
    hard_conflicted_payment = PaymentFactory(
        parent=payment_list,
        status=Payment.STATUS_PENDING,
        status_date=timezone.now() - timedelta(days=1),
    )
    PaymentFactory(
        parent=conflicting_plan,
        household=hard_conflicted_payment.household,
        status=Payment.STATUS_PENDING,
    )
    valid_payment = PaymentFactory(parent=payment_list, status=Payment.STATUS_PENDING)
    return {
        "payment_list": payment_list,
        "hard_conflicted_payment": hard_conflicted_payment,
        "valid_payment": valid_payment,
        "user": user,
    }


@pytest.fixture
def unlock_status_transition_context(
    user: User,
    business_area: BusinessArea,
    cycle: ProgramCycle,
) -> dict[str, Any]:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.LOCKED,
    )
    restorable_payment = PaymentFactory(
        parent=payment_list,
        status=Payment.STATUS_NOT_ELIGIBLE,
        conflicted=True,
    )
    excluded_payment = PaymentFactory(
        parent=payment_list,
        status=Payment.STATUS_NOT_ELIGIBLE,
        conflicted=True,
        excluded=True,
    )
    invalid_wallet_payment = PaymentFactory(
        parent=payment_list,
        status=Payment.STATUS_NOT_ELIGIBLE,
        conflicted=True,
        has_valid_wallet=False,
    )
    return {
        "payment_list": payment_list,
        "restorable_payment": restorable_payment,
        "excluded_payment": excluded_payment,
        "invalid_wallet_payment": invalid_wallet_payment,
        "user": user,
    }


@pytest.fixture
def invalid_wallet_payment_list(
    user: User,
    business_area: BusinessArea,
    program: Program,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    account_type_bank: AccountType,
) -> PaymentList:
    household = HouseholdFactory(business_area=business_area, program=program, size=1)
    delivery_mechanism = DeliveryMechanismFactory(
        code="bank_transfer_for_invalid_wallet_test",
        account_type=account_type_bank,
    )
    DeliveryMechanismConfig.objects.create(
        fsp=fsp,
        delivery_mechanism=delivery_mechanism,
        required_fields=["number"],
    )
    payment_list = PaymentListFactory(
        created_by=user,
        status=PaymentList.Status.DRAFT,
        business_area=business_area,
        program_cycle=cycle,
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
    )
    TargetingCriteriaRuleFactory(
        household_ids=household.unicef_id,
        payment_list=payment_list,
    )
    return payment_list


@pytest.fixture
def payment_list_base(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
) -> PaymentList:
    return PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.TP_LOCKED,
        delivery_mechanism=dm_transfer_to_account,
        financial_service_provider=fsp,
    )


@pytest.fixture
def payment_list_tp_open(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
) -> PaymentList:
    return PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.TP_OPEN,
        delivery_mechanism=dm_transfer_to_account,
        financial_service_provider=fsp,
    )


@pytest.fixture
def payment_list_in_status(user: User, business_area: Any, cycle: ProgramCycle, pp_status: str) -> PaymentList:
    return PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=pp_status,
    )


@pytest.fixture
def group_in_other_cycle(program: Program) -> Any:
    return PaymentPlanFactory(cycle=ProgramCycleFactory(program=program))


def test_delete_tp_open(payment_list_base: PaymentList) -> None:
    payment_list_base.status = PaymentList.Status.TP_OPEN
    payment_list_base.save()

    pp = PaymentListService(payment_list=payment_list_base).delete()

    assert pp.is_removed is True
    assert pp.status == PaymentList.Status.TP_OPEN


def test_delete_open(payment_list_base: PaymentList) -> None:
    payment_list_base.status = PaymentList.Status.OPEN
    payment_list_base.save()

    pp = PaymentListService(payment_list=payment_list_base).delete()

    assert pp.is_removed is False
    assert pp.status == PaymentList.Status.DRAFT


def test_delete_locked(payment_list_base: PaymentList) -> None:
    payment_list_base.status = PaymentList.Status.LOCKED
    payment_list_base.save()

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list=payment_list_base).delete()

    assert error.value.detail[0] == "Deletion is only allowed when the status is 'Open'"


def test_delete_when_its_one_pp_in_cycle(payment_list_base: PaymentList) -> None:
    payment_list_base.status = PaymentList.Status.OPEN
    payment_list_base.save()
    assert payment_list_base.program_cycle.status == ProgramCycle.ACTIVE

    pp = PaymentListService(payment_list=payment_list_base).delete()

    assert pp.is_removed is False
    assert pp.status == PaymentList.Status.DRAFT
    payment_list_base.program_cycle.refresh_from_db()
    assert payment_list_base.program_cycle.status == ProgramCycle.DRAFT


def test_delete_when_its_two_pp_in_cycle(user: User, business_area: Any) -> None:
    program = ProgramFactory(status=Program.ACTIVE, business_area=business_area, cycle=False)
    program_cycle = ProgramCycleFactory(status=ProgramCycle.ACTIVE, program=program)
    pp_1 = PaymentListFactory(
        status=PaymentList.Status.OPEN,
        program_cycle=program_cycle,
        created_by=user,
        business_area=business_area,
    )
    PaymentListFactory(
        status=PaymentList.Status.OPEN,
        program_cycle=program_cycle,
        created_by=user,
        business_area=business_area,
    )

    assert pp_1.program_cycle.status == ProgramCycle.ACTIVE

    pp_1 = PaymentListService(payment_list=pp_1).delete()

    assert pp_1.is_removed is False
    assert pp_1.status == PaymentList.Status.DRAFT
    program_cycle.refresh_from_db()
    assert program_cycle.status == ProgramCycle.ACTIVE


@freeze_time("2020-10-10")
def test_create_validation_errors(user: User, business_area: Any) -> None:
    program = ProgramFactory(
        status=Program.ACTIVE,
        business_area=business_area,
        start_date=timezone.datetime(2019, 10, 12, tzinfo=UTC).date(),
        end_date=timezone.datetime(2099, 12, 10, tzinfo=UTC).date(),
        cycle=False,
    )
    program_cycle = ProgramCycleFactory(
        program=program,
        start_date=timezone.datetime(2021, 10, 10, tzinfo=UTC).date(),
        end_date=timezone.datetime(2021, 12, 10, tzinfo=UTC).date(),
        status=ProgramCycle.ACTIVE,
    )
    household = HouseholdFactory(business_area=business_area, program=program)
    household.size = 1
    household.save(update_fields=["size"])
    create_input_data = {
        "program_cycle_id": str(program_cycle.id),
        "name": "TEST_123",
        "flag_exclude_if_active_adjudication_ticket": False,
        "flag_exclude_if_on_sanction_list": False,
        "rules": [
            {
                "household_filters_blocks": [],
                "household_ids": f"{household.unicef_id}",
                "individual_ids": "",
                "individuals_filters_blocks": [],
            }
        ],
    }

    PaymentListFactory(
        program_cycle=program_cycle,
        name="TEST_123",
        created_by=user,
        business_area=business_area,
    )
    with pytest.raises(ValidationError) as error:
        PaymentListService.create(
            input_data=create_input_data,
            user=user,
            program=program,
        )
    assert error.value.detail[0] == f"Target Population with name: TEST_123 and program: {program.name} already exists."

    program.status = Program.FINISHED
    program.save()
    program.refresh_from_db()
    with pytest.raises(ValidationError) as error:
        PaymentListService.create(
            input_data=create_input_data,
            user=user,
            program=program,
        )
    assert error.value.detail[0] == "Impossible to create Target Population for Programme within not Active status"

    program_cycle.status = ProgramCycle.FINISHED
    program_cycle.save()
    with pytest.raises(ValidationError) as error:
        PaymentListService.create(
            input_data=create_input_data,
            user=user,
            program=program,
        )
    assert error.value.detail[0] == "Impossible to create Target Population for Programme Cycle within Finished status"

    program_cycle.status = ProgramCycle.ACTIVE
    program_cycle.save()
    program.status = Program.ACTIVE
    program.save()

    purpose = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.add(purpose)
    currency_usd = CurrencyFactory(code="USD", name="United States Dollar")
    create_input_data["name"] = "TEST"
    create_input_data["payment_plan_id"] = PaymentPlanFactory(
        cycle=program_cycle,
        currency=currency_usd,
        dispersion_start_date=parse_date("2020-09-10"),
        dispersion_end_date=parse_date("2020-09-11"),
    ).id
    create_input_data["payment_plan_purposes"] = [purpose]
    pp = PaymentListService.create(
        input_data=create_input_data,
        user=user,
        program=program,
    )
    pp.status = PaymentList.Status.TP_OPEN
    pp.save()

    with pytest.raises(TransitionNotAllowed) as error:
        PaymentListService(payment_list=pp).open()
    assert str(error.value) == 'Status_Open :: no transition from "TP_OPEN"'

    pp.status = PaymentList.Status.DRAFT
    pp.save()
    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list=pp).open()
    assert error.value.detail[0] == "Dispersion End Date [2020-09-11] cannot be a past date"

    pp.refresh_from_db()
    assert pp.status == PaymentList.Status.DRAFT
    pp.payment_plan.dispersion_end_date = parse_date("2020-11-11")
    pp.payment_plan.save(update_fields=["dispersion_end_date"])

    pp = PaymentListService(payment_list=pp).open()
    pp.refresh_from_db()

    assert pp.status == PaymentList.Status.OPEN
    assert pp.currency == currency_usd


@freeze_time("2020-10-10")
@mock.patch("hope.models.payment_list.PaymentList.get_exchange_rate", return_value=2.0)
def test_create(
    get_exchange_rate_mock: Any,
    user: User,
    business_area: Any,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
    account_type_bank: AccountType,
    django_assert_num_queries: Any,
    django_capture_on_commit_callbacks: Any,
) -> None:
    program = ProgramFactory(
        status=Program.ACTIVE,
        business_area=business_area,
        start_date=timezone.datetime(2000, 9, 10, tzinfo=UTC).date(),
        end_date=timezone.datetime(2099, 10, 10, tzinfo=UTC).date(),
    )
    program_cycle = program.cycles.first()
    payment_plan = PaymentPlanFactory(cycle=program_cycle, financial_service_provider=fsp)

    hh1 = HouseholdFactory(program=program, business_area=business_area)
    hh2 = HouseholdFactory(program=program, business_area=business_area)
    hoh1 = hh1.head_of_household
    AccountFactory(
        individual=hoh1,
        account_type=account_type_bank,
    )
    AccountFactory(
        individual=hoh1,
        account_type=account_type_bank,
    )
    IndividualFactory.create_batch(
        4,
        household=hh1,
        business_area=business_area,
        program=program,
        registration_data_import=hh1.registration_data_import,
    )

    purpose = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.add(purpose)
    input_data = {
        "business_area_slug": "afghanistan",
        "name": "paymentListName",
        "program_cycle_id": program_cycle.id,
        "payment_plan_id": payment_plan.id,
        "flag_exclude_if_active_adjudication_ticket": False,
        "flag_exclude_if_on_sanction_list": False,
        "rules": [
            {
                "household_filters_blocks": [],
                "household_ids": f"{hh1.unicef_id}, {hh2.unicef_id}",
                "individual_ids": "",
                "individuals_filters_blocks": [],
            }
        ],
        "delivery_mechanism_code": dm_transfer_to_account.code,
        "payment_plan_purposes": [purpose],
    }

    with mock.patch("hope.apps.payment.services.payment_list_services.transaction") as mock_transaction:
        with django_assert_num_queries(24):
            pp = PaymentListService.create(
                input_data=input_data,
                user=user,
                program=program,
            )
        assert mock_transaction.on_commit.call_count == 1

    assert pp.status == PaymentList.Status.TP_OPEN
    assert pp.financial_service_provider == fsp
    assert pp.delivery_mechanism == dm_transfer_to_account
    assert pp.total_households_count == 0
    assert pp.total_individuals_count == 0
    assert pp.payment_items.count() == 0

    with django_capture_on_commit_callbacks(execute=True):
        prepare_payment_list_async_task(pp)

    pp.refresh_from_db()
    assert pp.status == PaymentList.Status.TP_OPEN
    assert pp.build_status == PaymentList.BuildStatus.BUILD_STATUS_OK
    assert pp.total_households_count == 2
    assert pp.total_individuals_count == 6
    assert pp.payment_items.count() == 2


@pytest.fixture
def draft_payment_list(payment_list_base: PaymentList) -> PaymentList:
    payment_plan = payment_list_base.payment_plan
    payment_plan.currency = CurrencyFactory(code="SDG", name="Sudanese pound")
    payment_plan.dispersion_start_date = parse_date("2026-10-05")
    payment_plan.dispersion_end_date = parse_date("2026-10-31")
    payment_plan.save(update_fields=["currency", "dispersion_start_date", "dispersion_end_date"])
    payment_list_base.status = PaymentList.Status.DRAFT
    payment_plan.exchange_rate = None
    payment_plan.save(update_fields=["exchange_rate"])
    payment_list_base.save(update_fields=["status"])
    return payment_list_base


@pytest.fixture
def unore_unavailable(request: pytest.FixtureRequest, settings: Any) -> Generator[requests_mock_lib.Mocker, None, None]:
    settings.USE_DUMMY_EXCHANGE_RATES = False
    settings.EXCHANGE_RATES_API_KEY = "TEST_API_KEY"
    settings.EXCHANGE_RATE_CACHE_EXPIRY = 60 * 60 * 24
    with requests_mock_lib.Mocker() as adapter:
        adapter.get(settings.EXCHANGE_RATES_API_URL, status_code=request.param)
        yield adapter


@freeze_time("2026-10-05")
@pytest.mark.parametrize(
    ("unore_unavailable", "expected_log_level"),
    [
        pytest.param(500, "WARNING", id="unore_server_error"),
        pytest.param(400, "ERROR", id="hope_bad_request"),
    ],
    indirect=["unore_unavailable"],
)
def test_open_arrange_unore_unavailable_and_cache_empty_act_open_assert_payment_list_opened_without_exchange_rate(
    draft_payment_list: PaymentList,
    unore_unavailable: requests_mock_lib.Mocker,
    expected_log_level: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING, logger="hope.apps.payment.services.payment_list_services"):
        PaymentListService(payment_list=draft_payment_list).open()

    draft_payment_list.refresh_from_db()
    assert unore_unavailable.called is True
    assert draft_payment_list.status == PaymentList.Status.OPEN
    assert draft_payment_list.exchange_rate is None
    assert caplog.records[-1].name == "hope.apps.payment.services.payment_list_services"
    assert caplog.records[-1].levelname == expected_log_level


def test_create_raises_when_payment_plan_belongs_to_different_cycle(user: User, business_area: Any) -> None:
    program = ProgramFactory(status=Program.ACTIVE, business_area=business_area)
    program_cycle = ProgramCycleFactory(program=program)
    other_cycle = ProgramCycleFactory(program=program)
    group_from_other_cycle = PaymentPlanFactory(cycle=other_cycle)

    input_data = {
        "business_area_slug": business_area.slug,
        "name": "Test TP",
        "program_cycle_id": program_cycle.id,
        "payment_plan_id": group_from_other_cycle.id,
        "flag_exclude_if_active_adjudication_ticket": False,
        "flag_exclude_if_on_sanction_list": False,
        "rules": [],
    }

    with pytest.raises(ValidationError) as error:
        PaymentListService.create(input_data=input_data, user=user, program=program)
    assert error.value.detail[0] == "Payment Plan does not exist in the given Programme Cycle."


def test_create_raises_when_payment_plan_does_not_exist(user: User, business_area: Any) -> None:
    program = ProgramFactory(status=Program.ACTIVE, business_area=business_area)
    program_cycle = ProgramCycleFactory(program=program)

    input_data = {
        "business_area_slug": business_area.slug,
        "name": "Test TP",
        "program_cycle_id": program_cycle.id,
        "payment_plan_id": uuid.uuid4(),
        "flag_exclude_if_active_adjudication_ticket": False,
        "flag_exclude_if_on_sanction_list": False,
        "rules": [],
    }

    with pytest.raises(ValidationError) as error:
        PaymentListService.create(input_data=input_data, user=user, program=program)
    assert error.value.detail[0] == "Payment Plan does not exist in the given Programme Cycle."


def test_create_raises_when_payment_plan_is_not_open(user: User, business_area: Any) -> None:
    program = ProgramFactory(status=Program.ACTIVE, business_area=business_area)
    program_cycle = ProgramCycleFactory(program=program)
    locked_payment_plan = PaymentPlanFactory(cycle=program_cycle, status=PaymentPlan.Status.LOCKED)

    input_data = {
        "business_area_slug": business_area.slug,
        "name": "Test TP",
        "program_cycle_id": program_cycle.id,
        "payment_plan_id": locked_payment_plan.id,
        "flag_exclude_if_active_adjudication_ticket": False,
        "flag_exclude_if_on_sanction_list": False,
        "rules": [],
    }

    with pytest.raises(ValidationError) as error:
        PaymentListService.create(input_data=input_data, user=user, program=program)
    assert error.value.detail[0] == "Adding Target Population to Payment Plan is possible only within Status OPEN"


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_list.PaymentList.get_exchange_rate", return_value=2.0)
def test_create_follow_up_pp(
    get_exchange_rate_mock: Any,
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    django_assert_num_queries: Any,
    django_capture_on_commit_callbacks: Any,
) -> None:
    pp = PaymentListFactory(
        total_households_count=1,
        created_by=user,
        business_area=business_area,
        program_cycle=cycle,
        name="Test Payment Plan",
    )
    follow_up_group = PaymentPlanFactory(
        cycle=cycle,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
        source_payment_plan=pp.payment_plan,
        currency=pp.currency,
        financial_service_provider=pp.financial_service_provider,
    )
    program = pp.program_cycle.program
    purpose = pp.payment_plan_purposes.first()
    payments = []
    for _ in range(5):
        hh = HouseholdFactory(program=program, business_area=business_area)
        IndividualFactory.create_batch(
            2,
            household=hh,
            business_area=business_area,
            program=program,
            registration_data_import=hh.registration_data_import,
        )
        payment = PaymentFactory(
            parent=pp,
            household=hh,
            status=Payment.STATUS_DISTRIBUTION_SUCCESS,
        )
        payments.append(payment)

    with pytest.raises(ValidationError) as error:
        PaymentListService(pp).create_follow_up(user, payment_plan=follow_up_group)
    assert error.value.detail[0] == "Cannot create a follow-up for a payment list with no unsuccessful payments"

    for payment, status in zip(payments[:4], Payment.FAILED_STATUSES, strict=True):
        payment.status = status
        payment.save()

    payments[4].household.withdrawn = True
    payments[4].household.save()

    p_error = payments[0]
    p_not_distributed = payments[1]
    p_force_failed = payments[2]
    p_manually_cancelled = payments[3]

    with django_assert_num_queries(11):
        follow_up_pp = PaymentListService(pp).create_follow_up(user, payment_plan=follow_up_group)

    follow_up_pp.refresh_from_db()
    assert follow_up_pp.status == PaymentList.Status.OPEN
    assert follow_up_pp.program == pp.program
    assert follow_up_pp.program_cycle == pp.program_cycle
    assert follow_up_pp.business_area == pp.business_area
    assert follow_up_pp.created_by == user
    assert follow_up_pp.currency == pp.currency
    assert follow_up_pp.dispersion_start_date == follow_up_group.dispersion_start_date
    assert follow_up_pp.dispersion_end_date == follow_up_group.dispersion_end_date
    assert follow_up_pp.program_cycle.start_date == pp.program_cycle.start_date
    assert follow_up_pp.program_cycle.end_date == pp.program_cycle.end_date
    assert follow_up_pp.total_households_count == 0
    assert follow_up_pp.total_individuals_count == 0
    assert follow_up_pp.payment_items.count() == 0
    assert follow_up_pp.payment_plan == follow_up_group
    assert list(follow_up_pp.payment_plan_purposes.values_list("pk", flat=True)) == [purpose.pk]

    assert pp.child_plans.count() == 1

    with django_capture_on_commit_callbacks(execute=True):
        prepare_child_payment_list_async_task(follow_up_pp)
    follow_up_pp.refresh_from_db()

    assert follow_up_pp.status == PaymentList.Status.OPEN
    assert follow_up_pp.build_status == PaymentList.BuildStatus.BUILD_STATUS_OK

    assert follow_up_pp.payment_items.count() == 4
    assert {
        p_error.id,
        p_not_distributed.id,
        p_force_failed.id,
        p_manually_cancelled.id,
    } == set(follow_up_pp.payment_items.values_list("source_payment_id", flat=True))

    follow_up_payment = follow_up_pp.payment_items.first()
    assert follow_up_payment.status == Payment.STATUS_PENDING
    assert follow_up_payment.parent == follow_up_pp
    assert follow_up_payment.source_payment is not None
    assert follow_up_payment.is_follow_up is True
    assert follow_up_payment.business_area == follow_up_payment.source_payment.business_area
    assert follow_up_payment.household == follow_up_payment.source_payment.household
    assert follow_up_payment.head_of_household == follow_up_payment.source_payment.head_of_household
    assert follow_up_payment.collector == follow_up_payment.source_payment.collector
    assert follow_up_payment.currency == follow_up_payment.source_payment.currency

    follow_up_payment.excluded = True
    follow_up_payment.save()

    with django_assert_num_queries(11):
        follow_up_pp_2 = PaymentListService(pp).create_follow_up(user, payment_plan=follow_up_group)

    assert pp.child_plans.count() == 2

    with django_assert_num_queries(60):
        with django_capture_on_commit_callbacks(execute=True):
            prepare_child_payment_list_async_task(follow_up_pp_2)

    assert follow_up_pp_2.payment_items.count() == 1
    assert {follow_up_payment.source_payment.id} == set(
        follow_up_pp_2.payment_items.values_list("source_payment_id", flat=True)
    )


def test_create_follow_up_pp_from_follow_up_validation(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.FINISHED,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
    )
    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).create_follow_up(user)

    assert error.value.detail[0] == "Cannot create a follow-up of a follow-up Payment List"


@pytest.mark.parametrize(
    ("plan_type", "method_name", "expected_kwargs"),
    [
        (PaymentList.PlanType.FOLLOW_UP, "create_follow_up", {}),
        (PaymentList.PlanType.TOP_UP, "create_top_up", {"fixed_amount": None, "amounts": None}),
        (
            PaymentList.PlanType.TOP_UP_AMENDMENT,
            "create_top_up_amendment",
            {"fixed_amount": None, "amounts": None},
        ),
    ],
)
def test_create_child_plan_arrange_supported_type_act_dispatch_assert_expected_service_method_called(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    plan_type: str,
    method_name: str,
    expected_kwargs: dict,
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
    )
    expected_child_plan = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        plan_type=plan_type,
    )
    linked_payment_plan = PaymentPlanFactory(
        cycle=cycle, plan_type=plan_type, source_payment_plan=payment_list.payment_plan
    )

    with mock.patch.object(PaymentListService, method_name, return_value=expected_child_plan) as service_method:
        result = PaymentListService(payment_list).create_child_plan(
            plan_type=plan_type,
            user=user,
            payment_plan=linked_payment_plan,
        )

    assert result == expected_child_plan
    service_method.assert_called_once_with(user, payment_plan=linked_payment_plan, **expected_kwargs)


def test_create_child_plan_arrange_unsupported_type_act_dispatch_assert_validation_error(
    user: User, business_area: Any, cycle: ProgramCycle
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
    )
    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).create_child_plan(
            plan_type=PaymentList.PlanType.REGULAR,
            user=user,
            payment_plan=payment_list.payment_plan,
        )

    assert str(error.value.detail[0]) == "Unsupported child payment list type: REGULAR"


@pytest.mark.parametrize(
    ("plan_type", "method_name", "expected_kwargs"),
    [
        (PaymentList.PlanType.FOLLOW_UP, "create_follow_up_payments", {}),
        (PaymentList.PlanType.TOP_UP, "create_funded_child_payments", {"amounts": None, "fixed_amount": None}),
        (
            PaymentList.PlanType.TOP_UP_AMENDMENT,
            "create_funded_child_payments",
            {"amounts": None, "fixed_amount": None},
        ),
    ],
)
def test_create_child_plan_payments_arrange_supported_type_act_dispatch_assert_expected_service_method_called(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    plan_type: str,
    method_name: str,
    expected_kwargs: dict,
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        plan_type=plan_type,
    )

    with mock.patch.object(PaymentListService, method_name) as service_method:
        PaymentListService(payment_list).create_child_plan_payments()

    service_method.assert_called_once_with(**expected_kwargs)


def test_create_child_plan_payments_arrange_unsupported_type_act_dispatch_assert_validation_error(
    user: User, business_area: Any, cycle: ProgramCycle
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        plan_type=PaymentList.PlanType.REGULAR,
    )

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).create_child_plan_payments()

    assert str(error.value.detail[0]) == "Unsupported child payment list type: REGULAR"


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_list.PaymentList.get_exchange_rate", return_value=2.0)
@patch("hope.models.payment_list_split.PaymentListSplit.MIN_NO_OF_PAYMENTS_IN_CHUNK")
def test_split(
    min_no_of_payments_in_chunk_mock: Any,
    get_exchange_rate_mock: Any,
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    django_assert_num_queries: Any,
) -> None:
    min_no_of_payments_in_chunk_mock.__get__ = mock.Mock(return_value=2)

    pp = PaymentListFactory(created_by=user, business_area=business_area, program_cycle=cycle)

    with pytest.raises(ValidationError, match="No payments to split"):
        PaymentListService(pp).split(PaymentListSplit.SplitType.BY_COLLECTOR)

    payments = []
    collector = IndividualFactory(household=None, business_area=business_area, program=cycle.program)
    for _ in range(3):
        hh = HouseholdFactory(business_area=business_area, program=cycle.program)
        IndividualFactory.create_batch(
            2,
            household=hh,
            business_area=business_area,
            program=cycle.program,
            registration_data_import=hh.registration_data_import,
        )
        payment = PaymentFactory(
            parent=pp,
            household=hh,
            status=Payment.STATUS_DISTRIBUTION_SUCCESS,
            collector=collector,
        )
        payments.append(payment)

    country = CountryFactory()
    admin_type_1 = AreaTypeFactory(country=country, area_level=1)
    admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
    area2 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_2)
    for _ in range(4):
        collector = IndividualFactory(household=None, business_area=business_area, program=cycle.program)
        hh = HouseholdFactory(admin2=area2, business_area=business_area, program=cycle.program)
        IndividualFactory.create_batch(
            2,
            household=hh,
            business_area=business_area,
            program=cycle.program,
            registration_data_import=hh.registration_data_import,
        )
        payment = PaymentFactory(
            parent=pp,
            household=hh,
            status=Payment.STATUS_DISTRIBUTION_SUCCESS,
            collector=collector,
        )
        payments.append(payment)

    for _ in range(5):
        collector = IndividualFactory(household=None, business_area=business_area, program=cycle.program)
        hh = HouseholdFactory(business_area=business_area, program=cycle.program)
        IndividualFactory.create_batch(
            2,
            household=hh,
            business_area=business_area,
            program=cycle.program,
            registration_data_import=hh.registration_data_import,
        )
        payment = PaymentFactory(
            parent=pp,
            household=hh,
            status=Payment.STATUS_DISTRIBUTION_SUCCESS,
            collector=collector,
        )
        payments.append(payment)

    with pytest.raises(ValidationError, match="Payments Number is required for split by records"):
        PaymentListService(pp).split(PaymentListSplit.SplitType.BY_RECORDS, chunks_no=None)

    with pytest.raises(ValidationError, match="Payment Parts number should be at least 2"):
        PaymentListService(pp).split(PaymentListSplit.SplitType.BY_RECORDS, chunks_no=1)

    with mock.patch("hope.apps.payment.services.payment_list_services.PaymentListSplit.MAX_CHUNKS") as max_chunks_patch:
        max_chunks_patch.__get__ = mock.Mock(return_value=2)
        with pytest.raises(ValidationError, match="Too many Payment Parts to split: 6, maximum is 2"):
            PaymentListService(pp).split(PaymentListSplit.SplitType.BY_RECORDS, chunks_no=2)

    with django_assert_num_queries(26):
        PaymentListService(pp).split(PaymentListSplit.SplitType.BY_COLLECTOR)
    unique_collectors_count = pp.eligible_payments.values_list("collector", flat=True).distinct().count()
    assert unique_collectors_count == 10
    pp_splits = pp.splits.all().order_by("order")

    assert pp_splits.count() == unique_collectors_count
    assert pp_splits[0].split_type == PaymentListSplit.SplitType.BY_COLLECTOR
    split_payment_counts = sorted([s.split_payment_items.count() for s in pp_splits], reverse=True)
    assert split_payment_counts == [3, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    with django_assert_num_queries(16):
        PaymentListService(pp).split(PaymentListSplit.SplitType.BY_RECORDS, chunks_no=5)
    pp_splits = pp.splits.all().order_by("order")
    assert pp_splits.count() == 3
    assert pp_splits[0].split_type == PaymentListSplit.SplitType.BY_RECORDS
    assert pp_splits[0].split_payment_items.count() == 5
    assert pp_splits[1].split_payment_items.count() == 5
    assert pp_splits[2].split_payment_items.count() == 2

    with django_assert_num_queries(14):
        PaymentListService(pp).split(PaymentListSplit.SplitType.BY_ADMIN_AREA2)
    unique_admin2_count = pp.eligible_payments.values_list("household__admin2", flat=True).distinct().count()
    assert unique_admin2_count == 2
    pp_splits = pp.splits.all().order_by("order")
    assert pp.splits.count() == unique_admin2_count
    assert pp_splits[0].split_type == PaymentListSplit.SplitType.BY_ADMIN_AREA2
    assert pp_splits[0].split_payment_items.count() == 4
    assert pp_splits[1].split_payment_items.count() == 8

    PaymentListService(pp).split(PaymentListSplit.SplitType.NO_SPLIT)
    pp_splits = pp.splits.all().order_by("order")
    assert pp.splits.count() == 1
    assert pp_splits[0].split_type == PaymentListSplit.SplitType.NO_SPLIT
    assert pp_splits[0].split_payment_items.count() == 12


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_list.PaymentList.get_exchange_rate", return_value=2.0)
def test_send_to_payment_gateway(
    get_exchange_rate_mock: Any,
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    dm_transfer_to_account: Any,
    django_capture_on_commit_callbacks: Any,
) -> None:
    pg_fsp = FinancialServiceProviderFactory(
        name="Western Union",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        payment_gateway_id="123",
    )
    pg_fsp.delivery_mechanisms.add(dm_transfer_to_account)
    pp = PaymentListFactory(
        status=PaymentList.Status.ACCEPTED,
        created_by=user,
        business_area=business_area,
        program_cycle=cycle,
        financial_service_provider=pg_fsp,
        delivery_mechanism=dm_transfer_to_account,
    )
    flow = PaymentListFlow(pp)
    flow.background_action_status_send_to_payment_gateway()
    pp.save()

    with pytest.raises(ValidationError, match="Sending in progress"):
        PaymentListService(pp).send_to_payment_gateway()

    flow.background_action_status_none()
    pp.save()

    split = PaymentListSplitFactory(payment_list=pp, sent_to_payment_gateway=True)

    with pytest.raises(ValidationError, match="Already sent to Payment Gateway"):
        PaymentListService(pp).send_to_payment_gateway()

    split.sent_to_payment_gateway = False
    split.save()
    with mock.patch("hope.apps.payment.services.payment_list_services.send_to_payment_gateway_async_task") as mock_task:
        pps = PaymentListService(pp)
        pps.user = mock.MagicMock(pk="123")
        with django_capture_on_commit_callbacks(execute=True):
            pps.send_to_payment_gateway()
        mock_task.assert_called_once_with(pp, str(pps.user.pk))

    pp.refresh_from_db(fields=["background_action_status"])
    assert pp.background_action_status == PaymentList.BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY


@freeze_time("2020-10-10")
def test_create_with_program_cycle_validation_error(user: User, business_area: Any) -> None:
    program = ProgramFactory(
        status=Program.ACTIVE,
        business_area=business_area,
        start_date=timezone.datetime(2000, 9, 10, tzinfo=UTC).date(),
        end_date=timezone.datetime(2099, 10, 10, tzinfo=UTC).date(),
        cycle=False,
    )
    cycle = ProgramCycleFactory(
        program=program,
        start_date=timezone.datetime(2021, 10, 10, tzinfo=UTC).date(),
        end_date=timezone.datetime(2021, 12, 10, tzinfo=UTC).date(),
        status=ProgramCycle.ACTIVE,
    )
    purpose = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.add(purpose)
    input_data = {
        "business_area_slug": "afghanistan",
        "currency": "USD",
        "name": "TestName123",
        "program_cycle_id": str(cycle.id),
        "flag_exclude_if_active_adjudication_ticket": False,
        "flag_exclude_if_on_sanction_list": False,
        "rules": [
            {
                "household_filters_blocks": [],
                "household_ids": "",
                "individual_ids": "",
                "individuals_filters_blocks": [
                    {
                        "individual_block_filters": [
                            {
                                "comparison_method": "RANGE",
                                "arguments": [1, 99],
                                "field_name": "age_at_registration",
                                "flex_field_classification": "NOT_FLEX_FIELD",
                            },
                        ],
                    }
                ],
            }
        ],
        "payment_plan_purposes": [purpose],
    }

    cycle.status = ProgramCycle.FINISHED
    cycle.save()
    with pytest.raises(ValidationError) as error:
        PaymentListService.create(
            input_data=input_data,
            user=user,
            program=program,
        )
    assert error.value.detail[0] == "Impossible to create Target Population for Programme Cycle within Finished status"

    cycle.status = ProgramCycle.DRAFT
    cycle.end_date = None
    cycle.save()
    input_data["payment_plan_id"] = PaymentPlanFactory(cycle=cycle).id
    PaymentListService.create(
        input_data=input_data,
        user=user,
        program=program,
    )
    cycle.refresh_from_db()
    assert cycle.status == ProgramCycle.DRAFT


@freeze_time("2022-12-12")
@mock.patch("hope.models.payment_list.PaymentList.get_exchange_rate", return_value=2.0)
def test_full_rebuild(
    get_exchange_rate_mock: Any,
    user: User,
    business_area: Any,
    django_assert_num_queries: Any,
    django_capture_on_commit_callbacks: Any,
) -> None:
    program = ProgramFactory(
        status=Program.ACTIVE,
        business_area=business_area,
        start_date=timezone.datetime(2000, 9, 10, tzinfo=UTC).date(),
        end_date=timezone.datetime(2099, 10, 10, tzinfo=UTC).date(),
    )
    program_cycle = program.cycles.first()
    payment_plan = PaymentPlanFactory(cycle=program_cycle)

    hh1 = HouseholdFactory(program=program, business_area=business_area)
    hh2 = HouseholdFactory(program=program, business_area=business_area)
    IndividualFactory.create_batch(
        4,
        household=hh1,
        business_area=business_area,
        program=program,
        registration_data_import=hh1.registration_data_import,
    )

    purpose = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.add(purpose)
    input_data = {
        "business_area_slug": "afghanistan",
        "name": "paymentListName",
        "program_cycle_id": program_cycle.id,
        "payment_plan_id": payment_plan.id,
        "flag_exclude_if_active_adjudication_ticket": False,
        "flag_exclude_if_on_sanction_list": False,
        "rules": [
            {
                "household_filters_blocks": [],
                "household_ids": f"{hh1.unicef_id}, {hh2.unicef_id}",
                "individual_ids": "",
                "individuals_filters_blocks": [],
            }
        ],
        "payment_plan_purposes": [purpose],
    }
    with mock.patch("hope.apps.payment.services.payment_list_services.transaction") as mock_transaction:
        with django_assert_num_queries(18):
            pp = PaymentListService.create(
                input_data=input_data,
                user=user,
                program=program,
            )
        assert mock_transaction.on_commit.call_count == 1

    assert pp.status == PaymentList.Status.TP_OPEN
    assert pp.total_households_count == 0
    assert pp.total_individuals_count == 0
    assert pp.payment_items.count() == 0

    with django_capture_on_commit_callbacks(execute=True):
        prepare_payment_list_async_task(pp)

    pp.refresh_from_db()
    assert pp.status == PaymentList.Status.TP_OPEN
    assert pp.build_status == PaymentList.BuildStatus.BUILD_STATUS_OK
    assert pp.payment_items.count() == 2

    old_payment_ids = list(pp.payment_items.values_list("id", flat=True))
    old_payment_unicef_ids = list(pp.payment_items.values_list("unicef_id", flat=True))

    pp_service = PaymentListService(payment_list=pp)
    pp_service.full_rebuild()

    pp.refresh_from_db()
    assert Payment.all_objects.filter(parent=pp).count() == 2

    new_payment_ids = list(pp.payment_items.values_list("id", flat=True))
    new_payment_unicef_ids = list(pp.payment_items.values_list("unicef_id", flat=True))

    for payment_id in new_payment_ids:
        assert payment_id not in old_payment_ids

    for payment_unicef_id in new_payment_unicef_ids:
        assert payment_unicef_id not in old_payment_unicef_ids


def test_get_approval_type_by_action_value_error(payment_list_base: PaymentList) -> None:
    with pytest.raises(ValueError, match="Action cannot be None"):
        PaymentListService(payment_list=payment_list_base).get_approval_type_by_action()


def test_validate_action_not_implemented(payment_list_base: PaymentList, user: User) -> None:
    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list_base).execute_update_status_action(
            input_data={"action": "INVALID_ACTION"}, user=user
        )
    actions = [
        "TP_LOCK",
        "TP_UNLOCK",
        "TP_REBUILD",
        "DRAFT",
        "LOCK",
        "LOCK_FSP",
        "UNLOCK",
        "UNLOCK_FSP",
        "SEND_FOR_APPROVAL",
        "APPROVE",
        "AUTHORIZE",
        "REVIEW",
        "REJECT",
        "SEND_TO_PAYMENT_GATEWAY",
    ]
    assert error.value.detail[0] == f"Not Implemented Action: INVALID_ACTION. List of possible actions: {actions}"


def test_tp_lock_invalid_pp_status(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.DRAFT,
        build_status=PaymentList.BuildStatus.BUILD_STATUS_OK,
    )
    with pytest.raises(TransitionNotAllowed) as error:
        PaymentListService(payment_list).tp_lock()
    assert str(error.value) == 'Status_Tp_Lock :: no transition from "DRAFT"'


def test_tp_lock_invalid_build_status(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.TP_OPEN,
        build_status=PaymentList.BuildStatus.BUILD_STATUS_BUILDING,
    )
    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).tp_lock()
    assert error.value.detail[0] == "Can only be locked when Build Status OK"


def test_tp_unlock(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.DRAFT,
    )
    with pytest.raises(TransitionNotAllowed) as error:
        PaymentListService(payment_list).tp_unlock()
    assert str(error.value) == 'Status_Tp_Open :: no transition from "DRAFT"'

    payment_list.status = PaymentList.Status.TP_LOCKED
    payment_list.save()
    PaymentListService(payment_list).tp_unlock()

    payment_list.refresh_from_db()
    assert payment_list.status == PaymentList.Status.TP_OPEN
    assert payment_list.build_status == PaymentList.BuildStatus.BUILD_STATUS_PENDING


def test_tp_rebuild(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.DRAFT,
        build_status=PaymentList.BuildStatus.BUILD_STATUS_FAILED,
    )
    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).tp_rebuild()
    assert error.value.detail[0] == "Can only Rebuild Population for Locked or Open Population status"

    payment_list.status = PaymentList.Status.TP_LOCKED
    payment_list.save()
    PaymentListService(payment_list).tp_rebuild()

    payment_list.refresh_from_db()
    assert payment_list.status == PaymentList.Status.TP_LOCKED
    assert payment_list.build_status == PaymentList.BuildStatus.BUILD_STATUS_PENDING


def test_draft_with_invalid_pp_status(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.TP_LOCKED,
    )
    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).draft()
    assert "Can only promote to Payment List if the Payment Plan has a Financial Service Provider." in str(error.value)

    payment_list.status = PaymentList.Status.DRAFT
    payment_list.save()
    payment_list.payment_plan.financial_service_provider = fsp
    payment_list.payment_plan.save(update_fields=["financial_service_provider"])

    with pytest.raises(TransitionNotAllowed) as error:
        PaymentListService(payment_list).draft()
    assert str(error.value) == 'Status_Draft :: no transition from "DRAFT"'


def test_lock_if_no_valid_payments(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.OPEN,
    )
    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).lock()
    assert error.value.detail[0] == "At least one valid Payment should exist in order to Lock the Payment List"


def test_lock_marks_pending_hard_conflict_not_eligible(
    lock_status_transition_context: dict[str, Any],
) -> None:
    hard_conflicted_payment = lock_status_transition_context["hard_conflicted_payment"]
    previous_status_date = hard_conflicted_payment.status_date

    PaymentListService(lock_status_transition_context["payment_list"]).execute_update_status_action(
        {"action": PaymentList.Action.LOCK.value},
        lock_status_transition_context["user"],
    )

    hard_conflicted_payment.refresh_from_db()
    lock_status_transition_context["valid_payment"].refresh_from_db()
    assert hard_conflicted_payment.conflicted is True
    assert hard_conflicted_payment.status == Payment.STATUS_NOT_ELIGIBLE
    assert hard_conflicted_payment.status_date > previous_status_date
    payment_log = LogEntry.objects.get(object_id=hard_conflicted_payment.pk)
    assert payment_log.changes["status_date"] == {
        "from": str(previous_status_date),
        "to": str(hard_conflicted_payment.status_date),
    }
    assert lock_status_transition_context["valid_payment"].status == Payment.STATUS_PENDING


def test_unlock_only_restores_not_eligible_payment_without_remaining_cause(
    unlock_status_transition_context: dict[str, Any],
) -> None:
    previous_status_date = unlock_status_transition_context["restorable_payment"].status_date

    PaymentListService(unlock_status_transition_context["payment_list"]).execute_update_status_action(
        {"action": PaymentList.Action.UNLOCK.value},
        unlock_status_transition_context["user"],
    )

    restorable_payment = unlock_status_transition_context["restorable_payment"]
    excluded_payment = unlock_status_transition_context["excluded_payment"]
    invalid_wallet_payment = unlock_status_transition_context["invalid_wallet_payment"]
    restorable_payment.refresh_from_db()
    excluded_payment.refresh_from_db()
    invalid_wallet_payment.refresh_from_db()
    assert restorable_payment.conflicted is False
    assert restorable_payment.status == Payment.STATUS_PENDING
    payment_log = LogEntry.objects.get(object_id=restorable_payment.pk)
    assert payment_log.changes["status_date"] == {
        "from": str(previous_status_date),
        "to": str(restorable_payment.status_date),
    }
    assert excluded_payment.conflicted is False
    assert excluded_payment.status == Payment.STATUS_NOT_ELIGIBLE
    assert invalid_wallet_payment.conflicted is False
    assert invalid_wallet_payment.status == Payment.STATUS_NOT_ELIGIBLE


def test_update_pp_validation_errors(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.LOCKED,
    )
    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).update({"exclusion_reason": "ABC"})
    assert error.value.detail[0] == f"Not Allow edit targeting criteria within status {payment_list.status}"

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).update({"vulnerability_score_min": "test_data"})
    assert (
        error.value.detail[0]
        == "You can only set vulnerability_score_min and vulnerability_score_max on Locked Population status"
    )

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).update({"name": "test_data"})
    assert error.value.detail[0] == "Name can be changed only within Open status"

    payment_list.status = PaymentList.Status.TP_OPEN
    payment_list.save()
    PaymentListFactory(
        name="test_data",
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.DRAFT,
    )
    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).update({"name": "test_data"})
    assert error.value.detail[0] == f"Name 'test_data' and program '{cycle.program.name}' already exists."

    finished_cycle = ProgramCycleFactory(program=cycle.program, status=ProgramCycle.FINISHED)
    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).update({"program_cycle_id": str(finished_cycle.id)})
    assert error.value.detail[0] == "Not possible to assign Finished Program Cycle"


def test_rebuild_payment_list_population(
    user: User, business_area: Any, cycle: ProgramCycle, django_capture_on_commit_callbacks: Any
) -> None:
    pp = PaymentListFactory(
        name="test_data",
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.TP_OPEN,
    )

    with django_capture_on_commit_callbacks(execute=True):
        PaymentListService.rebuild_payment_list_population(
            rebuild_list=False,
            should_update_money_stats=True,
            vulnerability_filter=False,
            payment_list=pp,
        )
        PaymentListService.rebuild_payment_list_population(
            rebuild_list=True,
            should_update_money_stats=False,
            vulnerability_filter=False,
            payment_list=pp,
        )
        PaymentListService.rebuild_payment_list_population(
            rebuild_list=False,
            should_update_money_stats=False,
            vulnerability_filter=True,
            payment_list=pp,
        )

    pp.refresh_from_db(fields=("build_status",))
    assert pp.build_status == PaymentList.BuildStatus.BUILD_STATUS_OK


@patch("hope.apps.payment.services.payment_list_services.payment_list_rebuild_stats_async_task")
@patch("hope.apps.payment.services.payment_list_services.payment_list_full_rebuild_async_task")
def test_rebuild_payment_list_population_full_rebuild_with_money_stats_queues_both_tasks(
    mock_full_rebuild: mock.Mock,
    mock_rebuild_stats: mock.Mock,
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
) -> None:
    pp = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.TP_OPEN,
    )

    PaymentListService.rebuild_payment_list_population(
        rebuild_list=True,
        should_update_money_stats=True,
        vulnerability_filter=False,
        payment_list=pp,
    )

    mock_full_rebuild.assert_called_once_with(pp)
    mock_rebuild_stats.assert_called_once_with(pp)


@patch("hope.apps.payment.celery_tasks.payment_list_apply_steficon_hh_selection_async_task")
@patch("hope.apps.payment.services.payment_list_services.payment_list_full_rebuild_async_task")
def test_rebuild_payment_list_population_full_rebuild_with_steficon_targeting_queues_steficon(
    mock_full_rebuild: mock.Mock,
    mock_apply_steficon: mock.Mock,
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
) -> None:
    pp = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.TP_OPEN,
        steficon_rule_targeting=RuleCommitFactory(),
    )

    PaymentListService.rebuild_payment_list_population(
        rebuild_list=True,
        should_update_money_stats=False,
        vulnerability_filter=True,
        payment_list=pp,
    )

    mock_full_rebuild.assert_called_once_with(pp)
    mock_apply_steficon.assert_called_once_with(pp, str(pp.steficon_rule_targeting.rule_id), None)


def test_lock_fsp_validation(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.LOCKED,
    )
    payment = PaymentFactory(
        parent=payment_list,
        program=cycle.program,
        business_area_id=payment_list.business_area_id,
        status=Payment.STATUS_PENDING,
        financial_service_provider=None,
        entitlement_quantity=None,
        entitlement_quantity_usd=None,
        delivered_quantity=None,
        delivered_quantity_usd=None,
    )

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).lock_fsp()
    assert error.value.detail[0] == "Payment List doesn't have FSP / DeliveryMechanism assigned."

    payment_list.payment_plan.financial_service_provider = fsp
    payment_list.payment_plan.save(update_fields=["financial_service_provider"])
    payment_list.delivery_mechanism = dm_transfer_to_account
    payment.save()

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).lock_fsp()
    assert error.value.detail[0] == "All Payments must have entitlement quantity set."

    payment.entitlement_quantity = 100
    payment.save()

    PaymentListService(payment_list).lock_fsp()
    payment.refresh_from_db()
    assert payment.financial_service_provider == fsp


def test_lock_fsp_rejects_running_rule_engine(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.LOCKED,
        financial_service_provider=fsp,
        delivery_mechanism=dm_transfer_to_account,
        background_action_status=PaymentList.BackgroundActionStatus.RULE_ENGINE_RUN,
    )

    with pytest.raises(ValidationError, match="Another background action is already in progress."):
        PaymentListService(payment_list).lock_fsp()
    payment_list.refresh_from_db(fields=("status",))
    assert payment_list.status == PaymentList.Status.LOCKED


def test_unlock_fsp(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.LOCKED_FSP,
    )

    PaymentListService(payment_list).unlock_fsp()

    payment_list.refresh_from_db(fields=("status",))
    assert payment_list.status == PaymentList.Status.LOCKED


@pytest.fixture
def payment_list_importing_fsp_extra_fields(user: User, business_area: Any, cycle: ProgramCycle) -> PaymentList:
    return PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.LOCKED_FSP,
        background_action_status=PaymentList.BackgroundActionStatus.XLSX_IMPORTING_FSP_EXTRA_FIELDS,
    )


@pytest.fixture
def payment_list_with_fsp_extra_fields_import_error(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
) -> PaymentList:
    return PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.LOCKED_FSP,
        background_action_status=PaymentList.BackgroundActionStatus.XLSX_IMPORT_ERROR,
    )


def test_unlock_fsp_rejects_active_fsp_extra_fields_import(
    payment_list_importing_fsp_extra_fields: PaymentList,
) -> None:
    with pytest.raises(ValidationError, match="Another background action is already in progress."):
        PaymentListService(payment_list_importing_fsp_extra_fields).unlock_fsp()


def test_send_for_approval_rejects_active_fsp_extra_fields_import(
    payment_list_importing_fsp_extra_fields: PaymentList,
) -> None:
    with pytest.raises(ValidationError, match="Another background action is already in progress."):
        PaymentListService(payment_list_importing_fsp_extra_fields).send_for_approval()


def test_unlock_fsp_allows_retryable_background_error(
    payment_list_with_fsp_extra_fields_import_error: PaymentList,
) -> None:
    PaymentListService(payment_list_with_fsp_extra_fields_import_error).unlock_fsp()

    assert payment_list_with_fsp_extra_fields_import_error.status == PaymentList.Status.LOCKED
    assert payment_list_with_fsp_extra_fields_import_error.background_action_status is None


def test_send_for_approval_allows_retryable_background_error(
    payment_list_with_fsp_extra_fields_import_error: PaymentList,
    user: User,
    mocker: Any,
) -> None:
    notification_task = mocker.patch(
        "hope.apps.payment.services.payment_list_services.send_payment_notification_emails_async_task"
    )

    PaymentListService(payment_list_with_fsp_extra_fields_import_error).execute_update_status_action(
        {"action": PaymentList.Action.SEND_FOR_APPROVAL},
        user,
    )

    assert payment_list_with_fsp_extra_fields_import_error.status == PaymentList.Status.IN_APPROVAL
    assert payment_list_with_fsp_extra_fields_import_error.background_action_status is None
    notification_task.assert_called_once()


def test_update_pp_program_cycle(payment_list_tp_open: PaymentList, program: Program) -> None:
    new_cycle = ProgramCycleFactory(program=program, title="New Cycle ABC")
    new_group = PaymentPlanFactory(
        cycle=new_cycle, financial_service_provider=payment_list_tp_open.financial_service_provider
    )

    PaymentListService(payment_list_tp_open).update({"program_cycle_id": new_cycle.id, "payment_plan_id": new_group.id})

    payment_list_tp_open.refresh_from_db()
    assert payment_list_tp_open.program_cycle.title == "New Cycle ABC"
    assert payment_list_tp_open.payment_plan == new_group


def test_edit_cycle_requires_group_from_new_cycle(payment_list_tp_open: PaymentList, program: Program) -> None:
    new_cycle = ProgramCycleFactory(program=program)
    new_group = PaymentPlanFactory(
        cycle=new_cycle, financial_service_provider=payment_list_tp_open.financial_service_provider
    )

    PaymentListService(payment_list_tp_open).update({"program_cycle_id": new_cycle.id, "payment_plan_id": new_group.id})

    payment_list_tp_open.refresh_from_db()
    assert payment_list_tp_open.program_cycle == new_cycle
    assert payment_list_tp_open.payment_plan == new_group


def test_edit_cycle_rejects_group_from_old_cycle(payment_list_tp_open: PaymentList, program: Program) -> None:
    old_payment_plan = payment_list_tp_open.payment_plan
    new_cycle = ProgramCycleFactory(program=program)

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list_tp_open).update(
            {"program_cycle_id": new_cycle.id, "payment_plan_id": old_payment_plan.id}
        )
    assert error.value.detail[0] == "Payment Plan does not exist in the given Programme Cycle."


def test_edit_cycle_rejects_missing_group(payment_list_tp_open: PaymentList, program: Program) -> None:
    new_cycle = ProgramCycleFactory(program=program)

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list_tp_open).update({"program_cycle_id": new_cycle.id})
    assert error.value.detail[0] == "Payment Plan is required when changing Programme Cycle."


def test_edit_cycle_rejects_group_not_open(payment_list_tp_open: PaymentList, program: Program) -> None:
    new_cycle = ProgramCycleFactory(program=program)
    locked_payment_plan = PaymentPlanFactory(cycle=new_cycle, status=PaymentPlan.Status.ACCEPTED)

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list_tp_open).update(
            {"program_cycle_id": new_cycle.id, "payment_plan_id": locked_payment_plan.id}
        )
    assert error.value.detail[0] == "Adding Target Population to Payment Plan is possible only within Status OPEN"


@pytest.mark.parametrize(
    "pp_status",
    [
        pytest.param(PaymentList.Status.TP_LOCKED, id="tp-locked"),
        pytest.param(PaymentList.Status.OPEN, id="open"),
        pytest.param(PaymentList.Status.ACCEPTED, id="accepted"),
    ],
)
def test_edit_cycle_outside_tp_open_raises_and_keeps_cycle(
    pp_status: str,
    payment_list_in_status: PaymentList,
    group_in_other_cycle: Any,
    cycle: ProgramCycle,
) -> None:
    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list_in_status).update(
            {"program_cycle_id": group_in_other_cycle.cycle_id, "payment_plan_id": group_in_other_cycle.id}
        )

    assert error.value.detail[0] == "Programme Cycle can be changed only within Open status"
    payment_list_in_status.refresh_from_db()
    assert payment_list_in_status.program_cycle == cycle


def test_update_pp_vulnerability_score(payment_list_base: PaymentList) -> None:
    PaymentListService(payment_list_base).update(
        {
            "vulnerability_score_min": "11.229222",
            "vulnerability_score_max": "77.889777",
        }
    )
    payment_list_base.refresh_from_db(fields=("vulnerability_score_min", "vulnerability_score_max"))
    assert payment_list_base.vulnerability_score_min == Decimal("11.229")
    assert payment_list_base.vulnerability_score_max == Decimal("77.890")


def test_update_pp_exclude_ids(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.TP_OPEN,
    )
    PaymentListService(payment_list).update({"excluded_ids": "IND-123", "exclusion_reason": "Test text"})
    payment_list.refresh_from_db(fields=("excluded_ids", "exclusion_reason"))
    assert payment_list.excluded_ids == "IND-123"
    assert payment_list.exclusion_reason == "Test text"


def test_open_rejects_group_without_currency(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        payment_plan=PaymentPlanFactory(cycle=cycle, financial_service_provider=fsp),
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.DRAFT,
        currency=None,
        delivery_mechanism=dm_transfer_to_account,
        financial_service_provider=fsp,
    )
    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).open()
    assert error.value.detail[0] == "Payment Plan needs a Currency before a Payment List can be opened."


def test_open_rejects_group_without_dispersion_dates(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        payment_plan=PaymentPlanFactory(
            cycle=cycle, financial_service_provider=fsp, currency=CurrencyFactory(code="PLN", name="Polish Zloty")
        ),
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.DRAFT,
        delivery_mechanism=dm_transfer_to_account,
    )
    PaymentPlan.objects.filter(pk=payment_list.payment_plan_id).update(
        dispersion_start_date=None, dispersion_end_date=None
    )
    payment_list.payment_plan.refresh_from_db()

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).open()

    assert error.value.detail[0] == "Payment Plan needs Dispersion Dates before a Payment List can be opened."
    payment_list.refresh_from_db()
    assert payment_list.status == PaymentList.Status.DRAFT


def test_update_pp_delivery_mechanism(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        payment_plan=PaymentPlanFactory(cycle=cycle, financial_service_provider=fsp),
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.TP_OPEN,
        delivery_mechanism=None,
        financial_service_provider=fsp,
    )

    PaymentListService(payment_list).update({"delivery_mechanism_code": dm_transfer_to_account.code})

    payment_list.refresh_from_db()
    assert payment_list.delivery_mechanism == dm_transfer_to_account
    assert payment_list.financial_service_provider == fsp


def test_update_pp_delivery_mechanism_ignored_when_not_open(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
    dm_transfer_to_digital_wallet: Any,
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        payment_plan=PaymentPlanFactory(cycle=cycle, financial_service_provider=fsp),
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.OPEN,
        currency=CurrencyFactory(code="AMD", name="Armenian Dram"),
        delivery_mechanism=dm_transfer_to_account,
        financial_service_provider=fsp,
    )

    PaymentListService(payment_list).update({"delivery_mechanism_code": dm_transfer_to_digital_wallet.code})

    payment_list.refresh_from_db()
    assert payment_list.delivery_mechanism == dm_transfer_to_account


def test_update_pp_delivery_mechanism_cleared_when_code_missing(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        payment_plan=PaymentPlanFactory(cycle=cycle, financial_service_provider=fsp),
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.TP_OPEN,
        delivery_mechanism=dm_transfer_to_account,
        financial_service_provider=fsp,
    )

    PaymentListService(payment_list).update({"delivery_mechanism_code": None})

    payment_list.refresh_from_db()
    assert payment_list.delivery_mechanism is None
    assert payment_list.financial_service_provider == fsp


def test_update_pp_delivery_mechanism_rejects_digital_wallet_without_usdc(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_digital_wallet: Any,
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        payment_plan=PaymentPlanFactory(
            cycle=cycle,
            financial_service_provider=fsp,
            currency=CurrencyFactory(code="PLN", name="Polish Zloty"),
        ),
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.TP_OPEN,
        delivery_mechanism=None,
        financial_service_provider=fsp,
    )

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).update({"delivery_mechanism_code": dm_transfer_to_digital_wallet.code})
    assert (
        error.value.detail[0] == "For delivery mechanism Transfer to Digital Wallet only currency USDC can be assigned."
    )


def test_change_group_copies_group_fsp(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        payment_plan=PaymentPlanFactory(cycle=cycle),
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.TP_OPEN,
        financial_service_provider=None,
    )
    new_group = PaymentPlanFactory(cycle=cycle, financial_service_provider=fsp)

    PaymentListService(payment_list).update({"payment_plan_id": str(new_group.id)})

    payment_list.refresh_from_db()
    assert payment_list.payment_plan == new_group
    assert payment_list.financial_service_provider == fsp


@patch("hope.apps.payment.services.payment_list_services.payment_list_full_rebuild_async_task")
def test_change_group_to_different_fsp_rebuilds_target_population(
    mock_full_rebuild: mock.Mock,
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    django_capture_on_commit_callbacks: Any,
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        payment_plan=PaymentPlanFactory(cycle=cycle),
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.TP_OPEN,
        financial_service_provider=None,
    )
    new_group = PaymentPlanFactory(cycle=cycle, financial_service_provider=fsp)

    with django_capture_on_commit_callbacks(execute=True):
        PaymentListService(payment_list).update({"payment_plan_id": str(new_group.id)})

    mock_full_rebuild.assert_called_once_with(payment_list)


def test_change_group_rejects_group_currency_not_matching_delivery_mechanism(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_digital_wallet: Any,
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        payment_plan=PaymentPlanFactory(cycle=cycle, financial_service_provider=fsp),
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.TP_OPEN,
        delivery_mechanism=dm_transfer_to_digital_wallet,
        financial_service_provider=fsp,
    )
    new_group = PaymentPlanFactory(
        cycle=cycle,
        financial_service_provider=fsp,
        currency=CurrencyFactory(code="PLN", name="Polish Zloty"),
    )

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).update({"payment_plan_id": str(new_group.id)})
    assert (
        error.value.detail[0] == "For delivery mechanism Transfer to Digital Wallet only currency USDC can be assigned."
    )


def test_export_xlsx(payment_list_base: PaymentList, user: User, django_capture_on_commit_callbacks: Any) -> None:
    payment_list_base.status = PaymentList.Status.LOCKED
    payment_list_base.save()
    assert FileTemp.objects.all().count() == 0

    with django_capture_on_commit_callbacks(execute=True):
        PaymentListService(payment_list_base).export_xlsx(str(user.pk))

    assert FileTemp.objects.all().count() == 1
    assert FileTemp.objects.first().object_id == str(payment_list_base.pk)


def test_create_payments_integrity_error_handling(
    user: User,
    business_area: Any,
    program: Program,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
) -> None:
    household = HouseholdFactory(business_area=business_area, program=program)
    household.size = 1
    household.save(update_fields=["size"])
    payment_list = PaymentListFactory(
        created_by=user,
        status=PaymentList.Status.DRAFT,
        business_area=business_area,
        program_cycle=cycle,
        delivery_mechanism=dm_transfer_to_account,
        financial_service_provider=fsp,
    )
    TargetingCriteriaRuleFactory(
        household_ids=f"{household.unicef_id}", payment_list=payment_list, alternative_collectors_ids="HH-1"
    )

    PaymentFactory(
        parent=payment_list,
        program=program,
        business_area_id=payment_list.business_area_id,
        status=Payment.STATUS_PENDING,
        household=household,
        collector=household.head_of_household,
    )

    hh_qs = program.households_with_payments_in_program
    assert hh_qs.count() == 1
    assert hh_qs.first().unicef_id == household.unicef_id

    with transaction.atomic():
        with pytest.raises(ValidationError, match="Duplicated Households in provided Targeting List") as error:
            PaymentListService.create_payments(payment_list)
        assert isinstance(error.value.__cause__, IntegrityError)
        assert 'duplicate key value violates unique constraint "payment_plan_and_household"' in str(
            error.value.__cause__
        )

    with transaction.atomic():
        IndividualRoleInHousehold.objects.filter(household=household, role=ROLE_PRIMARY).delete()

        with pytest.raises(ValidationError) as error:
            PaymentListService.create_payments(payment_list)
        assert f"Couldn't find a PRIMARY collector in {household.unicef_id}" in str(error.value)


def test_create_payments_marks_invalid_wallet_not_eligible(
    invalid_wallet_payment_list: PaymentList,
) -> None:
    PaymentListService.create_payments(invalid_wallet_payment_list)

    payment = invalid_wallet_payment_list.payment_items.get()
    assert payment.has_valid_wallet is False
    assert payment.status == Payment.STATUS_NOT_ELIGIBLE


def test_create_payments_sets_plan_currency(invalid_wallet_payment_list: PaymentList) -> None:
    group = invalid_wallet_payment_list.payment_plan
    group.currency = CurrencyFactory(code="AFN", name="Afghan afghani")
    group.save(update_fields=["currency"])

    PaymentListService.create_payments(invalid_wallet_payment_list)

    payment = invalid_wallet_payment_list.payment_items.get()
    assert payment.currency.code == "AFN"


def test_acceptance_process_validation_error(payment_list_base: PaymentList) -> None:
    payment_list_base.status = PaymentList.Status.OPEN
    payment_list_base.save()

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list=payment_list_base).acceptance_process()

    assert f"Approval Process object not found for PaymentList {payment_list_base.id}" in str(error.value)


def test_update_rules_tp_open(payment_list_base: PaymentList) -> None:
    payment_list_base.status = PaymentList.Status.TP_OPEN
    payment_list_base.save()
    input_data = {
        "rules": [
            {
                "individual_ids": "",
                "household_ids": "",
                "households_filters_blocks": [],
                "individuals_filters_blocks": [
                    {
                        "individual_block_filters": [
                            {
                                "comparison_method": "RANGE",
                                "arguments": [10, 20],
                                "field_name": "age",
                                "flex_field_classification": "NOT_FLEX_FIELD",
                            }
                        ]
                    }
                ],
            }
        ],
        "flag_exclude_if_on_sanction_list": True,
        "flag_exclude_if_active_adjudication_ticket": False,
    }
    PaymentListService(payment_list_base).update(input_data)
    payment_list_base.refresh_from_db()
    assert payment_list_base.rules.count() == 1
    assert payment_list_base.flag_exclude_if_on_sanction_list
    assert not payment_list_base.flag_exclude_if_active_adjudication_ticket


def test_send_reconciliation_overdue_emails() -> None:
    pp = PaymentListFactory(
        dispersion_start_date=now() - timedelta(days=10),
        dispersion_end_date=now(),
        status=PaymentList.Status.ACCEPTED,
    )
    pp.refresh_from_db()
    program = pp.program
    program.reconciliation_window_in_days = 10
    program.send_reconciliation_window_expiry_notifications = True
    program.save()

    PaymentFactory(parent=pp, status=Payment.STATUS_PENDING, delivered_quantity=None)
    assert pp.has_payments_reconciliation_overdue is True

    with mock.patch(
        "hope.apps.payment.services.payment_list_services.send_payment_list_reconciliation_overdue_email_async_task"
    ) as mock_task:
        PaymentListService.send_reconciliation_overdue_emails()
        mock_task.assert_called_once_with(pp)


def test_send_reconciliation_overdue_emails_skips_payment_lists_without_overdue_reconciliation() -> None:
    pp = PaymentListFactory(
        dispersion_start_date=now() - timedelta(days=10),
        dispersion_end_date=now(),
        status=PaymentList.Status.ACCEPTED,
    )
    pp.refresh_from_db()
    program = pp.program
    program.reconciliation_window_in_days = 10
    program.send_reconciliation_window_expiry_notifications = True
    program.save()

    PaymentFactory(parent=pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS, delivered_quantity=1)
    assert pp.has_payments_reconciliation_overdue is False

    with mock.patch(
        "hope.apps.payment.services.payment_list_services.send_payment_list_reconciliation_overdue_email_async_task"
    ) as mock_task:
        PaymentListService.send_reconciliation_overdue_emails()
        mock_task.assert_not_called()


def test_send_reconciliation_overdue_emails_reads_instruction_dispersion_start_date() -> None:
    program = ProgramFactory(reconciliation_window_in_days=10, send_reconciliation_window_expiry_notifications=True)
    pp = PaymentListFactory(
        program_cycle=program.cycles.first(),
        follow_up_instruction=FollowUpInstructionFactory(
            program=program, dispersion_start_date=now().date() - timedelta(days=10)
        ),
        plan_type=PaymentList.PlanType.FOLLOW_UP,
        status=PaymentList.Status.ACCEPTED,
    )
    PaymentFactory(parent=pp, status=Payment.STATUS_PENDING, delivered_quantity=None)

    with mock.patch(
        "hope.apps.payment.services.payment_list_services.send_payment_list_reconciliation_overdue_email_async_task"
    ) as mock_task:
        PaymentListService.send_reconciliation_overdue_emails()

    mock_task.assert_called_once_with(pp)


def test_send_reconciliation_overdue_email(business_area: Any) -> None:
    partner_unicef = PartnerFactory(name="UNICEF")
    partner_unicef_hq = PartnerFactory(name="UNICEF HQ", parent=partner_unicef)
    user = UserFactory(partner=partner_unicef_hq)
    role, _ = Role.objects.update_or_create(
        name="RECEIVE_PP_OVERDUE_EMAIL", defaults={"permissions": [Permissions.RECEIVE_PP_OVERDUE_EMAIL.value]}
    )
    RoleAssignment.objects.create(
        user=user,
        role=role,
        business_area=business_area,
    )

    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program)
    pp = PaymentListFactory(
        dispersion_start_date=now() - timedelta(days=10),
        dispersion_end_date=now(),
        status=PaymentList.Status.ACCEPTED,
        program_cycle=cycle,
    )
    pp.refresh_from_db()
    program = pp.program
    program.reconciliation_window_in_days = 10
    program.send_reconciliation_window_expiry_notifications = True
    program.save()

    with mock.patch.object(User, "email_user") as mock_email_user:
        with mock.patch("hope.apps.payment.services.payment_list_services.render_to_string") as mock_render_to_string:
            PaymentListService(pp).send_reconciliation_overdue_email_for_pp()
            mock_email_user.assert_called_once()
            assert mock_render_to_string.call_count == 2
            _args, kwargs = mock_render_to_string.call_args
            context = kwargs["context"]
            assert context["message"] == (
                f"Please be informed that Payment List: {pp.unicef_id} has exceeded its"
                f" reconciliation window of {pp.program.reconciliation_window_in_days} days."
                " Please take the necessary steps to complete the reconciliation process timely."
            )
            assert context["title"] == f"Payment List {pp.unicef_id} Reconciliation Overdue"


def test_get_collector() -> None:
    household_dict = {
        "unicef_id": "ID_1",
        "use_alt_collector": True,
        # no Alt Collector
    }
    with pytest.raises(ValidationError) as error:
        PaymentListService._get_collector(household_dict)
    assert error.value.detail[0] == "Couldn't find a ALTERNATE collector in ID_1"

    household_dict = {
        "unicef_id": "ID_2",
        "use_alt_collector": False,
        # no Pr Collector
    }
    with pytest.raises(ValidationError) as error:
        PaymentListService._get_collector(household_dict)
    assert error.value.detail[0] == "Couldn't find a PRIMARY collector in ID_2"

    collector = IndividualFactory()
    household_dict = {
        "unicef_id": "ID_2",
        "use_alt_collector": False,
        "pr_collector": collector.id,
    }
    collcector_result, collcector_type = PaymentListService._get_collector(household_dict)
    assert collcector_result == collector
    assert collcector_type == "PRIMARY"


def test_send_reconciliation_overdue_email_recipients(business_area: Any) -> None:
    partner_unicef = PartnerFactory(name="UNICEF")
    partner_unicef_hq = PartnerFactory(name="UNICEF HQ", parent=partner_unicef)
    role, _ = Role.objects.update_or_create(
        name="RECEIVE_PP_OVERDUE_EMAIL", defaults={"permissions": [Permissions.RECEIVE_PP_OVERDUE_EMAIL.value]}
    )

    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program)
    pp = PaymentListFactory(
        dispersion_start_date=now() - timedelta(days=10),
        dispersion_end_date=now(),
        status=PaymentList.Status.ACCEPTED,
        program_cycle=cycle,
    )
    pp.refresh_from_db()
    program = pp.program
    program.reconciliation_window_in_days = 10
    program.send_reconciliation_window_expiry_notifications = True
    program.save()

    different_program = ProgramFactory(business_area=business_area)

    user_with_perm_in_program = UserFactory(partner=partner_unicef_hq)
    RoleAssignment.objects.create(
        user=user_with_perm_in_program, role=role, business_area=business_area, program=program
    )

    user_with_perm_ba_wide = UserFactory(partner=partner_unicef_hq)
    RoleAssignment.objects.create(user=user_with_perm_ba_wide, role=role, business_area=business_area, program=None)

    superuser_with_perm = UserFactory(partner=partner_unicef_hq, is_superuser=True)
    RoleAssignment.objects.create(user=superuser_with_perm, role=role, business_area=business_area, program=program)

    user_with_perm_in_different_program = UserFactory(partner=partner_unicef_hq)
    RoleAssignment.objects.create(
        user=user_with_perm_in_different_program, role=role, business_area=business_area, program=different_program
    )

    with mock.patch.object(User, "email_user", autospec=True) as mock_email_user:
        PaymentListService(pp).send_reconciliation_overdue_email_for_pp()

        assert mock_email_user.call_count == 2
        emailed_users = {call.args[0] for call in mock_email_user.call_args_list}
        assert user_with_perm_in_program in emailed_users
        assert user_with_perm_ba_wide in emailed_users
        assert superuser_with_perm not in emailed_users
        assert user_with_perm_in_different_program not in emailed_users


@override_config(NOTIFY_INTERNAL_USERS=True)
def test_send_reconciliation_overdue_email_recipients_include_internal_users(business_area: Any) -> None:
    partner_unicef = PartnerFactory(name="UNICEF")
    partner_unicef_hq = PartnerFactory(name="UNICEF HQ", parent=partner_unicef)
    role, _ = Role.objects.update_or_create(
        name="RECEIVE_PP_OVERDUE_EMAIL", defaults={"permissions": [Permissions.RECEIVE_PP_OVERDUE_EMAIL.value]}
    )

    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program)
    pp = PaymentListFactory(
        dispersion_start_date=now() - timedelta(days=10),
        dispersion_end_date=now(),
        status=PaymentList.Status.ACCEPTED,
        program_cycle=cycle,
    )
    pp.refresh_from_db()
    program = pp.program
    program.reconciliation_window_in_days = 10
    program.send_reconciliation_window_expiry_notifications = True
    program.save()

    superuser_with_perm = UserFactory(partner=partner_unicef_hq, is_superuser=True)
    RoleAssignment.objects.create(user=superuser_with_perm, role=role, business_area=business_area, program=program)

    with mock.patch.object(User, "email_user", autospec=True) as mock_email_user:
        PaymentListService(pp).send_reconciliation_overdue_email_for_pp()

        assert mock_email_user.call_count == 1
        assert mock_email_user.call_args_list[0].args[0] == superuser_with_perm


@pytest.fixture
def locked_payment_list():
    return PaymentListFactory(
        program_cycle=ProgramCycleFactory(),
        status=PaymentList.Status.LOCKED,
    )


@pytest.fixture
def locked_payment_list_with_payments(locked_payment_list):
    for _ in range(PaymentListSplit.MIN_NO_OF_PAYMENTS_IN_CHUNK + 1):
        PaymentFactory(parent=locked_payment_list)
    return locked_payment_list


@patch("hope.apps.payment.services.payment_list_services.config")
def test_validate_acceptance_raises_type_error_when_required_number_is_none(mock_config, locked_payment_list):
    mock_config.PM_ACCEPTANCE_PROCESS_USER_HAVE_MULTIPLE_APPROVALS = True
    service = PaymentListService(payment_list=locked_payment_list)
    service.action = PaymentList.Action.APPROVE.value
    approval_process = mock.MagicMock()

    with patch.object(service, "get_required_number_by_approval_type", return_value=None):
        with pytest.raises(TypeError):
            service.validate_acceptance_process_approval_count(approval_process)


def test_check_payment_list_and_update_status_raises_type_error_when_required_number_is_none(locked_payment_list):
    service = PaymentListService(payment_list=locked_payment_list)
    service.action = PaymentList.Action.APPROVE.value
    approval_process = mock.MagicMock()

    with patch.object(service, "get_required_number_by_approval_type", return_value=None):
        with pytest.raises(TypeError):
            service.check_payment_list_and_update_status(approval_process)


@patch("hope.apps.payment.services.payment_list_services.config")
def test_validate_acceptance_does_not_raise_when_count_below_required(mock_config, locked_payment_list):
    mock_config.PM_ACCEPTANCE_PROCESS_USER_HAVE_MULTIPLE_APPROVALS = True
    service = PaymentListService(payment_list=locked_payment_list)
    service.action = PaymentList.Action.APPROVE.value
    approval_process = mock.MagicMock()
    approval_process.approvals.filter.return_value.count.return_value = 0

    with patch.object(service, "get_required_number_by_approval_type", return_value=5):
        service.validate_acceptance_process_approval_count(approval_process)


@patch("hope.apps.payment.services.payment_list_services.config")
def test_validate_acceptance_raises_when_count_meets_required(mock_config, locked_payment_list):
    mock_config.PM_ACCEPTANCE_PROCESS_USER_HAVE_MULTIPLE_APPROVALS = True
    service = PaymentListService(payment_list=locked_payment_list)
    service.action = PaymentList.Action.APPROVE.value
    approval_process = mock.MagicMock()
    approval_process.approvals.filter.return_value.count.return_value = 5

    with patch.object(service, "get_required_number_by_approval_type", return_value=5):
        with pytest.raises(ValidationError, match="Can't create new approval"):
            service.validate_acceptance_process_approval_count(approval_process)


def test_check_payment_list_and_update_status_does_not_change_when_count_below_required(locked_payment_list):
    service = PaymentListService(payment_list=locked_payment_list)
    service.action = PaymentList.Action.APPROVE.value
    approval_process = mock.MagicMock()
    approval_process.approvals.filter.return_value.count.return_value = 0

    with patch.object(service, "get_required_number_by_approval_type", return_value=5):
        service.check_payment_list_and_update_status(approval_process)


@patch("hope.apps.payment.services.payment_list_services.send_payment_notification_emails_async_task")
@patch("hope.apps.payment.services.payment_list_services.PaymentListFlow")
def test_check_payment_list_and_update_status_triggers_when_count_meets_required(
    mock_flow_cls, mock_notify, locked_payment_list
):
    service = PaymentListService(payment_list=locked_payment_list)
    service.action = PaymentList.Action.APPROVE.value
    service.user = mock.MagicMock()
    approval_process = mock.MagicMock()
    approval_process.approvals.filter.return_value.count.return_value = 5

    with patch.object(service, "get_required_number_by_approval_type", return_value=5):
        service.check_payment_list_and_update_status(approval_process)

    mock_flow_cls.return_value.status_approve.assert_called_once()


@patch("hope.apps.payment.services.payment_list_services.send_payment_notification_emails_async_task")
@patch("hope.apps.payment.services.payment_list_services.PaymentListFlow")
def test_check_payment_list_and_update_status_rejects_without_notification(
    mock_flow_cls, mock_notify, locked_payment_list
):
    service = PaymentListService(payment_list=locked_payment_list)
    service.action = PaymentList.Action.REJECT.value
    service.user = mock.MagicMock()
    approval_process = mock.MagicMock()
    approval_process.approvals.filter.return_value.count.return_value = 1

    with patch.object(service, "get_required_number_by_approval_type", return_value=1):
        service.check_payment_list_and_update_status(approval_process)

    mock_flow_cls.return_value.status_reject.assert_called_once()
    mock_notify.assert_not_called()


@pytest.fixture
def vision_authorization_context():
    business_area = BusinessAreaFactory(vision_integration_active=True)
    payment_list = PaymentListFactory(
        business_area=business_area,
        program_cycle__program__business_area=business_area,
        status=PaymentList.Status.IN_AUTHORIZATION,
    )
    approval_process = ApprovalProcessFactory(
        payment_list=payment_list,
        authorization_number_required=1,
    )
    ApprovalFactory(
        approval_process=approval_process,
        type="AUTHORIZATION",
        created_by=payment_list.created_by,
    )
    return payment_list, approval_process


@patch("hope.contrib.vision.tasks.send_payment_plan_to_vision_async_task")
@patch("hope.apps.payment.services.payment_list_services.send_payment_notification_emails_async_task")
def test_plan_authorization_does_not_queue_group_vision_send(
    mock_notification,
    mock_send_to_vision,
    vision_authorization_context,
    django_capture_on_commit_callbacks,
) -> None:
    FlagState.objects.get_or_create(
        name="VISION_INTEGRATION_ACTIVE",
        condition="boolean",
        value="True",
    )
    payment_list, approval_process = vision_authorization_context
    service = PaymentListService(payment_list)
    service.action = PaymentList.Action.AUTHORIZE.value
    service.user = payment_list.created_by

    with django_capture_on_commit_callbacks(execute=True):
        service.check_payment_list_and_update_status(approval_process)

    payment_list.refresh_from_db()
    assert payment_list.status == PaymentList.Status.IN_REVIEW
    mock_send_to_vision.assert_not_called()


def test_ready_for_closure_moves_plan_to_ready_for_closure(
    business_area: Any, cycle: ProgramCycle, django_assert_num_queries: Any
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        business_area=business_area,
        status=PaymentList.Status.FINISHED,
    )

    with django_assert_num_queries(12):
        PaymentListService(payment_list).ready_for_closure()

    payment_list.refresh_from_db()
    assert payment_list.status == PaymentList.Status.READY_FOR_CLOSURE


def test_send_back_to_finished_moves_plan_to_finished(
    business_area: Any, cycle: ProgramCycle, django_assert_num_queries: Any
) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        business_area=business_area,
        status=PaymentList.Status.READY_FOR_CLOSURE,
    )

    with django_assert_num_queries(12):
        PaymentListService(payment_list).send_back_to_finished()

    payment_list.refresh_from_db()
    assert payment_list.status == PaymentList.Status.FINISHED


def test_ready_for_closure_rejects_stale_status(business_area: Any, cycle: ProgramCycle) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        business_area=business_area,
        status=PaymentList.Status.FINISHED,
    )
    PaymentList.objects.filter(pk=payment_list.pk).update(status=PaymentList.Status.READY_FOR_CLOSURE)

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).ready_for_closure()

    assert "Mark as Ready for Closure is possible only within Status FINISHED" in str(error.value)


def test_send_back_to_finished_rejects_stale_status(business_area: Any, cycle: ProgramCycle) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        business_area=business_area,
        status=PaymentList.Status.READY_FOR_CLOSURE,
    )
    PaymentList.objects.filter(pk=payment_list.pk).update(status=PaymentList.Status.FINISHED)

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).send_back_to_finished()

    assert "Send Back is possible only within Status READY_FOR_CLOSURE" in str(error.value)


def test_close_rejects_stale_status(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        business_area=business_area,
        status=PaymentList.Status.READY_FOR_CLOSURE,
    )
    PaymentList.objects.filter(pk=payment_list.pk).update(status=PaymentList.Status.CLOSED)

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).close(closure_comment="Comment", user_id=str(user.pk))

    assert "Close Payment List is possible only within Status READY_FOR_CLOSURE" in str(error.value)


def test_acceptance_process_rejects_stale_status(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        business_area=business_area,
        status=PaymentList.Status.IN_APPROVAL,
    )
    ApprovalProcessFactory(payment_list=payment_list)
    PaymentList.objects.filter(pk=payment_list.pk).update(status=PaymentList.Status.IN_AUTHORIZATION)

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).execute_update_status_action(
            input_data={"action": PaymentList.Action.APPROVE.value, "comment": ""}, user=user
        )

    assert "Not possible to create APPROVE for Payment List within status IN_AUTHORIZATION" in str(error.value)


def test_build_payments_chunks_with_chunks_no_none_returns_single_chunk(locked_payment_list_with_payments):
    service = PaymentListService(payment_list=locked_payment_list_with_payments)
    payments = locked_payment_list_with_payments.eligible_payments.all()
    payments_count = payments.count()

    with patch.object(service, "_validate_split_by_record"):
        result = service._build_payments_chunks(
            split_type=PaymentListSplit.SplitType.BY_RECORDS,
            chunks_no=None,
            payments=payments,
            payments_count=payments_count,
        )
    assert len(result) == 1


def test_set_program_cycle_same_cycle_returns_early(business_area: Any, cycle: ProgramCycle) -> None:
    pp = PaymentListFactory(
        program_cycle=cycle,
        business_area=business_area,
        status=PaymentList.Status.TP_OPEN,
    )
    service = PaymentListService(payment_list=pp)
    service._set_program_cycle({"program_cycle_id": str(cycle.pk)})
    pp.refresh_from_db()
    assert pp.program_cycle == cycle


def test_execute_update_status_action_raises_when_instruction_managed(
    payment_list_base: PaymentList,
    user: User,
) -> None:
    instruction = FollowUpInstructionFactory(
        business_area=payment_list_base.business_area,
        program=payment_list_base.program,
        created_by=user,
    )
    payment_list_base.follow_up_instruction = instruction
    payment_list_base.payment_plan = None
    payment_list_base.save(update_fields=["follow_up_instruction", "payment_plan"])

    with pytest.raises(ValidationError, match="This Payment List is managed by a Follow Up Instruction."):
        PaymentListService(payment_list_base).execute_update_status_action(input_data={"action": "LOCK"}, user=user)


def test_copy_target_criteria_copies_individual_block_filters(
    business_area: Any,
    cycle: ProgramCycle,
) -> None:
    source_pp = PaymentListFactory(program_cycle=cycle, business_area=business_area)
    target_pp = PaymentListFactory(program_cycle=cycle, business_area=business_area)
    rule = TargetingCriteriaRuleFactory(payment_list=source_pp)
    ind_block = TargetingIndividualRuleFilterBlockFactory(targeting_criteria_rule=rule)
    TargetingIndividualBlockRuleFilterFactory(individuals_filters_block=ind_block)

    PaymentListService.copy_target_criteria(source_pp, target_pp)

    target_rule = target_pp.rules.get()
    target_block = target_rule.individuals_filters_blocks.get()
    assert TargetingIndividualBlockRuleFilter.objects.filter(individuals_filters_block=target_block).count() == 1


def test_set_group_for_open_pp_returns_early_when_cycle_is_changing(
    user: User,
    business_area: Any,
    program: Program,
) -> None:
    cycle_a = ProgramCycleFactory(status=ProgramCycle.ACTIVE, program=program)
    cycle_b = ProgramCycleFactory(status=ProgramCycle.ACTIVE, program=program)
    pp = PaymentListFactory(
        created_by=user,
        business_area=business_area,
        program_cycle=cycle_a,
        status=PaymentList.Status.TP_OPEN,
    )
    group_in_b = PaymentPlanFactory(cycle=cycle_b)
    service = PaymentListService(pp)

    service._set_payment_plan_for_open_payment_list(
        {"payment_plan_id": str(group_in_b.id), "program_cycle_id": cycle_b.id}
    )

    assert pp.payment_plan != group_in_b


def test_change_group_rejects_group_not_open(
    user: User,
    business_area: Any,
    program: Program,
) -> None:
    cycle = ProgramCycleFactory(status=ProgramCycle.ACTIVE, program=program)
    pp = PaymentListFactory(
        created_by=user,
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentList.Status.TP_OPEN,
    )
    locked_payment_plan = PaymentPlanFactory(cycle=cycle, status=PaymentPlan.Status.LOCKED)
    service = PaymentListService(pp)

    with pytest.raises(ValidationError) as error:
        service._set_payment_plan_for_open_payment_list({"payment_plan_id": str(locked_payment_plan.id)})
    assert error.value.detail[0] == "Adding Target Population to Payment Plan is possible only within Status OPEN"


def test_status_action_rejected_when_group_is_not_open(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_list = PaymentListFactory(
        program_cycle=cycle,
        payment_plan=PaymentPlanFactory(cycle=cycle, status=PaymentPlan.Status.LOCKED),
        business_area=business_area,
        status=PaymentList.Status.LOCKED_FSP,
    )

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list).execute_update_status_action(
            input_data={"action": PaymentList.Action.UNLOCK_FSP}, user=user
        )
    assert error.value.detail[0] == "This Payment List is managed by its Payment Plan."
