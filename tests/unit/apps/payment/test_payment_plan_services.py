from datetime import timedelta
from decimal import Decimal
from typing import Any
from unittest import mock
from unittest.mock import patch

from aniso8601 import parse_date
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.timezone import now
from freezegun import freeze_time
import pytest
from pytz import utc
from rest_framework.exceptions import ValidationError
from viewflow.fsm import TransitionNotAllowed

from extras.test_utils.factories import (
    AccountFactory,
    AccountTypeFactory,
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanSplitFactory,
    ProgramCycleFactory,
    ProgramFactory,
    TargetingCriteriaRuleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.household.const import ROLE_PRIMARY
from hope.apps.payment.celery_tasks import (
    prepare_follow_up_payment_plan_task,
    prepare_payment_plan_task,
)
from hope.apps.payment.flows import PaymentPlanFlow
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.models import (
    AccountType,
    DeliveryMechanism,
    FileTemp,
    FinancialServiceProvider,
    IndividualRoleInHousehold,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
    Program,
    ProgramCycle,
    Role,
    RoleAssignment,
    User,
)

pytestmark = pytest.mark.django_db


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
def fsp(dm_transfer_to_account: Any, dm_transfer_to_digital_wallet: Any) -> FinancialServiceProvider:
    fsp = FinancialServiceProviderFactory(
        name="Test FSP 1",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
    )
    fsp.delivery_mechanisms.add(dm_transfer_to_account, dm_transfer_to_digital_wallet)
    return fsp


@pytest.fixture
def account_type_bank() -> AccountType:
    return AccountTypeFactory(key="bank", label="Bank")


@pytest.fixture
def program(business_area: Any) -> Program:
    return ProgramFactory(status=Program.ACTIVE, business_area=business_area)


@pytest.fixture
def cycle(program: Program) -> ProgramCycle:
    return ProgramCycleFactory(status=ProgramCycle.ACTIVE, program=program)


@pytest.fixture
def payment_plan_base(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
) -> PaymentPlan:
    return PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.TP_LOCKED,
        delivery_mechanism=dm_transfer_to_account,
        financial_service_provider=fsp,
    )


def test_delete_tp_open(payment_plan_base: PaymentPlan) -> None:
    payment_plan_base.status = PaymentPlan.Status.TP_OPEN
    payment_plan_base.save()

    pp = PaymentPlanService(payment_plan=payment_plan_base).delete()

    assert pp.is_removed is True
    assert pp.status == PaymentPlan.Status.TP_OPEN


def test_delete_open(payment_plan_base: PaymentPlan) -> None:
    payment_plan_base.status = PaymentPlan.Status.OPEN
    payment_plan_base.save()

    pp = PaymentPlanService(payment_plan=payment_plan_base).delete()

    assert pp.is_removed is False
    assert pp.status == PaymentPlan.Status.DRAFT


def test_delete_locked(payment_plan_base: PaymentPlan) -> None:
    payment_plan_base.status = PaymentPlan.Status.LOCKED
    payment_plan_base.save()

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan=payment_plan_base).delete()

    assert error.value.detail[0] == "Deletion is only allowed when the status is 'Open'"


def test_delete_when_its_one_pp_in_cycle(payment_plan_base: PaymentPlan) -> None:
    payment_plan_base.status = PaymentPlan.Status.OPEN
    payment_plan_base.save()
    assert payment_plan_base.program_cycle.status == ProgramCycle.ACTIVE

    pp = PaymentPlanService(payment_plan=payment_plan_base).delete()

    assert pp.is_removed is False
    assert pp.status == PaymentPlan.Status.DRAFT
    payment_plan_base.program_cycle.refresh_from_db()
    assert payment_plan_base.program_cycle.status == ProgramCycle.DRAFT


def test_delete_when_its_two_pp_in_cycle(user: User, business_area: Any) -> None:
    program = ProgramFactory(status=Program.ACTIVE, business_area=business_area)
    program_cycle = ProgramCycleFactory(status=ProgramCycle.ACTIVE, program=program)
    pp_1 = PaymentPlanFactory(
        status=PaymentPlan.Status.OPEN,
        program_cycle=program_cycle,
        created_by=user,
        business_area=business_area,
    )
    PaymentPlanFactory(
        status=PaymentPlan.Status.OPEN,
        program_cycle=program_cycle,
        created_by=user,
        business_area=business_area,
    )

    assert pp_1.program_cycle.status == ProgramCycle.ACTIVE

    pp_1 = PaymentPlanService(payment_plan=pp_1).delete()

    assert pp_1.is_removed is False
    assert pp_1.status == PaymentPlan.Status.DRAFT
    program_cycle.refresh_from_db()
    assert program_cycle.status == ProgramCycle.ACTIVE


@freeze_time("2020-10-10")
def test_create_validation_errors(user: User, business_area: Any) -> None:
    program = ProgramFactory(
        status=Program.ACTIVE,
        business_area=business_area,
        start_date=timezone.datetime(2019, 10, 12, tzinfo=utc).date(),
        end_date=timezone.datetime(2099, 12, 10, tzinfo=utc).date(),
    )
    program_cycle = ProgramCycleFactory(
        program=program,
        start_date=timezone.datetime(2021, 10, 10, tzinfo=utc).date(),
        end_date=timezone.datetime(2021, 12, 10, tzinfo=utc).date(),
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

    PaymentPlanFactory(
        program_cycle=program_cycle,
        name="TEST_123",
        created_by=user,
        business_area=business_area,
    )
    with pytest.raises(ValidationError) as error:
        PaymentPlanService.create(
            input_data=create_input_data,
            user=user,
            business_area_slug=business_area.slug,
        )
    assert error.value.detail[0] == f"Target Population with name: TEST_123 and program: {program.name} already exists."

    program.status = Program.FINISHED
    program.save()
    program.refresh_from_db()
    with pytest.raises(ValidationError) as error:
        PaymentPlanService.create(
            input_data=create_input_data,
            user=user,
            business_area_slug=business_area.slug,
        )
    assert error.value.detail[0] == "Impossible to create Target Population for Programme within not Active status"

    program_cycle.status = ProgramCycle.FINISHED
    program_cycle.save()
    with pytest.raises(ValidationError) as error:
        PaymentPlanService.create(
            input_data=create_input_data,
            user=user,
            business_area_slug=business_area.slug,
        )
    assert error.value.detail[0] == "Impossible to create Target Population for Programme Cycle within Finished status"

    program_cycle.status = ProgramCycle.ACTIVE
    program_cycle.save()
    program.status = Program.ACTIVE
    program.save()

    create_input_data["name"] = "TEST"
    pp = PaymentPlanService.create(
        input_data=create_input_data,
        user=user,
        business_area_slug=business_area.slug,
    )
    pp.status = PaymentPlan.Status.TP_OPEN
    pp.save()

    open_input_data = {
        "dispersion_start_date": parse_date("2020-09-10"),
        "dispersion_end_date": parse_date("2020-09-11"),
        "currency": "USD",
    }
    with pytest.raises(TransitionNotAllowed) as error:
        PaymentPlanService(payment_plan=pp).open(input_data=open_input_data)
    assert str(error.value) == 'Status_Open :: no transition from "TP_OPEN"'

    pp.status = PaymentPlan.Status.DRAFT
    pp.save()
    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan=pp).open(input_data=open_input_data)
    assert (
        error.value.detail[0] == f"Dispersion End Date [{open_input_data['dispersion_end_date']}] cannot be a past date"
    )

    open_input_data["dispersion_end_date"] = parse_date("2020-11-11")
    pp.refresh_from_db()
    assert pp.status == PaymentPlan.Status.DRAFT

    pp = PaymentPlanService(payment_plan=pp).open(input_data=open_input_data)
    pp.refresh_from_db()

    assert pp.status == PaymentPlan.Status.OPEN


@freeze_time("2020-10-10")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create(
    get_exchange_rate_mock: Any,
    user: User,
    business_area: Any,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
    account_type_bank: AccountType,
    django_assert_num_queries: Any,
) -> None:
    program = ProgramFactory(
        status=Program.ACTIVE,
        business_area=business_area,
        start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
        end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
    )
    program_cycle = ProgramCycleFactory(program=program)

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

    input_data = {
        "business_area_slug": "afghanistan",
        "name": "paymentPlanName",
        "program_cycle_id": program_cycle.id,
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
        "fsp_id": fsp.id,
        "delivery_mechanism_code": dm_transfer_to_account.code,
    }

    with mock.patch("hope.apps.payment.services.payment_plan_services.transaction") as mock_transaction:
        with django_assert_num_queries(16):
            pp = PaymentPlanService.create(
                input_data=input_data,
                user=user,
                business_area_slug=business_area.slug,
            )
        assert mock_transaction.on_commit.call_count == 1

    assert pp.status == PaymentPlan.Status.TP_OPEN
    assert pp.total_households_count == 0
    assert pp.total_individuals_count == 0
    assert pp.payment_items.count() == 0

    with django_assert_num_queries(86):
        prepare_payment_plan_task.delay(str(pp.id))

    pp.refresh_from_db()
    assert pp.status == PaymentPlan.Status.TP_OPEN
    assert pp.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK
    assert pp.total_households_count == 2
    assert pp.total_individuals_count == 6
    assert pp.payment_items.count() == 2


@freeze_time("2020-10-10")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_update_validation_errors(get_exchange_rate_mock: Any, payment_plan_base: PaymentPlan) -> None:
    payment_plan_base.status = PaymentPlan.Status.LOCKED
    payment_plan_base.save()

    input_data = {
        "dispersion_start_date": parse_date("2020-09-10"),
        "dispersion_end_date": parse_date("2020-09-11"),
        "currency": "USD",
    }

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan=payment_plan_base).update(input_data=input_data)
    assert error.value.detail[0] == "Not Allow edit Payment Plan within status LOCKED"

    payment_plan_base.status = PaymentPlan.Status.OPEN
    payment_plan_base.save()

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan=payment_plan_base).update(input_data=input_data)
    assert error.value.detail[0] == f"Dispersion End Date [{input_data['dispersion_end_date']}] cannot be a past date"


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_follow_up_pp(
    get_exchange_rate_mock: Any,
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    django_assert_num_queries: Any,
) -> None:
    pp = PaymentPlanFactory(
        total_households_count=1,
        created_by=user,
        business_area=business_area,
        program_cycle=cycle,
        name="Test Payment Plan",
    )
    program = pp.program_cycle.program
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
            currency="PLN",
        )
        payments.append(payment)

    dispersion_start_date = pp.dispersion_start_date + timedelta(days=1)
    dispersion_end_date = pp.dispersion_end_date + timedelta(days=1)

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(pp).create_follow_up(user, dispersion_start_date, dispersion_end_date)
    assert error.value.detail[0] == "Cannot create a follow-up for a payment plan with no unsuccessful payments"

    for payment, status in zip(payments[:4], Payment.FAILED_STATUSES, strict=True):
        payment.status = status
        payment.save()

    payments[4].household.withdrawn = True
    payments[4].household.save()

    p_error = payments[0]
    p_not_distributed = payments[1]
    p_force_failed = payments[2]
    p_manually_cancelled = payments[3]

    with django_assert_num_queries(6):
        follow_up_pp = PaymentPlanService(pp).create_follow_up(user, dispersion_start_date, dispersion_end_date)

    follow_up_pp.refresh_from_db()
    assert follow_up_pp.status == PaymentPlan.Status.OPEN
    assert follow_up_pp.program == pp.program
    assert follow_up_pp.program_cycle == pp.program_cycle
    assert follow_up_pp.business_area == pp.business_area
    assert follow_up_pp.created_by == user
    assert follow_up_pp.currency == pp.currency
    assert follow_up_pp.dispersion_start_date == dispersion_start_date
    assert follow_up_pp.dispersion_end_date == dispersion_end_date
    assert follow_up_pp.program_cycle.start_date == pp.program_cycle.start_date
    assert follow_up_pp.program_cycle.end_date == pp.program_cycle.end_date
    assert follow_up_pp.total_households_count == 0
    assert follow_up_pp.total_individuals_count == 0
    assert follow_up_pp.payment_items.count() == 0

    assert pp.follow_ups.count() == 1

    prepare_follow_up_payment_plan_task(follow_up_pp.id)
    follow_up_pp.refresh_from_db()

    assert follow_up_pp.status == PaymentPlan.Status.OPEN
    assert follow_up_pp.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK

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

    with django_assert_num_queries(6):
        follow_up_pp_2 = PaymentPlanService(pp).create_follow_up(user, dispersion_start_date, dispersion_end_date)

    assert pp.follow_ups.count() == 2

    with django_assert_num_queries(53):
        prepare_follow_up_payment_plan_task(follow_up_pp_2.id)

    assert follow_up_pp_2.payment_items.count() == 1
    assert {follow_up_payment.source_payment.id} == set(
        follow_up_pp_2.payment_items.values_list("source_payment_id", flat=True)
    )


def test_create_follow_up_pp_from_follow_up_validation(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.FINISHED,
        is_follow_up=True,
    )
    dispersion_start_date = payment_plan.dispersion_start_date + timedelta(days=1)
    dispersion_end_date = payment_plan.dispersion_end_date + timedelta(days=1)

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan).create_follow_up(user, dispersion_start_date, dispersion_end_date)

    assert error.value.detail[0] == "Cannot create a follow-up of a follow-up Payment Plan"


def test_update_follow_up_dates_and_not_currency(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.OPEN,
        currency="PLN",
        is_follow_up=True,
    )
    dispersion_start_date = payment_plan.dispersion_start_date + timedelta(days=1)
    dispersion_end_date = payment_plan.dispersion_end_date + timedelta(days=1)
    payment_plan = PaymentPlanService(payment_plan).update(
        {
            "dispersion_start_date": dispersion_start_date,
            "dispersion_end_date": dispersion_end_date,
            "currency": "UAH",
        }
    )
    assert payment_plan.currency == "PLN"
    assert payment_plan.dispersion_start_date == dispersion_start_date
    assert payment_plan.dispersion_end_date == dispersion_end_date


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
@patch("hope.models.payment_plan_split.PaymentPlanSplit.MIN_NO_OF_PAYMENTS_IN_CHUNK")
def test_split(
    min_no_of_payments_in_chunk_mock: Any,
    get_exchange_rate_mock: Any,
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    django_assert_num_queries: Any,
) -> None:
    min_no_of_payments_in_chunk_mock.__get__ = mock.Mock(return_value=2)

    pp = PaymentPlanFactory(created_by=user, business_area=business_area, program_cycle=cycle)

    with pytest.raises(ValidationError, match="No payments to split"):
        PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_COLLECTOR)

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
            currency="PLN",
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
            currency="PLN",
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
            currency="PLN",
            collector=collector,
        )
        payments.append(payment)

    with pytest.raises(ValidationError, match="Payments Number is required for split by records"):
        PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_RECORDS, chunks_no=None)

    with pytest.raises(ValidationError, match="Payment Parts number should be between 2 and total number of payments"):
        PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_RECORDS, chunks_no=669)

    with mock.patch("hope.apps.payment.services.payment_plan_services.PaymentPlanSplit.MAX_CHUNKS") as max_chunks_patch:
        max_chunks_patch.__get__ = mock.Mock(return_value=2)
        with pytest.raises(ValidationError, match="Too many Payment Parts to split: 6, maximum is 2"):
            PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_RECORDS, chunks_no=2)

    with django_assert_num_queries(26):
        PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_COLLECTOR)
    unique_collectors_count = pp.eligible_payments.values_list("collector", flat=True).distinct().count()
    assert unique_collectors_count == 10
    pp_splits = pp.splits.all().order_by("order")

    assert pp_splits.count() == unique_collectors_count
    assert pp_splits[0].split_type == PaymentPlanSplit.SplitType.BY_COLLECTOR
    split_payment_counts = sorted([s.split_payment_items.count() for s in pp_splits], reverse=True)
    assert split_payment_counts == [3, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    with django_assert_num_queries(16):
        PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_RECORDS, chunks_no=5)
    pp_splits = pp.splits.all().order_by("order")
    assert pp_splits.count() == 3
    assert pp_splits[0].split_type == PaymentPlanSplit.SplitType.BY_RECORDS
    assert pp_splits[0].split_payment_items.count() == 5
    assert pp_splits[1].split_payment_items.count() == 5
    assert pp_splits[2].split_payment_items.count() == 2

    with django_assert_num_queries(14):
        PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_ADMIN_AREA2)
    unique_admin2_count = pp.eligible_payments.values_list("household__admin2", flat=True).distinct().count()
    assert unique_admin2_count == 2
    pp_splits = pp.splits.all().order_by("order")
    assert pp.splits.count() == unique_admin2_count
    assert pp_splits[0].split_type == PaymentPlanSplit.SplitType.BY_ADMIN_AREA2
    assert pp_splits[0].split_payment_items.count() == 4
    assert pp_splits[1].split_payment_items.count() == 8

    PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.NO_SPLIT)
    pp_splits = pp.splits.all().order_by("order")
    assert pp.splits.count() == 1
    assert pp_splits[0].split_type == PaymentPlanSplit.SplitType.NO_SPLIT
    assert pp_splits[0].split_payment_items.count() == 12


@freeze_time("2023-10-10")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_send_to_payment_gateway(
    get_exchange_rate_mock: Any,
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    dm_transfer_to_account: Any,
) -> None:
    pg_fsp = FinancialServiceProviderFactory(
        name="Western Union",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        payment_gateway_id="123",
    )
    pg_fsp.delivery_mechanisms.add(dm_transfer_to_account)
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        created_by=user,
        business_area=business_area,
        program_cycle=cycle,
        financial_service_provider=pg_fsp,
        delivery_mechanism=dm_transfer_to_account,
    )
    flow = PaymentPlanFlow(pp)
    flow.background_action_status_send_to_payment_gateway()
    pp.save()

    with pytest.raises(ValidationError, match="Sending in progress"):
        PaymentPlanService(pp).send_to_payment_gateway()

    flow.background_action_status_none()
    pp.save()

    split = PaymentPlanSplitFactory(payment_plan=pp, sent_to_payment_gateway=True)

    with pytest.raises(ValidationError, match="Already sent to Payment Gateway"):
        PaymentPlanService(pp).send_to_payment_gateway()

    split.sent_to_payment_gateway = False
    split.save()
    with mock.patch("hope.apps.payment.services.payment_plan_services.send_to_payment_gateway.delay") as mock_task:
        pps = PaymentPlanService(pp)
        pps.user = mock.MagicMock(pk="123")
        pps.send_to_payment_gateway()
        assert mock_task.call_count == 1


@mock.patch("hope.apps.payment.services.payment_plan_services.import_payment_plan_payment_list_per_fsp_from_xlsx.delay")
def test_import_xlsx_per_fsp(
    mock_task: Any,
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    django_capture_on_commit_callbacks: Any,
) -> None:
    pp = PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        created_by=user,
        business_area=business_area,
        program_cycle=cycle,
        background_action_status=None,
    )

    mock_file = SimpleUploadedFile(
        "test.xlsx",
        b"test file content",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    service = PaymentPlanService(pp)

    with django_capture_on_commit_callbacks(execute=True):
        result = service.import_xlsx_per_fsp(user, mock_file)

    assert mock_task.call_count == 1

    pp.refresh_from_db()
    assert pp.background_action_status == PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION
    assert pp.reconciliation_import_file is not None
    assert result == pp


@freeze_time("2020-10-10")
def test_create_with_program_cycle_validation_error(user: User, business_area: Any) -> None:
    program = ProgramFactory(
        status=Program.ACTIVE,
        business_area=business_area,
        start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
        end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
    )
    cycle = ProgramCycleFactory(
        program=program,
        start_date=timezone.datetime(2021, 10, 10, tzinfo=utc).date(),
        end_date=timezone.datetime(2021, 12, 10, tzinfo=utc).date(),
        status=ProgramCycle.ACTIVE,
    )
    input_data = {
        "business_area_slug": "afghanistan",
        "dispersion_start_date": parse_date("2020-11-11"),
        "dispersion_end_date": parse_date("2020-11-20"),
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
    }

    cycle.status = ProgramCycle.FINISHED
    cycle.save()
    with pytest.raises(ValidationError) as error:
        PaymentPlanService.create(
            input_data=input_data,
            user=user,
            business_area_slug=business_area.slug,
        )
    assert error.value.detail[0] == "Impossible to create Target Population for Programme Cycle within Finished status"

    cycle.status = ProgramCycle.DRAFT
    cycle.end_date = None
    cycle.save()
    PaymentPlanService.create(
        input_data=input_data,
        user=user,
        business_area_slug=business_area.slug,
    )
    cycle.refresh_from_db()
    assert cycle.status == ProgramCycle.DRAFT


@freeze_time("2022-12-12")
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_full_rebuild(
    get_exchange_rate_mock: Any,
    user: User,
    business_area: Any,
    django_assert_num_queries: Any,
) -> None:
    program = ProgramFactory(
        status=Program.ACTIVE,
        business_area=business_area,
        start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
        end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
    )
    program_cycle = ProgramCycleFactory(program=program)

    hh1 = HouseholdFactory(program=program, business_area=business_area)
    hh2 = HouseholdFactory(program=program, business_area=business_area)
    IndividualFactory.create_batch(
        4,
        household=hh1,
        business_area=business_area,
        program=program,
        registration_data_import=hh1.registration_data_import,
    )

    input_data = {
        "business_area_slug": "afghanistan",
        "name": "paymentPlanName",
        "program_cycle_id": program_cycle.id,
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
    }
    with mock.patch("hope.apps.payment.services.payment_plan_services.transaction") as mock_transaction:
        with django_assert_num_queries(12):
            pp = PaymentPlanService.create(
                input_data=input_data,
                user=user,
                business_area_slug=business_area.slug,
            )
        assert mock_transaction.on_commit.call_count == 1

    assert pp.status == PaymentPlan.Status.TP_OPEN
    assert pp.total_households_count == 0
    assert pp.total_individuals_count == 0
    assert pp.payment_items.count() == 0

    with django_assert_num_queries(70):
        prepare_payment_plan_task.delay(str(pp.id))

    pp.refresh_from_db()
    assert pp.status == PaymentPlan.Status.TP_OPEN
    assert pp.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK
    assert pp.payment_items.count() == 2

    old_payment_ids = list(pp.payment_items.values_list("id", flat=True))
    old_payment_unicef_ids = list(pp.payment_items.values_list("unicef_id", flat=True))

    pp_service = PaymentPlanService(payment_plan=pp)
    pp_service.full_rebuild()

    pp.refresh_from_db()
    assert Payment.all_objects.filter(parent=pp).count() == 2

    new_payment_ids = list(pp.payment_items.values_list("id", flat=True))
    new_payment_unicef_ids = list(pp.payment_items.values_list("unicef_id", flat=True))

    for payment_id in new_payment_ids:
        assert payment_id not in old_payment_ids

    for payment_unicef_id in new_payment_unicef_ids:
        assert payment_unicef_id not in old_payment_unicef_ids


def test_get_approval_type_by_action_value_error(payment_plan_base: PaymentPlan) -> None:
    with pytest.raises(ValueError, match="Action cannot be None"):
        PaymentPlanService(payment_plan=payment_plan_base).get_approval_type_by_action()


def test_validate_action_not_implemented(payment_plan_base: PaymentPlan, user: User) -> None:
    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan_base).execute_update_status_action(
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
        "SEND_XLSX_PASSWORD",
    ]
    assert error.value.detail[0] == f"Not Implemented Action: INVALID_ACTION. List of possible actions: {actions}"


def test_tp_lock_invalid_pp_status(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.DRAFT,
    )
    with pytest.raises(TransitionNotAllowed) as error:
        PaymentPlanService(payment_plan).tp_lock()
    assert str(error.value) == 'Status_Tp_Lock :: no transition from "DRAFT"'


def test_tp_unlock(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.DRAFT,
    )
    with pytest.raises(TransitionNotAllowed) as error:
        PaymentPlanService(payment_plan).tp_unlock()
    assert str(error.value) == 'Status_Tp_Open :: no transition from "DRAFT"'

    payment_plan.status = PaymentPlan.Status.TP_LOCKED
    payment_plan.save()
    PaymentPlanService(payment_plan).tp_unlock()

    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.TP_OPEN
    assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_PENDING


def test_tp_rebuild(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.DRAFT,
        build_status=PaymentPlan.BuildStatus.BUILD_STATUS_FAILED,
    )
    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan).tp_rebuild()
    assert error.value.detail[0] == "Can only Rebuild Population for Locked or Open Population status"

    payment_plan.status = PaymentPlan.Status.TP_LOCKED
    payment_plan.save()
    PaymentPlanService(payment_plan).tp_rebuild()

    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.TP_LOCKED
    assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_PENDING


def test_draft_with_invalid_pp_status(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.TP_LOCKED,
    )
    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan).draft()
    assert "Can only promote to Payment Plan if DM/FSP is chosen." in str(error.value)

    payment_plan.status = PaymentPlan.Status.DRAFT
    payment_plan.financial_service_provider = fsp
    payment_plan.save()

    with pytest.raises(TransitionNotAllowed) as error:
        PaymentPlanService(payment_plan).draft()
    assert str(error.value) == 'Status_Draft :: no transition from "DRAFT"'


def test_lock_if_no_valid_payments(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.OPEN,
    )
    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan).lock()
    assert error.value.detail[0] == "At least one valid Payment should exist in order to Lock the Payment Plan"


def test_update_pp_validation_errors(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.LOCKED,
    )
    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan).update({"exclusion_reason": "ABC"})
    assert error.value.detail[0] == f"Not Allow edit targeting criteria within status {payment_plan.status}"

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan).update({"vulnerability_score_min": "test_data"})
    assert (
        error.value.detail[0]
        == "You can only set vulnerability_score_min and vulnerability_score_max on Locked Population status"
    )

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan).update({"currency": "test_data"})
    assert error.value.detail[0] == f"Not Allow edit Payment Plan within status {payment_plan.status}"

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan).update({"name": "test_data"})
    assert error.value.detail[0] == "Name can be changed only within Open status"

    payment_plan.status = PaymentPlan.Status.TP_OPEN
    payment_plan.save()
    PaymentPlanFactory(
        name="test_data",
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.DRAFT,
    )
    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan).update({"name": "test_data"})
    assert error.value.detail[0] == f"Name 'test_data' and program '{cycle.program.name}' already exists."

    cycle.status = ProgramCycle.FINISHED
    cycle.save()
    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan).update({"program_cycle_id": str(cycle.id)})
    assert error.value.detail[0] == "Not possible to assign Finished Program Cycle"


def test_rebuild_payment_plan_population(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    pp = PaymentPlanFactory(
        name="test_data",
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.TP_OPEN,
    )

    PaymentPlanService.rebuild_payment_plan_population(
        rebuild_list=False,
        should_update_money_stats=True,
        vulnerability_filter=False,
        payment_plan=pp,
    )
    PaymentPlanService.rebuild_payment_plan_population(
        rebuild_list=True,
        should_update_money_stats=False,
        vulnerability_filter=False,
        payment_plan=pp,
    )
    PaymentPlanService.rebuild_payment_plan_population(
        rebuild_list=False,
        should_update_money_stats=False,
        vulnerability_filter=True,
        payment_plan=pp,
    )

    pp.refresh_from_db(fields=("build_status",))
    assert pp.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK


def test_lock_fsp_validation(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.LOCKED,
    )
    payment = PaymentFactory(
        parent=payment_plan,
        program=cycle.program,
        business_area_id=payment_plan.business_area_id,
        status=Payment.STATUS_PENDING,
        financial_service_provider=None,
        entitlement_quantity=None,
        entitlement_quantity_usd=None,
        delivered_quantity=None,
        delivered_quantity_usd=None,
    )

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan).lock_fsp()
    assert error.value.detail[0] == "Payment Plan doesn't have FSP / DeliveryMechanism assigned."

    payment_plan.financial_service_provider = fsp
    payment_plan.delivery_mechanism = dm_transfer_to_account
    payment.save()

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan).lock_fsp()
    assert error.value.detail[0] == "All Payments must have entitlement quantity set."

    payment.entitlement_quantity = 100
    payment.save()

    PaymentPlanService(payment_plan).lock_fsp()
    payment.refresh_from_db()
    assert payment.financial_service_provider == fsp


def test_unlock_fsp(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.LOCKED_FSP,
    )

    PaymentPlanService(payment_plan).unlock_fsp()

    payment_plan.refresh_from_db(fields=("status",))
    assert payment_plan.status == PaymentPlan.Status.LOCKED


def test_update_pp_program_cycle(payment_plan_base: PaymentPlan, program: Program) -> None:
    new_cycle = ProgramCycleFactory(program=program, title="New Cycle ABC")

    PaymentPlanService(payment_plan_base).update({"program_cycle_id": new_cycle.id})

    payment_plan_base.refresh_from_db()
    assert payment_plan_base.program_cycle.title == "New Cycle ABC"


def test_update_pp_vulnerability_score(payment_plan_base: PaymentPlan) -> None:
    PaymentPlanService(payment_plan_base).update(
        {
            "vulnerability_score_min": "11.229222",
            "vulnerability_score_max": "77.889777",
        }
    )
    payment_plan_base.refresh_from_db(fields=("vulnerability_score_min", "vulnerability_score_max"))
    assert payment_plan_base.vulnerability_score_min == Decimal("11.229")
    assert payment_plan_base.vulnerability_score_max == Decimal("77.890")


def test_update_pp_exclude_ids(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.TP_OPEN,
    )
    PaymentPlanService(payment_plan).update({"excluded_ids": "IND-123", "exclusion_reason": "Test text"})
    payment_plan.refresh_from_db(fields=("excluded_ids", "exclusion_reason"))
    assert payment_plan.excluded_ids == "IND-123"
    assert payment_plan.exclusion_reason == "Test text"


def test_update_pp_currency(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    dm_transfer_to_account: Any,
    fsp: FinancialServiceProvider,
) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.OPEN,
        currency="AMD",
        delivery_mechanism=dm_transfer_to_account,
        financial_service_provider=fsp,
    )
    PaymentPlanService(payment_plan).update({"currency": "PLN"})
    payment_plan.refresh_from_db()
    assert payment_plan.currency == "PLN"


def test_update_pp_currency_validation(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    dm_transfer_to_digital_wallet: Any,
    fsp: FinancialServiceProvider,
) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.OPEN,
        currency="USDC",
        delivery_mechanism=dm_transfer_to_digital_wallet,
        financial_service_provider=fsp,
    )
    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan).update({"currency": "PLN"})
    assert (
        error.value.detail[0] == "For delivery mechanism Transfer to Digital Wallet only currency USDC can be assigned."
    )


def test_update_dispersion_end_date(user: User, business_area: Any, cycle: ProgramCycle) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.OPEN,
        currency="AMD",
    )
    new_end_date = timezone.now().date() + timedelta(days=3)
    PaymentPlanService(payment_plan).update({"dispersion_end_date": new_end_date})
    payment_plan.refresh_from_db()
    assert payment_plan.dispersion_end_date == new_end_date


def test_update_pp_dm_fsp(
    user: User,
    business_area: Any,
    cycle: ProgramCycle,
    fsp: FinancialServiceProvider,
    dm_transfer_to_account: Any,
    dm_transfer_to_digital_wallet: Any,
) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.TP_OPEN,
        currency="AMD",
        delivery_mechanism=None,
        financial_service_provider=None,
    )
    PaymentPlanService(payment_plan).update(
        {
            "fsp_id": str(fsp.id),
            "delivery_mechanism_code": dm_transfer_to_account.code,
        }
    )
    payment_plan.refresh_from_db()
    assert payment_plan.delivery_mechanism == dm_transfer_to_account
    assert payment_plan.financial_service_provider == fsp

    payment_plan.status = PaymentPlan.Status.OPEN
    payment_plan.save()

    PaymentPlanService(payment_plan).update(
        {
            "fsp_id": fsp.id,
            "delivery_mechanism_code": dm_transfer_to_digital_wallet.code,
        }
    )
    payment_plan.refresh_from_db()
    assert payment_plan.delivery_mechanism == dm_transfer_to_account
    assert payment_plan.financial_service_provider == fsp

    PaymentPlanService(payment_plan).update(
        {
            "fsp_id": None,
            "delivery_mechanism_code": None,
        }
    )
    payment_plan.refresh_from_db()
    assert payment_plan.delivery_mechanism == dm_transfer_to_account
    assert payment_plan.financial_service_provider == fsp


def test_export_xlsx(payment_plan_base: PaymentPlan, user) -> None:
    payment_plan_base.status = PaymentPlan.Status.LOCKED
    payment_plan_base.save()
    assert FileTemp.objects.all().count() == 0

    PaymentPlanService(payment_plan_base).export_xlsx(user.pk)

    assert FileTemp.objects.all().count() == 1
    assert FileTemp.objects.first().object_id == str(payment_plan_base.pk)


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
    payment_plan = PaymentPlanFactory(
        created_by=user,
        status=PaymentPlan.Status.PREPARING,
        business_area=business_area,
        program_cycle=cycle,
        delivery_mechanism=dm_transfer_to_account,
        financial_service_provider=fsp,
    )
    TargetingCriteriaRuleFactory(household_ids=f"{household.unicef_id}", payment_plan=payment_plan)

    PaymentFactory(
        parent=payment_plan,
        program=program,
        business_area_id=payment_plan.business_area_id,
        status=Payment.STATUS_PENDING,
        household=household,
        collector=household.head_of_household,
    )

    hh_qs = program.households_with_payments_in_program
    assert hh_qs.count() == 1
    assert hh_qs.first().unicef_id == household.unicef_id

    with transaction.atomic():
        with pytest.raises(IntegrityError) as error:
            PaymentPlanService.create_payments(payment_plan)
        assert 'duplicate key value violates unique constraint "payment_plan_and_household"' in str(error.value)

    with transaction.atomic():
        IndividualRoleInHousehold.objects.filter(household=household, role=ROLE_PRIMARY).delete()

        with pytest.raises(ValidationError) as error:
            PaymentPlanService.create_payments(payment_plan)
        assert f"Couldn't find a primary collector in {household.unicef_id}" in str(error.value)


def test_acceptance_process_validation_error(payment_plan_base: PaymentPlan) -> None:
    payment_plan_base.status = PaymentPlan.Status.PREPARING
    payment_plan_base.save()

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan=payment_plan_base).acceptance_process()

    assert f"Approval Process object not found for PaymentPlan {payment_plan_base.id}" in str(error.value)


def test_update_rules_tp_open(payment_plan_base: PaymentPlan) -> None:
    payment_plan_base.status = PaymentPlan.Status.TP_OPEN
    payment_plan_base.save()
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
    PaymentPlanService(payment_plan_base).update(input_data)
    payment_plan_base.refresh_from_db()
    assert payment_plan_base.rules.count() == 1
    assert payment_plan_base.flag_exclude_if_on_sanction_list
    assert not payment_plan_base.flag_exclude_if_active_adjudication_ticket


def test_send_reconciliation_overdue_emails() -> None:
    pp = PaymentPlanFactory(
        dispersion_start_date=now() - timedelta(days=10),
        dispersion_end_date=now(),
        status=PaymentPlan.Status.ACCEPTED,
    )
    pp.refresh_from_db()
    program = pp.program
    program.reconciliation_window_in_days = 10
    program.send_reconciliation_window_expiry_notifications = True
    program.save()

    PaymentFactory(parent=pp, status=Payment.STATUS_PENDING, delivered_quantity=None)
    assert pp.has_payments_reconciliation_overdue is True

    with mock.patch(
        "hope.apps.payment.services.payment_plan_services.send_payment_plan_reconciliation_overdue_email.delay"
    ) as mock_task:
        PaymentPlanService.send_reconciliation_overdue_emails()
        mock_task.assert_called_once_with(str(pp.id))


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

    pp = PaymentPlanFactory(
        dispersion_start_date=now() - timedelta(days=10),
        dispersion_end_date=now(),
        status=PaymentPlan.Status.ACCEPTED,
        business_area=business_area,
    )
    pp.refresh_from_db()
    program = pp.program
    program.reconciliation_window_in_days = 10
    program.send_reconciliation_window_expiry_notifications = True
    program.save()

    with mock.patch.object(User, "email_user") as mock_email_user:
        with mock.patch("hope.apps.payment.services.payment_plan_services.render_to_string") as mock_render_to_string:
            PaymentPlanService(pp).send_reconciliation_overdue_email_for_pp()
            mock_email_user.assert_called_once()
            assert mock_render_to_string.call_count == 2
            _args, kwargs = mock_render_to_string.call_args
            context = kwargs["context"]
            assert context["message"] == (
                f"Please be informed that Payment Plan: {pp.unicef_id} has exceeded its"
                f" reconciliation window of {pp.program.reconciliation_window_in_days} days."
                " Please take the necessary steps to complete the reconciliation process timely."
            )
            assert context["title"] == f"Payment Plan {pp.unicef_id} Reconciliation Overdue"
