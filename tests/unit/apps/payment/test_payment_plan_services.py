from datetime import timedelta
from decimal import Decimal
from typing import Any
from unittest import mock
from unittest.mock import patch

from aniso8601 import parse_date
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.timezone import now
from django_fsm import TransitionNotAllowed
from flaky import flaky
from freezegun import freeze_time
import pytest
from pytz import utc
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.household import (
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
    create_household_with_individual_with_collectors,
)
from extras.test_utils.factories.payment import (
    AccountFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanSplitFactory,
    generate_delivery_mechanisms,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.factories.targeting import TargetingCriteriaRuleFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.base_test_case import BaseTestCase
from hope.apps.payment.celery_tasks import (
    prepare_follow_up_payment_plan_task,
    prepare_payment_plan_task,
)
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.models.account_type import AccountType
from hope.models.delivery_mechanism import DeliveryMechanism
from hope.models.file_temp import FileTemp
from hope.models.financial_service_provider import FinancialServiceProvider
from hope.models.household import ROLE_PRIMARY
from hope.models.individual_role_in_household import IndividualRoleInHousehold
from hope.models.payment import Payment
from hope.models.payment_plan import PaymentPlan
from hope.models.payment_plan_split import PaymentPlanSplit
from hope.models.program import Program
from hope.models.program_cycle import ProgramCycle
from hope.models.role import Role
from hope.models.role_assignment import RoleAssignment
from hope.models.user import User


class TestPaymentPlanServices(BaseTestCase):
    databases = ("default",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        generate_delivery_mechanisms()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(
            cls.user,
            [Permissions.PM_CREATE],
            cls.business_area,
            whole_business_area_access=True,
        )
        cls.dm_transfer_to_account = DeliveryMechanism.objects.get(code="transfer_to_account")
        cls.dm_transfer_to_digital_wallet = DeliveryMechanism.objects.get(code="transfer_to_digital_wallet")
        cls.program = ProgramFactory(status=Program.ACTIVE)
        cls.cycle = cls.program.cycles.first()
        cls.fsp = FinancialServiceProviderFactory(
            name="Test FSP 1",
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        )
        cls.payment_plan = PaymentPlanFactory(
            program_cycle=cls.cycle,
            created_by=cls.user,
            status=PaymentPlan.Status.TP_LOCKED,
            delivery_mechanism=cls.dm_transfer_to_account,
            financial_service_provider=cls.fsp,
        )

    def test_delete_tp_open(self) -> None:
        program = ProgramFactory(status=Program.ACTIVE)
        pp: PaymentPlan = PaymentPlanFactory(
            status=PaymentPlan.Status.TP_OPEN,
            program_cycle=program.cycles.first(),
            created_by=self.user,
        )

        pp = PaymentPlanService(payment_plan=pp).delete()
        assert pp.is_removed is True
        assert pp.status == PaymentPlan.Status.TP_OPEN

    def test_delete_open(self) -> None:
        program = ProgramFactory(status=Program.ACTIVE)
        pp: PaymentPlan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
            program_cycle=program.cycles.first(),
            created_by=self.user,
        )

        pp = PaymentPlanService(payment_plan=pp).delete()
        assert pp.is_removed is False
        assert pp.status == PaymentPlan.Status.DRAFT

    def test_delete_locked(self) -> None:
        pp = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED, created_by=self.user)

        with pytest.raises(ValidationError) as e:
            PaymentPlanService(payment_plan=pp).delete()
        assert e.value.detail[0] == "Deletion is only allowed when the status is 'Open'"

    def test_delete_when_its_one_pp_in_cycle(self) -> None:
        program = ProgramFactory(status=Program.ACTIVE)
        pp: PaymentPlan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
            program_cycle=program.cycles.first(),
            created_by=self.user,
        )
        program_cycle = ProgramCycleFactory(status=ProgramCycle.ACTIVE, program=pp.program)
        pp.program_cycle = program_cycle
        pp.save()
        pp.refresh_from_db()

        assert pp.program_cycle.status == ProgramCycle.ACTIVE

        pp = PaymentPlanService(payment_plan=pp).delete()
        assert pp.is_removed is False
        assert pp.status == PaymentPlan.Status.DRAFT
        program_cycle.refresh_from_db()
        assert program_cycle.status == ProgramCycle.DRAFT

    def test_delete_when_its_two_pp_in_cycle(self) -> None:
        program = ProgramFactory(status=Program.ACTIVE)
        program_cycle = ProgramCycleFactory(status=ProgramCycle.ACTIVE, program=program)
        pp_1: PaymentPlan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
            program_cycle=program_cycle,
            created_by=self.user,
        )
        PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
            program_cycle=program_cycle,
            created_by=self.user,
        )

        assert pp_1.program_cycle.status == ProgramCycle.ACTIVE

        pp_1 = PaymentPlanService(payment_plan=pp_1).delete()
        assert pp_1.is_removed is False
        assert pp_1.status == PaymentPlan.Status.DRAFT
        program_cycle.refresh_from_db()
        assert program_cycle.status == ProgramCycle.ACTIVE

    @freeze_time("2020-10-10")
    def test_create_validation_errors(self) -> None:
        program = ProgramFactory(
            status=Program.ACTIVE,
            start_date=timezone.datetime(2019, 10, 12, tzinfo=utc).date(),
            end_date=timezone.datetime(2099, 12, 10, tzinfo=utc).date(),
            cycle__start_date=timezone.datetime(2021, 10, 10, tzinfo=utc).date(),
            cycle__end_date=timezone.datetime(2021, 12, 10, tzinfo=utc).date(),
        )
        program_cycle = program.cycles.first()
        household, individuals = create_household_and_individuals(
            household_data={
                "business_area": self.business_area,
                "program": program,
            },
            individuals_data=[{}],
        )
        create_input_data = {
            "program_cycle_id": str(program_cycle.id),
            "name": "TEST_123",
            "flag_exclude_if_active_adjudication_ticket": False,
            "flag_exclude_if_on_sanction_list": False,
            "rules": [
                {
                    "collectors_filters_blocks": [],
                    "household_filters_blocks": [],
                    "household_ids": f"{household.unicef_id}",
                    "individual_ids": "",
                    "individuals_filters_blocks": [],
                }
            ],
        }

        with self.assertRaisesMessage(
            ValidationError,
            f"Target Population with name: TEST_123 and program: {program.name} already exists.",
        ):
            PaymentPlanFactory(program_cycle=program_cycle, name="TEST_123", created_by=self.user)
            PaymentPlanService.create(
                input_data=create_input_data,
                user=self.user,
                business_area_slug=self.business_area.slug,
            )
        with self.assertRaisesMessage(
            ValidationError,
            "Impossible to create Target Population for Programme within not Active status",
        ):
            program.status = Program.FINISHED
            program.save()
            program.refresh_from_db()
            PaymentPlanService.create(
                input_data=create_input_data,
                user=self.user,
                business_area_slug=self.business_area.slug,
            )
        with self.assertRaisesMessage(
            ValidationError,
            "Impossible to create Target Population for Programme Cycle within Finished status",
        ):
            program_cycle.status = ProgramCycle.FINISHED
            program_cycle.save()
            PaymentPlanService.create(
                input_data=create_input_data,
                user=self.user,
                business_area_slug=self.business_area.slug,
            )
        program_cycle.status = ProgramCycle.ACTIVE
        program_cycle.save()
        program.status = Program.ACTIVE
        program.save()
        # create PP
        create_input_data["name"] = "TEST"
        pp = PaymentPlanService.create(
            input_data=create_input_data,
            user=self.user,
            business_area_slug=self.business_area.slug,
        )
        pp.status = PaymentPlan.Status.TP_OPEN
        pp.save()

        # check validation for Open PP
        open_input_data = {
            "dispersion_start_date": parse_date("2020-09-10"),
            "dispersion_end_date": parse_date("2020-09-11"),
            "currency": "USD",
        }
        with pytest.raises(TransitionNotAllowed) as e:
            PaymentPlanService(payment_plan=pp).open(input_data=open_input_data)
        assert str(e.value) == "Can't switch from state 'TP_OPEN' using method 'status_open'"

        pp.status = PaymentPlan.Status.DRAFT
        pp.save()
        with self.assertRaisesMessage(
            ValidationError,
            f"Dispersion End Date [{open_input_data['dispersion_end_date']}] cannot be a past date",
        ):
            PaymentPlanService(payment_plan=pp).open(input_data=open_input_data)
        open_input_data["dispersion_end_date"] = parse_date("2020-11-11")
        pp.refresh_from_db()
        assert pp.status == PaymentPlan.Status.DRAFT
        pp = PaymentPlanService(payment_plan=pp).open(input_data=open_input_data)
        pp.refresh_from_db()
        assert pp.status == PaymentPlan.Status.OPEN

    @freeze_time("2020-10-10")
    @mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_create(self, get_exchange_rate_mock: Any) -> None:
        program = ProgramFactory(
            status=Program.ACTIVE,
            start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
        )
        program_cycle = program.cycles.first()

        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        AccountFactory(
            individual=hoh1,
            account_type=AccountType.objects.get(key="bank"),
        )
        AccountFactory(
            individual=hoh1,
            account_type=AccountType.objects.get(key="bank"),
        )
        hh1 = HouseholdFactory(head_of_household=hoh1, program=program, business_area=self.business_area)
        hh2 = HouseholdFactory(head_of_household=hoh2, program=program, business_area=self.business_area)
        hoh1.household = hh1
        hoh1.save()
        hoh2.household = hh2
        hoh2.save()
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)

        input_data = {
            "business_area_slug": "afghanistan",
            "name": "paymentPlanName",
            "program_cycle_id": program_cycle.id,
            "flag_exclude_if_active_adjudication_ticket": False,
            "flag_exclude_if_on_sanction_list": False,
            "rules": [
                {
                    "collectors_filters_blocks": [],
                    "household_filters_blocks": [],
                    "household_ids": f"{hh1.unicef_id}, {hh2.unicef_id}",
                    "individual_ids": "",
                    "individuals_filters_blocks": [],
                }
            ],
            "fsp_id": self.fsp.id,
            "delivery_mechanism_code": self.dm_transfer_to_account.code,
        }

        with mock.patch(
            "hope.apps.payment.services.payment_plan_services.transaction"
        ) as mock_prepare_payment_plan_task:
            with self.assertNumQueries(16):
                pp = PaymentPlanService.create(
                    input_data=input_data,
                    user=self.user,
                    business_area_slug=self.business_area.slug,
                )
            assert mock_prepare_payment_plan_task.on_commit.call_count == 1

        assert pp.status == PaymentPlan.Status.TP_OPEN
        assert pp.total_households_count == 0
        assert pp.total_individuals_count == 0
        assert pp.payment_items.count() == 0
        with self.assertNumQueries(97):
            prepare_payment_plan_task.delay(str(pp.id))
        pp.refresh_from_db()
        assert pp.status == PaymentPlan.Status.TP_OPEN
        assert pp.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK
        assert pp.total_households_count == 2
        assert pp.total_individuals_count == 6
        assert pp.payment_items.count() == 2

    @freeze_time("2020-10-10")
    @mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_update_validation_errors(self, get_exchange_rate_mock: Any) -> None:
        pp = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED, created_by=self.user)

        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)

        input_data = {
            "dispersion_start_date": parse_date("2020-09-10"),
            "dispersion_end_date": parse_date("2020-09-11"),
            "currency": "USD",
        }

        with self.assertRaisesMessage(ValidationError, "Not Allow edit Payment Plan within status LOCKED"):
            pp = PaymentPlanService(payment_plan=pp).update(input_data=input_data)
        pp.status = PaymentPlan.Status.OPEN
        pp.save()

        with self.assertRaisesMessage(
            ValidationError,
            f"Dispersion End Date [{input_data['dispersion_end_date']}] cannot be a past date",
        ):
            PaymentPlanService(payment_plan=pp).update(input_data=input_data)

    @freeze_time("2023-10-10")
    @mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_create_follow_up_pp(self, get_exchange_rate_mock: Any) -> None:
        pp = PaymentPlanFactory(
            total_households_count=1,
            created_by=self.user,
        )
        program = pp.program_cycle.program
        payments = []
        for _ in range(5):
            hoh = IndividualFactory(household=None)
            hh = HouseholdFactory(head_of_household=hoh, program=program, business_area=self.business_area)
            IndividualRoleInHouseholdFactory(household=hh, individual=hoh, role=ROLE_PRIMARY)
            IndividualFactory.create_batch(2, household=hh)
            payment = PaymentFactory(
                parent=pp,
                household=hh,
                status=Payment.STATUS_DISTRIBUTION_SUCCESS,
                currency="PLN",
            )
            payments.append(payment)

        dispersion_start_date = pp.dispersion_start_date + timedelta(days=1)
        dispersion_end_date = pp.dispersion_end_date + timedelta(days=1)

        with self.assertRaisesMessage(
            ValidationError,
            "Cannot create a follow-up for a payment plan with no unsuccessful payments",
        ):
            PaymentPlanService(pp).create_follow_up(self.user, dispersion_start_date, dispersion_end_date)

        # create follow-up payments for
        # STATUS_ERROR, STATUS_NOT_DISTRIBUTED, STATUS_FORCE_FAILED, STATUS_MANUALLY_CANCELLED
        for payment, status in zip(payments[:4], Payment.FAILED_STATUSES, strict=True):
            payment.status = status
            payment.save()

        # do not create follow-up payments for withdrawn households
        payments[4].household.withdrawn = True
        payments[4].household.save()

        p_error = payments[0]
        p_not_distributed = payments[1]
        p_force_failed = payments[2]
        p_manually_cancelled = payments[3]

        with self.assertNumQueries(6):
            follow_up_pp = PaymentPlanService(pp).create_follow_up(
                self.user, dispersion_start_date, dispersion_end_date
            )

        follow_up_pp.refresh_from_db()
        assert follow_up_pp.status == PaymentPlan.Status.OPEN
        assert follow_up_pp.program == pp.program
        assert follow_up_pp.program_cycle == pp.program_cycle
        assert follow_up_pp.business_area == pp.business_area
        assert follow_up_pp.created_by == self.user
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

        # exclude one payment from follow up pp, create new follow up pp which covers this payment
        follow_up_payment.excluded = True
        follow_up_payment.save()

        with self.assertNumQueries(6):
            follow_up_pp_2 = PaymentPlanService(pp).create_follow_up(
                self.user, dispersion_start_date, dispersion_end_date
            )

        assert pp.follow_ups.count() == 2

        with self.assertNumQueries(46):
            prepare_follow_up_payment_plan_task(follow_up_pp_2.id)

        assert follow_up_pp_2.payment_items.count() == 1
        assert {follow_up_payment.source_payment.id} == set(
            follow_up_pp_2.payment_items.values_list("source_payment_id", flat=True)
        )

    def test_create_follow_up_pp_from_follow_up_validation(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.FINISHED,
            is_follow_up=True,
        )
        dispersion_start_date = payment_plan.dispersion_start_date + timedelta(days=1)
        dispersion_end_date = payment_plan.dispersion_end_date + timedelta(days=1)
        with pytest.raises(ValidationError) as e:
            PaymentPlanService(payment_plan).create_follow_up(self.user, dispersion_start_date, dispersion_end_date)
        assert e.value.detail[0] == "Cannot create a follow-up of a follow-up Payment Plan"

    def test_update_follow_up_dates_and_not_currency(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
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

    @flaky(max_runs=5, min_passes=1)
    @freeze_time("2023-10-10")
    @mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
    @patch("hope.models.payment_plan_split.PaymentPlanSplit.MIN_NO_OF_PAYMENTS_IN_CHUNK")
    def test_split(self, min_no_of_payments_in_chunk_mock: Any, get_exchange_rate_mock: Any) -> None:
        min_no_of_payments_in_chunk_mock.__get__ = mock.Mock(return_value=2)

        pp = PaymentPlanFactory(created_by=self.user)

        with self.assertRaisesMessage(ValidationError, "No payments to split"):
            PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_COLLECTOR)

        payments = []
        # 2 payments with the same collector
        # 2 payments with the same admin area 2
        # 2 other payments
        collector = IndividualFactory(household=None)
        for _ in range(3):
            hoh = IndividualFactory(household=None)
            hh = HouseholdFactory(head_of_household=hoh)
            IndividualRoleInHouseholdFactory(household=hh, individual=hoh, role=ROLE_PRIMARY)
            IndividualFactory.create_batch(2, household=hh)
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
            collector = IndividualFactory(household=None)
            hoh = IndividualFactory(household=None)
            hh = HouseholdFactory(head_of_household=hoh, admin2=area2)
            IndividualRoleInHouseholdFactory(household=hh, individual=hoh, role=ROLE_PRIMARY)
            IndividualFactory.create_batch(2, household=hh)
            payment = PaymentFactory(
                parent=pp,
                household=hh,
                status=Payment.STATUS_DISTRIBUTION_SUCCESS,
                currency="PLN",
                collector=collector,
            )
            payments.append(payment)

        for _ in range(5):
            collector = IndividualFactory(household=None)
            hoh = IndividualFactory(household=None)
            hh = HouseholdFactory(head_of_household=hoh)
            IndividualRoleInHouseholdFactory(household=hh, individual=hoh, role=ROLE_PRIMARY)
            IndividualFactory.create_batch(2, household=hh)
            payment = PaymentFactory(
                parent=pp,
                household=hh,
                status=Payment.STATUS_DISTRIBUTION_SUCCESS,
                currency="PLN",
                collector=collector,
            )
            payments.append(payment)

        with self.assertRaisesMessage(ValidationError, "Payments Number is required for split by records"):
            PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_RECORDS, chunks_no=None)

        with self.assertRaisesMessage(
            ValidationError,
            "Payment Parts number should be between 2 and total number of payments",
        ):
            PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_RECORDS, chunks_no=669)

        with mock.patch(
            "hope.apps.payment.services.payment_plan_services.PaymentPlanSplit.MAX_CHUNKS"
        ) as max_chunks_patch:
            max_chunks_patch.__get__ = mock.Mock(return_value=2)
            with self.assertRaisesMessage(ValidationError, "Too many Payment Parts to split: 6, maximum is 2"):
                PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_RECORDS, chunks_no=2)

        # split by collector
        with self.assertNumQueries(26):
            PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_COLLECTOR)
        unique_collectors_count = pp.eligible_payments.values_list("collector", flat=True).distinct().count()
        assert unique_collectors_count == 10
        pp_splits = pp.splits.all().order_by("order")

        assert pp_splits.count() == unique_collectors_count
        assert pp_splits[0].split_type == PaymentPlanSplit.SplitType.BY_COLLECTOR
        assert pp_splits[0].split_payment_items.count() == 3
        assert pp_splits[1].split_payment_items.count() == 1
        assert pp_splits[2].split_payment_items.count() == 1
        assert pp_splits[3].split_payment_items.count() == 1
        assert pp_splits[4].split_payment_items.count() == 1
        assert pp_splits[5].split_payment_items.count() == 1
        assert pp_splits[6].split_payment_items.count() == 1
        assert pp_splits[7].split_payment_items.count() == 1
        assert pp_splits[8].split_payment_items.count() == 1
        assert pp_splits[9].split_payment_items.count() == 1

        # split by records
        with self.assertNumQueries(17):
            PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_RECORDS, chunks_no=5)
        pp_splits = pp.splits.all().order_by("order")
        assert pp_splits.count() == 3
        assert pp_splits[0].split_type == PaymentPlanSplit.SplitType.BY_RECORDS
        assert pp_splits[0].split_payment_items.count() == 5
        assert pp_splits[1].split_payment_items.count() == 5
        assert pp_splits[2].split_payment_items.count() == 2

        # split by admin2
        with self.assertNumQueries(15):
            PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_ADMIN_AREA2)
        unique_admin2_count = pp.eligible_payments.values_list("household__admin2", flat=True).distinct().count()
        assert unique_admin2_count == 2
        pp_splits = pp.splits.all().order_by("order")
        assert pp.splits.count() == unique_admin2_count
        assert pp_splits[0].split_type == PaymentPlanSplit.SplitType.BY_ADMIN_AREA2
        assert pp_splits[0].split_payment_items.count() == 4
        assert pp_splits[1].split_payment_items.count() == 8

        # split by no_split
        PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.NO_SPLIT)
        pp_splits = pp.splits.all().order_by("order")
        assert pp.splits.count() == 1
        assert pp_splits[0].split_type == PaymentPlanSplit.SplitType.NO_SPLIT
        assert pp_splits[0].split_payment_items.count() == 12

    @freeze_time("2023-10-10")
    @mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_send_to_payment_gateway(self, get_exchange_rate_mock: Any) -> None:
        pg_fsp = FinancialServiceProviderFactory(
            name="Western Union",
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            payment_gateway_id="123",
        )
        pg_fsp.delivery_mechanisms.add(self.dm_transfer_to_account)
        pp = PaymentPlanFactory(
            status=PaymentPlan.Status.ACCEPTED,
            created_by=self.user,
            financial_service_provider=pg_fsp,
            delivery_mechanism=self.dm_transfer_to_account,
        )
        pp.background_action_status_send_to_payment_gateway()
        pp.save()
        with self.assertRaisesMessage(ValidationError, "Sending in progress"):
            PaymentPlanService(pp).send_to_payment_gateway()

        pp.background_action_status_none()
        pp.save()

        split = PaymentPlanSplitFactory(payment_plan=pp, sent_to_payment_gateway=True)

        with self.assertRaisesMessage(ValidationError, "Already sent to Payment Gateway"):
            PaymentPlanService(pp).send_to_payment_gateway()

        split.sent_to_payment_gateway = False
        split.save()
        with mock.patch(
            "hope.apps.payment.services.payment_plan_services.send_to_payment_gateway.delay"
        ) as mock_send_to_payment_gateway_task:
            pps = PaymentPlanService(pp)
            pps.user = mock.MagicMock(pk="123")
            pps.send_to_payment_gateway()
            assert mock_send_to_payment_gateway_task.call_count == 1

    @freeze_time("2020-10-10")
    def test_create_with_program_cycle_validation_error(self) -> None:
        program = ProgramFactory(
            status=Program.ACTIVE,
            start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
            cycle__start_date=timezone.datetime(2021, 10, 10, tzinfo=utc).date(),
            cycle__end_date=timezone.datetime(2021, 12, 10, tzinfo=utc).date(),
        )
        cycle = program.cycles.first()
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
                    "collectors_filters_blocks": [
                        {
                            "comparison_method": "EQUALS",
                            "arguments": ["No"],
                            "field_name": "mobile_phone_number__cash_over_the_counter",
                            "flex_field_classification": "NOT_FLEX_FIELD",
                        },
                    ],
                    "household_filters_blocks": [],
                    "household_ids": "",
                    "individual_ids": "",
                    "individuals_filters_blocks": [],
                }
            ],
        }

        with self.assertRaisesMessage(
            ValidationError,
            "Impossible to create Target Population for Programme Cycle within Finished status",
        ):
            cycle.status = ProgramCycle.FINISHED
            cycle.save()
            PaymentPlanService.create(
                input_data=input_data,
                user=self.user,
                business_area_slug=self.business_area.slug,
            )

        cycle.status = ProgramCycle.DRAFT
        cycle.end_date = None
        cycle.save()
        PaymentPlanService.create(
            input_data=input_data,
            user=self.user,
            business_area_slug=self.business_area.slug,
        )
        cycle.refresh_from_db()
        # open PP will update cycle' status into Active
        assert cycle.status == ProgramCycle.DRAFT

    @freeze_time("2022-12-12")
    @mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_full_rebuild(self, get_exchange_rate_mock: Any) -> None:
        program = ProgramFactory(
            status=Program.ACTIVE,
            start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
        )
        program_cycle = program.cycles.first()

        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1, program=program, business_area=self.business_area)
        hh2 = HouseholdFactory(head_of_household=hoh2, program=program, business_area=self.business_area)
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)

        input_data = {
            "business_area_slug": "afghanistan",
            "name": "paymentPlanName",
            "program_cycle_id": program_cycle.id,
            "flag_exclude_if_active_adjudication_ticket": False,
            "flag_exclude_if_on_sanction_list": False,
            "rules": [
                {
                    "collectors_filters_blocks": [],
                    "household_filters_blocks": [],
                    "household_ids": f"{hh1.unicef_id}, {hh2.unicef_id}",
                    "individual_ids": "",
                    "individuals_filters_blocks": [],
                }
            ],
        }
        with mock.patch(
            "hope.apps.payment.services.payment_plan_services.transaction"
        ) as mock_prepare_payment_plan_task:
            with self.assertNumQueries(12):
                pp = PaymentPlanService.create(
                    input_data=input_data,
                    user=self.user,
                    business_area_slug=self.business_area.slug,
                )
            assert mock_prepare_payment_plan_task.on_commit.call_count == 1

        assert pp.status == PaymentPlan.Status.TP_OPEN
        assert pp.total_households_count == 0
        assert pp.total_individuals_count == 0
        assert pp.payment_items.count() == 0
        with self.assertNumQueries(70):
            prepare_payment_plan_task.delay(str(pp.id))
        pp.refresh_from_db()
        assert pp.status == PaymentPlan.Status.TP_OPEN
        assert pp.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK
        assert pp.payment_items.count() == 2

        old_payment_ids = list(pp.payment_items.values_list("id", flat=True))
        old_payment_unicef_ids = list(pp.payment_items.values_list("unicef_id", flat=True))

        # check rebuild
        pp_service = PaymentPlanService(payment_plan=pp)
        pp_service.full_rebuild()

        pp.refresh_from_db()
        # all Payments (removed and new)
        assert Payment.all_objects.filter(parent=pp).count() == 2

        new_payment_ids = list(pp.payment_items.values_list("id", flat=True))
        new_payment_unicef_ids = list(pp.payment_items.values_list("unicef_id", flat=True))

        for p_id in new_payment_ids:
            assert p_id not in old_payment_ids

        for p_unicef_id in new_payment_unicef_ids:
            assert p_unicef_id not in old_payment_unicef_ids

    def test_get_approval_type_by_action_value_error(self) -> None:
        with pytest.raises(ValueError, match="Action cannot be None"):
            PaymentPlanService(payment_plan=self.payment_plan).get_approval_type_by_action()

    def test_validate_action_not_implemented(self) -> None:
        with pytest.raises(ValidationError) as e:
            PaymentPlanService(self.payment_plan).execute_update_status_action(
                input_data={"action": "INVALID_ACTION"}, user=self.user
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
        assert e.value.detail[0] == f"Not Implemented Action: INVALID_ACTION. List of possible actions: {actions}"

    def test_tp_lock_invalid_pp_status(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.DRAFT,
        )
        with pytest.raises(TransitionNotAllowed) as e:
            PaymentPlanService(payment_plan).tp_lock()
        assert str(e.value) == "Can't switch from state 'DRAFT' using method 'status_tp_lock'"

    def test_tp_unlock(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.DRAFT,
        )
        with pytest.raises(TransitionNotAllowed) as e:
            PaymentPlanService(payment_plan).tp_unlock()
        assert str(e.value) == "Can't switch from state 'DRAFT' using method 'status_tp_open'"
        payment_plan.status = PaymentPlan.Status.TP_LOCKED
        payment_plan.save()
        PaymentPlanService(payment_plan).tp_unlock()

        payment_plan.refresh_from_db()
        assert payment_plan.status == PaymentPlan.Status.TP_OPEN
        assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_PENDING

    def test_tp_rebuild(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.DRAFT,
            build_status=PaymentPlan.BuildStatus.BUILD_STATUS_FAILED,
        )
        with pytest.raises(ValidationError) as e:
            PaymentPlanService(payment_plan).tp_rebuild()
        assert e.value.detail[0] == "Can only Rebuild Population for Locked or Open Population status"
        payment_plan.status = PaymentPlan.Status.TP_LOCKED
        payment_plan.save()
        PaymentPlanService(payment_plan).tp_rebuild()

        payment_plan.refresh_from_db()
        assert payment_plan.status == PaymentPlan.Status.TP_LOCKED
        assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_PENDING

    def test_draft_with_invalid_pp_status(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.TP_LOCKED,
        )
        with pytest.raises(ValidationError) as e:
            PaymentPlanService(payment_plan).draft()
        assert "Can only promote to Payment Plan if DM/FSP is chosen." in str(e.value)

        payment_plan.status = PaymentPlan.Status.DRAFT
        payment_plan.financial_service_provider = self.fsp
        payment_plan.save()

        with pytest.raises(TransitionNotAllowed) as e:
            PaymentPlanService(payment_plan).draft()
        assert str(e.value) == "Can't switch from state 'DRAFT' using method 'status_draft'"

    def test_lock_if_no_valid_payments(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.OPEN,
        )
        with pytest.raises(ValidationError) as e:
            PaymentPlanService(payment_plan).lock()
        assert e.value.detail[0] == "At least one valid Payment should exist in order to Lock the Payment Plan"

    def test_update_pp_validation_errors(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.LOCKED,
        )
        with pytest.raises(ValidationError) as e:
            PaymentPlanService(payment_plan).update({"exclusion_reason": "ABC"})
        assert e.value.detail[0] == f"Not Allow edit targeting criteria within status {payment_plan.status}"

        with pytest.raises(ValidationError) as e:
            PaymentPlanService(payment_plan).update({"vulnerability_score_min": "test_data"})
        assert (
            e.value.detail[0]
            == "You can only set vulnerability_score_min and vulnerability_score_max on Locked Population status"
        )

        with pytest.raises(ValidationError) as e:
            PaymentPlanService(payment_plan).update({"currency": "test_data"})
        assert e.value.detail[0] == f"Not Allow edit Payment Plan within status {payment_plan.status}"

        with pytest.raises(ValidationError) as e:
            PaymentPlanService(payment_plan).update({"name": "test_data"})
        assert e.value.detail[0] == "Name can be changed only within Open status"

        payment_plan.status = PaymentPlan.Status.TP_OPEN
        payment_plan.save()
        PaymentPlanFactory(
            name="test_data",
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.DRAFT,
        )
        with pytest.raises(ValidationError) as e:
            PaymentPlanService(payment_plan).update({"name": "test_data"})
        assert e.value.detail[0] == f"Name 'test_data' and program '{self.cycle.program.name}' already exists."

        self.cycle.status = ProgramCycle.FINISHED
        self.cycle.save()
        with pytest.raises(ValidationError) as e:
            PaymentPlanService(payment_plan).update({"program_cycle_id": str(self.cycle.id)})
        assert e.value.detail[0] == "Not possible to assign Finished Program Cycle"

    def test_rebuild_payment_plan_population(self) -> None:
        pp = PaymentPlanFactory(
            name="test_data",
            program_cycle=self.cycle,
            created_by=self.user,
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

        self.payment_plan.refresh_from_db(fields=("build_status",))
        assert pp.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_PENDING

    def test_lock_fsp_validation(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.LOCKED,
        )
        payment = PaymentFactory(
            parent=payment_plan,
            program_id=self.program.id,
            business_area_id=payment_plan.business_area_id,
            status=Payment.PENDING_STATUSES,
            financial_service_provider=None,
            entitlement_quantity=None,
            entitlement_quantity_usd=None,
            delivered_quantity=None,
            delivered_quantity_usd=None,
        )

        with pytest.raises(ValidationError) as e:
            PaymentPlanService(payment_plan).lock_fsp()
        assert e.value.detail[0] == "Payment Plan doesn't have FSP / DeliveryMechanism assigned."
        payment_plan.financial_service_provider = self.fsp
        payment_plan.delivery_mechanism = self.dm_transfer_to_account
        payment.save()

        with pytest.raises(ValidationError) as e:
            PaymentPlanService(payment_plan).lock_fsp()
        assert e.value.detail[0] == "All Payments must have entitlement quantity set."
        payment.entitlement_quantity = 100
        payment.save()

        PaymentPlanService(payment_plan).lock_fsp()
        payment.refresh_from_db()
        assert payment.financial_service_provider == self.fsp

    def test_unlock_fsp(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.LOCKED_FSP,
        )

        PaymentPlanService(payment_plan).unlock_fsp()

        payment_plan.refresh_from_db(fields=("status",))
        assert payment_plan.status == PaymentPlan.Status.LOCKED

    def test_update_pp_program_cycle(self) -> None:
        new_cycle = ProgramCycleFactory(program=self.program, title="New Cycle ABC")

        PaymentPlanService(self.payment_plan).update({"program_cycle_id": new_cycle.id})

        self.payment_plan.refresh_from_db()
        assert self.payment_plan.program_cycle.title == "New Cycle ABC"

    def test_update_pp_vulnerability_score(self) -> None:
        PaymentPlanService(self.payment_plan).update(
            {
                "vulnerability_score_min": "11.229222",
                "vulnerability_score_max": "77.889777",
            }
        )
        self.payment_plan.refresh_from_db(fields=("vulnerability_score_min", "vulnerability_score_max"))
        assert self.payment_plan.vulnerability_score_min == Decimal("11.229")
        assert self.payment_plan.vulnerability_score_max == Decimal("77.890")

    def test_update_pp_exclude_ids(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.TP_OPEN,
        )
        PaymentPlanService(payment_plan).update({"excluded_ids": "IND-123", "exclusion_reason": "Test text"})
        payment_plan.refresh_from_db(fields=("excluded_ids", "exclusion_reason"))
        assert payment_plan.excluded_ids == "IND-123"
        assert payment_plan.exclusion_reason == "Test text"

    def test_update_pp_currency(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.OPEN,
            currency="AMD",
            delivery_mechanism=self.dm_transfer_to_account,
            financial_service_provider=self.fsp,
        )
        PaymentPlanService(payment_plan).update({"currency": "PLN"})
        payment_plan.refresh_from_db()
        assert payment_plan.currency == "PLN"

    def test_update_pp_currency_validation(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.OPEN,
            currency="USDC",
            delivery_mechanism=self.dm_transfer_to_digital_wallet,
            financial_service_provider=self.fsp,
        )
        with self.assertRaisesMessage(
            ValidationError,
            "For delivery mechanism Transfer to Digital Wallet only currency USDC can be assigned.",
        ):
            PaymentPlanService(payment_plan).update({"currency": "PLN"})

    def test_update_dispersion_end_date(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.OPEN,
            currency="AMD",
        )
        PaymentPlanService(payment_plan).update({"dispersion_end_date": timezone.now().date() + timedelta(days=3)})
        payment_plan.refresh_from_db()
        assert payment_plan.dispersion_end_date == timezone.now().date() + timedelta(days=3)

    def test_update_pp_dm_fsp(self) -> None:
        # allow changing dm/dsp on a TP PP stage
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.TP_OPEN,
            currency="AMD",
            delivery_mechanism=None,
            financial_service_provider=None,
        )
        PaymentPlanService(payment_plan).update(
            {
                "fsp_id": str(self.fsp.id),
                "delivery_mechanism_code": self.dm_transfer_to_account.code,
            }
        )
        payment_plan.refresh_from_db()
        assert payment_plan.delivery_mechanism == self.dm_transfer_to_account
        assert payment_plan.financial_service_provider == self.fsp

        # do not allow changing dm/dsp on a promoted PP stage
        payment_plan.status = PaymentPlan.Status.OPEN
        payment_plan.save()

        PaymentPlanService(payment_plan).update(
            {
                "fsp_id": self.fsp.id,
                "delivery_mechanism_code": self.dm_transfer_to_digital_wallet.code,
            }
        )
        payment_plan.refresh_from_db()
        assert payment_plan.delivery_mechanism == self.dm_transfer_to_account
        assert payment_plan.financial_service_provider == self.fsp

        PaymentPlanService(payment_plan).update(
            {
                "fsp_id": None,
                "delivery_mechanism_code": None,
            }
        )
        payment_plan.refresh_from_db()
        assert payment_plan.delivery_mechanism == self.dm_transfer_to_account
        assert payment_plan.financial_service_provider == self.fsp

    def test_export_xlsx(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.LOCKED,
        )
        assert FileTemp.objects.all().count() == 0

        PaymentPlanService(payment_plan).export_xlsx(self.user.pk)

        assert FileTemp.objects.all().count() == 1
        assert FileTemp.objects.first().object_id == str(payment_plan.pk)

    def test_create_payments_integrity_error_handling(self) -> None:
        household, individuals = create_household_with_individual_with_collectors(
            household_args={
                "business_area": self.business_area,
                "program": self.program,
            },
        )
        payment_plan = PaymentPlanFactory(
            created_by=self.user,
            status=PaymentPlan.Status.PREPARING,
            business_area=self.business_area,
            program_cycle=self.cycle,
            delivery_mechanism=self.dm_transfer_to_account,
            financial_service_provider=self.fsp,
        )
        TargetingCriteriaRuleFactory(household_ids=f"{household.unicef_id}", payment_plan=payment_plan)

        PaymentFactory(
            parent=payment_plan,
            program_id=self.program.id,
            business_area_id=payment_plan.business_area_id,
            status=Payment.PENDING_STATUSES,
            household_id=household.pk,
            collector_id=individuals[0].pk,
        )

        # check households with payments in program
        hh_qs = self.program.households_with_payments_in_program
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

    def test_acceptance_process_validation_error(self) -> None:
        payment_plan = PaymentPlanFactory(
            created_by=self.user,
            status=PaymentPlan.Status.PREPARING,
            business_area=self.business_area,
            program_cycle=self.cycle,
        )
        with pytest.raises(ValidationError) as error:
            PaymentPlanService(payment_plan=payment_plan).acceptance_process()

        assert f"Approval Process object not found for PaymentPlan {payment_plan.id}" in str(error.value)

    def test_update_rules_tp_open(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.TP_OPEN,
        )
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
                    "collectors_filters_blocks": [],
                }
            ],
            "flag_exclude_if_on_sanction_list": True,
            "flag_exclude_if_active_adjudication_ticket": False,
        }
        # Should not raise ValidationError
        PaymentPlanService(payment_plan).update(input_data)
        payment_plan.refresh_from_db()
        # Check that rules were updated
        assert payment_plan.rules.count() == 1
        # Check flags
        assert payment_plan.flag_exclude_if_on_sanction_list
        assert not payment_plan.flag_exclude_if_active_adjudication_ticket

    def test_send_reconciliation_overdue_emails(self) -> None:
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
        ) as mock_send_payment_plan_reconciliation_overdue_email_task:
            PaymentPlanService.send_reconciliation_overdue_emails()
            mock_send_payment_plan_reconciliation_overdue_email_task.assert_called_once_with(str(pp.id))

    def test_send_reconciliation_overdue_email(self) -> None:
        partner_unicef = PartnerFactory(name="UNICEF")
        partner_unicef_hq = PartnerFactory(name="UNICEF HQ", parent=partner_unicef)
        user = UserFactory.create(partner=partner_unicef_hq)
        role, _ = Role.objects.update_or_create(
            name="RECEIVE_PP_OVERDUE_EMAIL", defaults={"permissions": [Permissions.RECEIVE_PP_OVERDUE_EMAIL.value]}
        )
        RoleAssignment.objects.create(
            user=user,
            role=role,
            business_area=self.business_area,
        )

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

        with mock.patch.object(User, "email_user") as mock_email_user:
            with mock.patch(
                "hope.apps.payment.services.payment_plan_services.render_to_string"
            ) as mock_render_to_string:
                PaymentPlanService(pp).send_reconciliation_overdue_email_for_pp()
                mock_email_user.assert_called_once()
                assert mock_render_to_string.call_count == 2
                args, kwargs = mock_render_to_string.call_args
                context = kwargs["context"]
                assert context["message"] == (
                    f"Please be informed that Payment Plan: {pp.unicef_id} has exceeded its"
                    f" reconciliation window of {pp.program.reconciliation_window_in_days} days."
                    " Please take the necessary steps to complete the reconciliation process timely."
                )
                assert context["title"] == f"Payment Plan {pp.unicef_id} Reconciliation Overdue"
