from datetime import timedelta
from decimal import Decimal
from typing import Any
from unittest import mock
from unittest.mock import patch

from django.db import IntegrityError
from django.utils import timezone

from aniso8601 import parse_date
from flaky import flaky
from freezegun import freeze_time
from graphql import GraphQLError
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.household.fixtures import (
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
    create_household_with_individual_with_collectors,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.payment.celery_tasks import (
    prepare_follow_up_payment_plan_task,
    prepare_payment_plan_task,
)
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismPerPaymentPlanFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    FinancialServiceProvider,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
)
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetingCriteriaRuleFactory,
)


class TestPaymentPlanServices(APITestCase):
    databases = ("default",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        generate_delivery_mechanisms()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(cls.user, [Permissions.PM_CREATE], cls.business_area)
        cls.dm_transfer_to_account = DeliveryMechanism.objects.get(code="transfer_to_account")
        cls.program = ProgramFactory(status=Program.ACTIVE)
        cls.cycle = cls.program.cycles.first()

        cls.payment_plan = PaymentPlanFactory(
            program_cycle=cls.cycle, created_by=cls.user, status=PaymentPlan.Status.TP_LOCKED
        )

    def test_delete_tp_open(self) -> None:
        program = ProgramFactory(status=Program.ACTIVE)
        pp: PaymentPlan = PaymentPlanFactory(
            status=PaymentPlan.Status.TP_OPEN, program_cycle=program.cycles.first(), created_by=self.user
        )

        pp = PaymentPlanService(payment_plan=pp).delete()
        self.assertEqual(pp.is_removed, True)
        self.assertEqual(pp.status, PaymentPlan.Status.TP_OPEN)

    def test_delete_open(self) -> None:
        program = ProgramFactory(status=Program.ACTIVE)
        pp: PaymentPlan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN, program_cycle=program.cycles.first(), created_by=self.user
        )

        pp = PaymentPlanService(payment_plan=pp).delete()
        self.assertEqual(pp.is_removed, False)
        self.assertEqual(pp.status, PaymentPlan.Status.DRAFT)

    def test_delete_locked(self) -> None:
        pp = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED, created_by=self.user)

        with self.assertRaises(GraphQLError) as e:
            PaymentPlanService(payment_plan=pp).delete()
        self.assertEqual(
            e.exception.message,
            "Deletion is only allowed when the status is 'Open'",
        )

    def test_delete_when_its_one_pp_in_cycle(self) -> None:
        program = ProgramFactory(status=Program.ACTIVE)
        pp: PaymentPlan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN, program_cycle=program.cycles.first(), created_by=self.user
        )
        program_cycle = ProgramCycleFactory(status=ProgramCycle.ACTIVE, program=pp.program)
        pp.program_cycle = program_cycle
        pp.save()
        pp.refresh_from_db()

        self.assertEqual(pp.program_cycle.status, ProgramCycle.ACTIVE)

        pp = PaymentPlanService(payment_plan=pp).delete()
        self.assertEqual(pp.is_removed, False)
        self.assertEqual(pp.status, PaymentPlan.Status.DRAFT)
        program_cycle.refresh_from_db()
        self.assertEqual(program_cycle.status, ProgramCycle.DRAFT)

    def test_delete_when_its_two_pp_in_cycle(self) -> None:
        program = ProgramFactory(status=Program.ACTIVE)
        program_cycle = ProgramCycleFactory(status=ProgramCycle.ACTIVE, program=program)
        pp_1: PaymentPlan = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN, program_cycle=program_cycle, created_by=self.user
        )
        PaymentPlanFactory(status=PaymentPlan.Status.OPEN, program_cycle=program_cycle, created_by=self.user)

        self.assertEqual(pp_1.program_cycle.status, ProgramCycle.ACTIVE)

        pp_1 = PaymentPlanService(payment_plan=pp_1).delete()
        self.assertEqual(pp_1.is_removed, False)
        self.assertEqual(pp_1.status, PaymentPlan.Status.DRAFT)
        program_cycle.refresh_from_db()
        self.assertEqual(program_cycle.status, ProgramCycle.ACTIVE)

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
        create_input_data = dict(
            program_cycle_id=self.id_to_base64(str(program_cycle.id), "ProgramCycle"),
            name="TEST_123",
            targeting_criteria={
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
            },
        )

        with self.assertRaisesMessage(GraphQLError, "PaymentPlan can not be created in provided Business Area"):
            PaymentPlanService.create(
                input_data=create_input_data, user=self.user, business_area_slug=self.business_area.slug
            )
        self.business_area.is_payment_plan_applicable = True
        self.business_area.save()

        with self.assertRaisesMessage(
            GraphQLError, f"Payment Plan with name: TEST_123 and program: {program.name} already exists."
        ):
            PaymentPlanFactory(program_cycle=program_cycle, name="TEST_123", created_by=self.user)
            PaymentPlanService.create(
                input_data=create_input_data, user=self.user, business_area_slug=self.business_area.slug
            )
        with self.assertRaisesMessage(
            GraphQLError, "Impossible to create Payment Plan for Programme within not Active status"
        ):
            program.status = Program.FINISHED
            program.save()
            program.refresh_from_db()
            PaymentPlanService.create(
                input_data=create_input_data, user=self.user, business_area_slug=self.business_area.slug
            )
        with self.assertRaisesMessage(
            GraphQLError, "Impossible to create Payment Plan for Programme Cycle within Finished status"
        ):
            program_cycle.status = ProgramCycle.FINISHED
            program_cycle.save()
            PaymentPlanService.create(
                input_data=create_input_data, user=self.user, business_area_slug=self.business_area.slug
            )
        program_cycle.status = ProgramCycle.ACTIVE
        program_cycle.save()
        program.status = Program.ACTIVE
        program.save()
        # create PP
        create_input_data["name"] = "TEST"
        pp = PaymentPlanService.create(
            input_data=create_input_data, user=self.user, business_area_slug=self.business_area.slug
        )
        pp.status = PaymentPlan.Status.TP_OPEN
        pp.save()

        # check validation for Open PP
        open_input_data = dict(
            dispersion_start_date=parse_date("2020-09-10"),
            dispersion_end_date=parse_date("2020-09-11"),
            currency="USD",
        )
        with self.assertRaisesMessage(GraphQLError, "Can only move from Draft status to Open"):
            PaymentPlanService(payment_plan=pp).open(input_data=open_input_data)

        pp.status = PaymentPlan.Status.DRAFT
        pp.save()
        with self.assertRaisesMessage(
            GraphQLError, f"Dispersion End Date [{open_input_data['dispersion_end_date']}] cannot be a past date"
        ):
            PaymentPlanService(payment_plan=pp).open(input_data=open_input_data)
        open_input_data["dispersion_end_date"] = parse_date("2020-11-11")
        pp = PaymentPlanService(payment_plan=pp).open(input_data=open_input_data)
        pp.refresh_from_db()
        self.assertEqual(pp.status, PaymentPlan.Status.OPEN)

    @freeze_time("2020-10-10")
    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_create(self, get_exchange_rate_mock: Any) -> None:
        program = ProgramFactory(
            status=Program.ACTIVE,
            start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
        )
        program_cycle = program.cycles.first()

        self.business_area.is_payment_plan_applicable = True
        self.business_area.save()

        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1, program=program, business_area=self.business_area)
        hh2 = HouseholdFactory(head_of_household=hoh2, program=program, business_area=self.business_area)
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)

        input_data = dict(
            business_area_slug="afghanistan",
            name="paymentPlanName",
            program_cycle_id=self.id_to_base64(program_cycle.id, "ProgramCycleNode"),
            targeting_criteria={
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
            },
        )

        with mock.patch(
            "hct_mis_api.apps.payment.services.payment_plan_services.transaction"
        ) as mock_prepare_payment_plan_task:
            with self.assertNumQueries(11):
                pp = PaymentPlanService.create(
                    input_data=input_data, user=self.user, business_area_slug=self.business_area.slug
                )
            assert mock_prepare_payment_plan_task.on_commit.call_count == 1

        self.assertEqual(pp.status, PaymentPlan.Status.TP_OPEN)
        self.assertEqual(pp.total_households_count, 0)
        self.assertEqual(pp.total_individuals_count, 0)
        self.assertEqual(pp.payment_items.count(), 0)
        with self.assertNumQueries(74):
            prepare_payment_plan_task.delay(str(pp.id))
        pp.refresh_from_db()
        self.assertEqual(pp.status, PaymentPlan.Status.TP_OPEN)
        self.assertEqual(pp.total_households_count, 2)
        self.assertEqual(pp.total_individuals_count, 4)
        self.assertEqual(pp.payment_items.count(), 2)

    @freeze_time("2020-10-10")
    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_update_validation_errors(self, get_exchange_rate_mock: Any) -> None:
        pp = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED, created_by=self.user)

        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)

        input_data = dict(
            dispersion_start_date=parse_date("2020-09-10"),
            dispersion_end_date=parse_date("2020-09-11"),
            currency="USD",
        )

        with self.assertRaisesMessage(GraphQLError, "Not Allow edit Payment Plan within status LOCKED"):
            pp = PaymentPlanService(payment_plan=pp).update(input_data=input_data)
        pp.status = PaymentPlan.Status.OPEN
        pp.save()

        with self.assertRaisesMessage(
            GraphQLError, f"Dispersion End Date [{input_data['dispersion_end_date']}] cannot be a past date"
        ):
            PaymentPlanService(payment_plan=pp).update(input_data=input_data)

    @freeze_time("2023-10-10")
    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_create_follow_up_pp(self, get_exchange_rate_mock: Any) -> None:
        tc = TargetingCriteriaFactory()
        pp = PaymentPlanFactory(
            targeting_criteria=tc,
            total_households_count=1,
            created_by=self.user,
        )
        program = pp.program_cycle.program
        payments = []
        for _ in range(4):
            hoh = IndividualFactory(household=None)
            hh = HouseholdFactory(head_of_household=hoh, program=program, business_area=self.business_area)
            IndividualRoleInHouseholdFactory(household=hh, individual=hoh, role=ROLE_PRIMARY)
            IndividualFactory.create_batch(2, household=hh)
            payment = PaymentFactory(
                parent=pp, household=hh, status=Payment.STATUS_DISTRIBUTION_SUCCESS, currency="PLN"
            )
            payments.append(payment)

        dispersion_start_date = (pp.dispersion_start_date + timedelta(days=1)).date()
        dispersion_end_date = (pp.dispersion_end_date + timedelta(days=1)).date()

        with self.assertRaisesMessage(
            GraphQLError, "Cannot create a follow-up for a payment plan with no unsuccessful payments"
        ):
            PaymentPlanService(pp).create_follow_up(self.user, dispersion_start_date, dispersion_end_date)

        # do not create follow-up payments for STATUS_ERROR, STATUS_NOT_DISTRIBUTED, STATUS_FORCE_FAILED,
        for payment, status in zip(
            payments[:3], [Payment.STATUS_ERROR, Payment.STATUS_NOT_DISTRIBUTED, Payment.STATUS_FORCE_FAILED]
        ):
            payment.status = status
            payment.save()

        # do not create follow-up payments for withdrawn households
        payments[3].household.withdrawn = True
        payments[3].household.save()

        pp_error = payments[0]
        pp_not_distributed = payments[1]
        pp_force_failed = payments[2]

        with self.assertNumQueries(8):
            follow_up_pp = PaymentPlanService(pp).create_follow_up(
                self.user, dispersion_start_date, dispersion_end_date
            )

        follow_up_pp.refresh_from_db()
        self.assertEqual(follow_up_pp.status, PaymentPlan.Status.OPEN)
        self.assertEqual(follow_up_pp.target_population, pp.target_population)
        self.assertEqual(follow_up_pp.program, pp.program)
        self.assertEqual(follow_up_pp.program_cycle, pp.program_cycle)
        self.assertEqual(follow_up_pp.business_area, pp.business_area)
        self.assertEqual(follow_up_pp.created_by, self.user)
        self.assertEqual(follow_up_pp.currency, pp.currency)
        self.assertEqual(follow_up_pp.dispersion_start_date, dispersion_start_date)
        self.assertEqual(follow_up_pp.dispersion_end_date, dispersion_end_date)
        self.assertEqual(follow_up_pp.program_cycle.start_date, pp.program_cycle.start_date)
        self.assertEqual(follow_up_pp.program_cycle.end_date, pp.program_cycle.end_date)
        self.assertEqual(follow_up_pp.total_households_count, 0)
        self.assertEqual(follow_up_pp.total_individuals_count, 0)
        self.assertEqual(follow_up_pp.payment_items.count(), 0)

        self.assertEqual(pp.follow_ups.count(), 1)

        prepare_follow_up_payment_plan_task(follow_up_pp.id)
        follow_up_pp.refresh_from_db()

        self.assertEqual(follow_up_pp.status, PaymentPlan.Status.OPEN)
        self.assertEqual(follow_up_pp.build_status, PaymentPlan.BuildStatus.BUILD_STATUS_OK)

        self.assertEqual(follow_up_pp.payment_items.count(), 3)
        self.assertEqual(
            {pp_error.id, pp_not_distributed.id, pp_force_failed.id},
            set(follow_up_pp.payment_items.values_list("source_payment_id", flat=True)),
        )

        follow_up_payment = follow_up_pp.payment_items.first()
        self.assertEqual(follow_up_payment.status, Payment.STATUS_PENDING)
        self.assertEqual(follow_up_payment.parent, follow_up_pp)
        self.assertIsNotNone(follow_up_payment.source_payment)
        self.assertEqual(follow_up_payment.is_follow_up, True)
        self.assertEqual(follow_up_payment.business_area, follow_up_payment.source_payment.business_area)
        self.assertEqual(follow_up_payment.household, follow_up_payment.source_payment.household)
        self.assertEqual(follow_up_payment.head_of_household, follow_up_payment.source_payment.head_of_household)
        self.assertEqual(follow_up_payment.collector, follow_up_payment.source_payment.collector)
        self.assertEqual(follow_up_payment.currency, follow_up_payment.source_payment.currency)

        # exclude one payment from follow up pp, create new follow up pp which covers this payment
        follow_up_payment.excluded = True
        follow_up_payment.save()

        with self.assertNumQueries(8):
            follow_up_pp_2 = PaymentPlanService(pp).create_follow_up(
                self.user, dispersion_start_date, dispersion_end_date
            )

        self.assertEqual(pp.follow_ups.count(), 2)

        with self.assertNumQueries(47):
            prepare_follow_up_payment_plan_task(follow_up_pp_2.id)

        self.assertEqual(follow_up_pp_2.payment_items.count(), 1)
        self.assertEqual(
            {follow_up_payment.source_payment.id},
            set(follow_up_pp_2.payment_items.values_list("source_payment_id", flat=True)),
        )

    def test_create_follow_up_pp_from_follow_up_validation(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.FINISHED,
            is_follow_up=True,
        )
        dispersion_start_date = (payment_plan.dispersion_start_date + timedelta(days=1)).date()
        dispersion_end_date = (payment_plan.dispersion_end_date + timedelta(days=1)).date()
        with self.assertRaises(GraphQLError) as e:
            PaymentPlanService(payment_plan).create_follow_up(self.user, dispersion_start_date, dispersion_end_date)
        self.assertEqual(
            e.exception.message,
            "Cannot create a follow-up of a follow-up Payment Plan",
        )

    def test_update_follow_up_dates_and_not_currency(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.OPEN,
            currency="PLN",
            is_follow_up=True,
        )
        dispersion_start_date = (payment_plan.dispersion_start_date + timedelta(days=1)).date()
        dispersion_end_date = (payment_plan.dispersion_end_date + timedelta(days=1)).date()
        payment_plan = PaymentPlanService(payment_plan).update(
            {
                "dispersion_start_date": dispersion_start_date,
                "dispersion_end_date": dispersion_end_date,
                "currency": "UAH",
            }
        )
        self.assertEqual(payment_plan.currency, "PLN")
        self.assertEqual(payment_plan.dispersion_start_date, dispersion_start_date)
        self.assertEqual(payment_plan.dispersion_end_date, dispersion_end_date)

    @flaky(max_runs=5, min_passes=1)
    @freeze_time("2023-10-10")
    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    @patch("hct_mis_api.apps.payment.models.PaymentPlanSplit.MIN_NO_OF_PAYMENTS_IN_CHUNK")
    def test_split(self, min_no_of_payments_in_chunk_mock: Any, get_exchange_rate_mock: Any) -> None:
        min_no_of_payments_in_chunk_mock.__get__ = mock.Mock(return_value=2)

        pp = PaymentPlanFactory(created_by=self.user)

        with self.assertRaisesMessage(GraphQLError, "No payments to split"):
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
                parent=pp, household=hh, status=Payment.STATUS_DISTRIBUTION_SUCCESS, currency="PLN", collector=collector
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
                parent=pp, household=hh, status=Payment.STATUS_DISTRIBUTION_SUCCESS, currency="PLN", collector=collector
            )
            payments.append(payment)

        for _ in range(5):
            collector = IndividualFactory(household=None)
            hoh = IndividualFactory(household=None)
            hh = HouseholdFactory(head_of_household=hoh)
            IndividualRoleInHouseholdFactory(household=hh, individual=hoh, role=ROLE_PRIMARY)
            IndividualFactory.create_batch(2, household=hh)
            payment = PaymentFactory(
                parent=pp, household=hh, status=Payment.STATUS_DISTRIBUTION_SUCCESS, currency="PLN", collector=collector
            )
            payments.append(payment)

        with self.assertRaisesMessage(GraphQLError, "Payments Number is required for split by records"):
            PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_RECORDS, chunks_no=None)

        with self.assertRaisesMessage(
            GraphQLError, "Payment Parts number should be between 2 and total number of payments"
        ):
            PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_RECORDS, chunks_no=669)

        with mock.patch(
            "hct_mis_api.apps.payment.services.payment_plan_services.PaymentPlanSplit.MAX_CHUNKS"
        ) as max_chunks_patch:
            max_chunks_patch.__get__ = mock.Mock(return_value=2)
            with self.assertRaisesMessage(GraphQLError, "Too many Payment Parts to split: 6, maximum is 2"):
                PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_RECORDS, chunks_no=2)

        # split by collector
        with self.assertNumQueries(26):
            PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_COLLECTOR)
        unique_collectors_count = pp.eligible_payments.values_list("collector", flat=True).distinct().count()
        self.assertEqual(unique_collectors_count, 10)
        pp_splits = pp.splits.all().order_by("order")

        self.assertEqual(pp_splits.count(), unique_collectors_count)
        self.assertEqual(pp_splits[0].split_type, PaymentPlanSplit.SplitType.BY_COLLECTOR)
        self.assertEqual(pp_splits[0].payments.count(), 3)
        self.assertEqual(pp_splits[1].payments.count(), 1)
        self.assertEqual(pp_splits[2].payments.count(), 1)
        self.assertEqual(pp_splits[3].payments.count(), 1)
        self.assertEqual(pp_splits[4].payments.count(), 1)
        self.assertEqual(pp_splits[5].payments.count(), 1)
        self.assertEqual(pp_splits[6].payments.count(), 1)
        self.assertEqual(pp_splits[7].payments.count(), 1)
        self.assertEqual(pp_splits[8].payments.count(), 1)
        self.assertEqual(pp_splits[9].payments.count(), 1)

        # split by records
        with self.assertNumQueries(16):
            PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_RECORDS, chunks_no=5)
        pp_splits = pp.splits.all().order_by("order")
        self.assertEqual(pp_splits.count(), 3)
        self.assertEqual(pp_splits[0].split_type, PaymentPlanSplit.SplitType.BY_RECORDS)
        self.assertEqual(pp_splits[0].payments.count(), 5)
        self.assertEqual(pp_splits[1].payments.count(), 5)
        self.assertEqual(pp_splits[2].payments.count(), 2)

        # split by admin2
        with self.assertNumQueries(14):
            PaymentPlanService(pp).split(PaymentPlanSplit.SplitType.BY_ADMIN_AREA2)
        unique_admin2_count = pp.eligible_payments.values_list("household__admin2", flat=True).distinct().count()
        self.assertEqual(unique_admin2_count, 2)
        pp_splits = pp.splits.all().order_by("order")
        self.assertEqual(pp.splits.count(), unique_admin2_count)
        self.assertEqual(pp_splits[0].split_type, PaymentPlanSplit.SplitType.BY_ADMIN_AREA2)
        self.assertEqual(pp_splits[0].payments.count(), 4)
        self.assertEqual(pp_splits[1].payments.count(), 8)

    @freeze_time("2023-10-10")
    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_send_to_payment_gateway(self, get_exchange_rate_mock: Any) -> None:
        pp = PaymentPlanFactory(
            status=PaymentPlan.Status.ACCEPTED,
            created_by=self.user,
        )
        pp.background_action_status_send_to_payment_gateway()
        pp.save()
        with self.assertRaisesMessage(GraphQLError, "Sending in progress"):
            PaymentPlanService(pp).send_to_payment_gateway()

        pp.background_action_status_none()
        pp.save()

        pg_fsp = FinancialServiceProviderFactory(
            name="Western Union",
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            payment_gateway_id="123",
        )
        pg_fsp.delivery_mechanisms.add(self.dm_transfer_to_account)
        dm = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=pp,
            financial_service_provider=pg_fsp,
            delivery_mechanism=self.dm_transfer_to_account,
            sent_to_payment_gateway=True,
        )

        with self.assertRaisesMessage(GraphQLError, "Already sent to Payment Gateway"):
            PaymentPlanService(pp).send_to_payment_gateway()

        dm.sent_to_payment_gateway = False
        dm.save()
        with mock.patch(
            "hct_mis_api.apps.payment.services.payment_plan_services.send_to_payment_gateway.delay"
        ) as mock_send_to_payment_gateway_task:
            pps = PaymentPlanService(pp)
            pps.user = mock.MagicMock(pk="123")
            pps.send_to_payment_gateway()
            assert mock_send_to_payment_gateway_task.call_count == 1

    @freeze_time("2020-10-10")
    def test_create_with_program_cycle_validation_error(self) -> None:
        self.business_area.is_payment_plan_applicable = True
        self.business_area.save()
        program = ProgramFactory(
            status=Program.ACTIVE,
            start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
            cycle__start_date=timezone.datetime(2021, 10, 10, tzinfo=utc).date(),
            cycle__end_date=timezone.datetime(2021, 12, 10, tzinfo=utc).date(),
        )
        cycle = program.cycles.first()
        input_data = dict(
            business_area_slug="afghanistan",
            dispersion_start_date=parse_date("2020-11-11"),
            dispersion_end_date=parse_date("2020-11-20"),
            currency="USD",
            name="TestName123",
            program_cycle_id=self.id_to_base64(cycle.id, "ProgramCycleNode"),
            targeting_criteria={
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
            },
        )

        with self.assertRaisesMessage(
            GraphQLError,
            "Impossible to create Payment Plan for Programme Cycle within Finished status",
        ):
            cycle.status = ProgramCycle.FINISHED
            cycle.save()
            PaymentPlanService.create(input_data=input_data, user=self.user, business_area_slug=self.business_area.slug)

        cycle.status = ProgramCycle.DRAFT
        cycle.end_date = None
        cycle.save()
        PaymentPlanService.create(input_data=input_data, user=self.user, business_area_slug=self.business_area.slug)
        cycle.refresh_from_db()
        # open PP will update cycle' status into Active
        assert cycle.status == ProgramCycle.DRAFT

    @freeze_time("2022-12-12")
    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_full_rebuild(self, get_exchange_rate_mock: Any) -> None:
        program = ProgramFactory(
            status=Program.ACTIVE,
            start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
        )
        program_cycle = program.cycles.first()
        self.business_area.is_payment_plan_applicable = True
        self.business_area.save()

        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1, program=program, business_area=self.business_area)
        hh2 = HouseholdFactory(head_of_household=hoh2, program=program, business_area=self.business_area)
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)

        input_data = dict(
            business_area_slug="afghanistan",
            name="paymentPlanName",
            program_cycle_id=self.id_to_base64(program_cycle.id, "ProgramCycleNode"),
            targeting_criteria={
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
            },
        )
        with mock.patch(
            "hct_mis_api.apps.payment.services.payment_plan_services.transaction"
        ) as mock_prepare_payment_plan_task:
            with self.assertNumQueries(11):
                pp = PaymentPlanService.create(
                    input_data=input_data, user=self.user, business_area_slug=self.business_area.slug
                )
            assert mock_prepare_payment_plan_task.on_commit.call_count == 1

        self.assertEqual(pp.status, PaymentPlan.Status.TP_OPEN)
        self.assertEqual(pp.total_households_count, 0)
        self.assertEqual(pp.total_individuals_count, 0)
        self.assertEqual(pp.payment_items.count(), 0)
        with self.assertNumQueries(74):
            prepare_payment_plan_task.delay(str(pp.id))
        pp.refresh_from_db()
        self.assertEqual(pp.status, PaymentPlan.Status.TP_OPEN)
        self.assertEqual(pp.payment_items.count(), 2)

        old_payment_ids = list(pp.payment_items.values_list("id", flat=True))
        old_payment_unicef_ids = list(pp.payment_items.values_list("unicef_id", flat=True))

        # check rebuild
        pp_service = PaymentPlanService(payment_plan=pp)
        pp_service.full_rebuild()

        pp.refresh_from_db()
        # all Payments (removed and new)
        self.assertEqual(Payment.all_objects.filter(parent=pp).count(), 2)

        new_payment_ids = list(pp.payment_items.values_list("id", flat=True))
        new_payment_unicef_ids = list(pp.payment_items.values_list("unicef_id", flat=True))

        for p_id in new_payment_ids:
            self.assertNotIn(p_id, old_payment_ids)

        for p_unicef_id in new_payment_unicef_ids:
            self.assertNotIn(p_unicef_id, old_payment_unicef_ids)

    def test_get_approval_type_by_action_value_error(self) -> None:
        with self.assertRaises(ValueError) as error:
            PaymentPlanService(payment_plan=self.payment_plan).get_approval_type_by_action()
        self.assertEqual(str(error.exception), "Action cannot be None")

    def test_validate_action_not_implemented(self) -> None:
        with self.assertRaises(GraphQLError) as e:
            PaymentPlanService(self.payment_plan).execute_update_status_action(
                input_data={"action": "INVALID_ACTION"}, user=self.user
            )
        self.assertEqual(
            e.exception.message,
            "Not Implemented Action: INVALID_ACTION. List of possible actions: "
            "['TP_LOCK', 'TP_UNLOCK', 'TP_REBUILD', 'DRAFT', 'LOCK', 'LOCK_FSP', 'UNLOCK', 'UNLOCK_FSP', "
            "'SEND_FOR_APPROVAL', 'APPROVE', 'AUTHORIZE', 'REVIEW', 'REJECT', 'SEND_TO_PAYMENT_GATEWAY']",
        )

    def test_tp_lock_invalid_pp_status(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle, created_by=self.user, status=PaymentPlan.Status.DRAFT
        )
        with self.assertRaises(GraphQLError) as e:
            PaymentPlanService(payment_plan).tp_lock()
        self.assertEqual(
            e.exception.message,
            "Can only Lock Population for Open Population status",
        )

    def test_tp_unlock(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle, created_by=self.user, status=PaymentPlan.Status.DRAFT
        )
        with self.assertRaises(GraphQLError) as e:
            PaymentPlanService(payment_plan).tp_unlock()
        self.assertEqual(
            e.exception.message,
            "Can only Unlock Population for Locked Population status",
        )
        payment_plan.status = PaymentPlan.Status.TP_LOCKED
        payment_plan.save()
        PaymentPlanService(payment_plan).tp_unlock()

        payment_plan.refresh_from_db()
        self.assertEqual(payment_plan.status, PaymentPlan.Status.TP_OPEN)
        self.assertEqual(payment_plan.build_status, PaymentPlan.BuildStatus.BUILD_STATUS_PENDING)

    def test_tp_rebuild(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.DRAFT,
            build_status=PaymentPlan.BuildStatus.BUILD_STATUS_FAILED,
        )
        with self.assertRaises(GraphQLError) as e:
            PaymentPlanService(payment_plan).tp_rebuild()
        self.assertEqual(
            e.exception.message,
            "Can only Rebuild Population for Locked or Open Population status",
        )
        payment_plan.status = PaymentPlan.Status.TP_LOCKED
        payment_plan.save()
        PaymentPlanService(payment_plan).tp_rebuild()

        payment_plan.refresh_from_db()
        self.assertEqual(payment_plan.status, PaymentPlan.Status.TP_LOCKED)
        self.assertEqual(payment_plan.build_status, PaymentPlan.BuildStatus.BUILD_STATUS_PENDING)

    def test_draft_with_invalid_pp_status(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.DRAFT,
        )
        with self.assertRaises(GraphQLError) as e:
            PaymentPlanService(payment_plan).draft()
        self.assertEqual(
            e.exception.message,
            "Only Locked Population status can be moved to next step",
        )

    def test_lock_if_no_valid_payments(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.OPEN,
        )
        with self.assertRaises(GraphQLError) as e:
            PaymentPlanService(payment_plan).lock()
        self.assertEqual(
            e.exception.message,
            "At least one valid Payment should exist in order to Lock the Payment Plan",
        )

    def test_update_pp_validation_errors(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.DRAFT,
        )
        with self.assertRaises(GraphQLError) as e:
            PaymentPlanService(payment_plan).update({"exclusion_reason": "test_data"})
        self.assertEqual(
            e.exception.message,
            f"Not Allow edit targeting criteria within status {payment_plan.status}",
        )

        with self.assertRaises(GraphQLError) as e:
            PaymentPlanService(payment_plan).update({"vulnerability_score_min": "test_data"})
        self.assertEqual(
            e.exception.message,
            "You can only set vulnerability_score_min and vulnerability_score_max on Locked Population status",
        )

        with self.assertRaises(GraphQLError) as e:
            PaymentPlanService(payment_plan).update({"currency": "test_data"})
        self.assertEqual(
            e.exception.message,
            f"Not Allow edit Payment Plan within status {payment_plan.status}",
        )

        with self.assertRaises(GraphQLError) as e:
            PaymentPlanService(payment_plan).update({"name": "test_data"})
        self.assertEqual(
            e.exception.message,
            "Name can be changed only within Open status",
        )

        payment_plan.status = PaymentPlan.Status.TP_OPEN
        payment_plan.save()
        PaymentPlanFactory(
            name="test_data",
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.DRAFT,
        )
        with self.assertRaises(GraphQLError) as e:
            PaymentPlanService(payment_plan).update({"name": "test_data"})
        self.assertEqual(
            e.exception.message,
            f"Name 'test_data' and program '{self.cycle.program.name}' already exists.",
        )

        self.cycle.status = ProgramCycle.FINISHED
        self.cycle.save()
        program_cycle_id = self.id_to_base64(self.cycle.id, "ProgramCycleNode")
        with self.assertRaises(GraphQLError) as e:
            PaymentPlanService(payment_plan).update({"program_cycle_id": program_cycle_id})
        self.assertEqual(
            e.exception.message,
            "Not possible to assign Finished Program Cycle",
        )

    def test_rebuild_payment_plan_population(self) -> None:
        pp = PaymentPlanFactory(
            name="test_data",
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.TP_OPEN,
        )

        PaymentPlanService.rebuild_payment_plan_population(rebuild_list=False, rebuild_stats=True, payment_plan=pp)
        PaymentPlanService.rebuild_payment_plan_population(rebuild_list=True, rebuild_stats=False, payment_plan=pp)

        self.payment_plan.refresh_from_db(fields=("build_status",))
        self.assertEqual(pp.build_status, PaymentPlan.BuildStatus.BUILD_STATUS_PENDING)

    def test_unlock_fsp(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.LOCKED_FSP,
        )

        PaymentPlanService(payment_plan).unlock_fsp()

        payment_plan.refresh_from_db(fields=("status",))
        self.assertEqual(payment_plan.status, PaymentPlan.Status.LOCKED)

    def test_update_pp_program_cycle(self) -> None:
        new_cycle = ProgramCycleFactory(program=self.program, title="New Cycle ABC")
        program_cycle_id = self.id_to_base64(new_cycle.id, "ProgramCycleNode")

        PaymentPlanService(self.payment_plan).update({"program_cycle_id": program_cycle_id})

        self.payment_plan.refresh_from_db()
        self.assertEqual(self.payment_plan.program_cycle.title, "New Cycle ABC")

    def test_update_pp_vulnerability_score(self) -> None:
        PaymentPlanService(self.payment_plan).update(
            {"vulnerability_score_min": "11.229222", "vulnerability_score_max": "77.889777"}
        )
        self.payment_plan.refresh_from_db(fields=("vulnerability_score_min", "vulnerability_score_max"))
        self.assertEqual(self.payment_plan.vulnerability_score_min, Decimal("11.229"))
        self.assertEqual(self.payment_plan.vulnerability_score_max, Decimal("77.890"))

    def test_update_pp_exclude_ids(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.TP_OPEN,
        )
        PaymentPlanService(payment_plan).update({"excluded_ids": "IND-123", "exclusion_reason": "Test text"})
        payment_plan.refresh_from_db(fields=("excluded_ids", "exclusion_reason"))
        self.assertEqual(payment_plan.excluded_ids, "IND-123")
        self.assertEqual(payment_plan.exclusion_reason, "Test text")

    def test_update_pp_currency(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.OPEN,
            currency="AMD",
        )
        PaymentPlanService(payment_plan).update({"currency": "PLN"})
        payment_plan.refresh_from_db()
        self.assertEqual(payment_plan.currency, "PLN")

    def test_update_dispersion_end_date(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle,
            created_by=self.user,
            status=PaymentPlan.Status.OPEN,
            currency="AMD",
        )
        PaymentPlanService(payment_plan).update({"dispersion_end_date": timezone.now().date() + timedelta(days=3)})
        payment_plan.refresh_from_db()
        self.assertEqual(payment_plan.dispersion_end_date, timezone.now().date() + timedelta(days=3))

    def test_export_xlsx(self) -> None:
        payment_plan = PaymentPlanFactory(
            program_cycle=self.cycle, created_by=self.user, status=PaymentPlan.Status.LOCKED
        )
        self.assertEqual(FileTemp.objects.all().count(), 0)

        PaymentPlanService(payment_plan).export_xlsx(self.user.pk)

        self.assertEqual(FileTemp.objects.all().count(), 1)
        self.assertEqual(FileTemp.objects.first().object_id, str(payment_plan.pk))

    def test_create_payments_integrity_error_handling(self) -> None:
        household, individuals = create_household_with_individual_with_collectors(
            household_args={
                "business_area": self.business_area,
                "program": self.program,
            },
        )
        targeting_criteria = TargetingCriteriaFactory()
        TargetingCriteriaRuleFactory(household_ids=f"{household.unicef_id}", targeting_criteria=targeting_criteria)
        payment_plan = PaymentPlanFactory(
            created_by=self.user,
            status=PaymentPlan.Status.PREPARING,
            business_area=self.business_area,
            program_cycle=self.cycle,
            targeting_criteria=targeting_criteria,
        )
        PaymentFactory(
            parent=payment_plan,
            program_id=self.program.id,
            business_area_id=payment_plan.business_area_id,
            status=Payment.STATUS_PENDING,
            household_id=household.pk,
            collector_id=individuals[0].pk,
        )

        # check households with payments in program
        hh_qs = self.program.households_with_payments_in_program
        self.assertEqual(hh_qs.count(), 1)
        self.assertEqual(hh_qs.first().unicef_id, household.unicef_id)

        with self.assertRaises(IntegrityError) as error:
            PaymentPlanService.create_payments(payment_plan)

        self.assertIn(
            'duplicate key value violates unique constraint "payment_plan_and_household"', str(error.exception)
        )
