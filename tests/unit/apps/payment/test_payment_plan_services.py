from datetime import timedelta
from typing import Any
from unittest import mock
from unittest.mock import patch

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
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.household.fixtures import (
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
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
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import TargetPopulation


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

    def test_delete_open(self) -> None:
        pp: PaymentPlan = PaymentPlanFactory(status=PaymentPlan.Status.OPEN, program__status=Program.ACTIVE)

        pp = PaymentPlanService(payment_plan=pp).delete()
        self.assertEqual(pp.is_removed, True)

    def test_delete_locked(self) -> None:
        pp = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED)

        with self.assertRaises(GraphQLError):
            PaymentPlanService(payment_plan=pp).delete()

    def test_delete_when_its_one_pp_in_cycle(self) -> None:
        pp = PaymentPlanFactory(status=PaymentPlan.Status.OPEN, program__status=Program.ACTIVE)
        program_cycle = ProgramCycleFactory(status=ProgramCycle.ACTIVE, program=pp.program)
        pp.program_cycle = program_cycle
        pp.save()
        pp.refresh_from_db()

        self.assertEqual(pp.program_cycle.status, ProgramCycle.ACTIVE)

        pp = PaymentPlanService(payment_plan=pp).delete()
        self.assertEqual(pp.is_removed, True)
        program_cycle.refresh_from_db()
        self.assertEqual(program_cycle.status, ProgramCycle.DRAFT)

    def test_delete_when_its_two_pp_in_cycle(self) -> None:
        pp_1 = PaymentPlanFactory(status=PaymentPlan.Status.OPEN, program__status=Program.ACTIVE)
        pp_2 = PaymentPlanFactory(status=PaymentPlan.Status.OPEN, program=pp_1.program)
        program_cycle = ProgramCycleFactory(status=ProgramCycle.ACTIVE, program=pp_1.program)
        pp_1.program_cycle = program_cycle
        pp_1.save()
        pp_1.refresh_from_db()
        pp_2.program_cycle = program_cycle
        pp_2.save()

        self.assertEqual(pp_1.program_cycle.status, ProgramCycle.ACTIVE)

        pp_1 = PaymentPlanService(payment_plan=pp_1).delete()
        self.assertEqual(pp_1.is_removed, True)
        program_cycle.refresh_from_db()
        self.assertEqual(program_cycle.status, ProgramCycle.ACTIVE)

    @flaky(max_runs=5, min_passes=1)
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

        input_data = dict(
            program_cycle_id=self.id_to_base64(str(program_cycle.id), "ProgramCycle"),
            dispersion_start_date=parse_date("2020-09-10"),
            dispersion_end_date=parse_date("2020-09-11"),
            currency="USD",
        )

        with self.assertRaisesMessage(GraphQLError, "PaymentPlan can not be created in provided Business Area"):
            PaymentPlanService.create(input_data=input_data, user=self.user, business_area_slug=self.business_area.slug)
        self.business_area.is_payment_plan_applicable = True
        self.business_area.save()

        with self.assertRaisesMessage(
            GraphQLError, f"Dispersion End Date [{input_data['dispersion_end_date']}] cannot be a past date"
        ):
            PaymentPlanService.create(input_data=input_data, user=self.user, business_area_slug=self.business_area.slug)
        input_data["dispersion_end_date"] = parse_date("2020-11-11")

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
            dispersion_start_date=parse_date("2020-09-10"),
            dispersion_end_date=parse_date("2020-11-10"),
            currency="USD",
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
        with self.assertNumQueries(77):
            prepare_payment_plan_task.delay(str(pp.id))
        pp.refresh_from_db()
        self.assertEqual(pp.status, PaymentPlan.Status.TP_OPEN)
        self.assertEqual(pp.total_households_count, 2)
        self.assertEqual(pp.total_individuals_count, 4)
        self.assertEqual(pp.payment_items.count(), 2)

    @freeze_time("2020-10-10")
    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_update_validation_errors(self, get_exchange_rate_mock: Any) -> None:
        pp = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED)
        new_targeting = TargetPopulationFactory(program=ProgramFactory())

        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)
        new_targeting.households.set([hh1, hh2])
        new_targeting.save()

        input_data = dict(
            targeting_id=self.id_to_base64(new_targeting.id, "Targeting"),
            dispersion_start_date=parse_date("2020-09-10"),
            dispersion_end_date=parse_date("2020-09-11"),
            currency="USD",
        )

        with self.assertRaisesMessage(GraphQLError, "Only Payment Plan in Open status can be edited"):
            pp = PaymentPlanService(payment_plan=pp).update(input_data=input_data)
        pp.status = PaymentPlan.Status.OPEN
        pp.save()

        with self.assertRaisesMessage(
            GraphQLError, f"TargetPopulation id:{new_targeting.id} does not exist or is not in status Ready"
        ):
            pp = PaymentPlanService(payment_plan=pp).update(input_data=input_data)
        new_targeting.status = TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE
        new_targeting.save()

        with self.assertRaisesMessage(
            GraphQLError, f"Dispersion End Date [{input_data['dispersion_end_date']}] cannot be a past date"
        ):
            PaymentPlanService(payment_plan=pp).update(input_data=input_data)

    @freeze_time("2023-10-10")
    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_create_follow_up_pp(self, get_exchange_rate_mock: Any) -> None:
        pp = PaymentPlanFactory(
            total_households_count=1,
            program__cycle__start_date=timezone.datetime(2021, 6, 10, tzinfo=utc).date(),
            program__cycle__end_date=timezone.datetime(2021, 7, 10, tzinfo=utc).date(),
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

        with self.assertNumQueries(5):
            follow_up_pp = PaymentPlanService(pp).create_follow_up(
                self.user, dispersion_start_date, dispersion_end_date
            )

        follow_up_pp.refresh_from_db()
        self.assertEqual(follow_up_pp.status, PaymentPlan.Status.TP_OPEN)
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

        with self.assertNumQueries(5):
            follow_up_pp_2 = PaymentPlanService(pp).create_follow_up(
                self.user, dispersion_start_date, dispersion_end_date
            )

        self.assertEqual(pp.follow_ups.count(), 2)

        with self.assertNumQueries(48):
            prepare_follow_up_payment_plan_task(follow_up_pp_2.id)

        self.assertEqual(follow_up_pp_2.payment_items.count(), 1)
        self.assertEqual(
            {follow_up_payment.source_payment.id},
            set(follow_up_pp_2.payment_items.values_list("source_payment_id", flat=True)),
        )

    @flaky(max_runs=5, min_passes=1)
    @freeze_time("2023-10-10")
    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    @patch("hct_mis_api.apps.payment.models.PaymentPlanSplit.MIN_NO_OF_PAYMENTS_IN_CHUNK")
    def test_split(self, min_no_of_payments_in_chunk_mock: Any, get_exchange_rate_mock: Any) -> None:
        min_no_of_payments_in_chunk_mock.__get__ = mock.Mock(return_value=2)

        pp = PaymentPlanFactory(
            program__cycle__start_date=timezone.datetime(2021, 6, 10, tzinfo=utc).date(),
            program__cycle__end_date=timezone.datetime(2021, 7, 10, tzinfo=utc).date(),
        )

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
            program__cycle__start_date=timezone.datetime(2021, 6, 10, tzinfo=utc).date(),
            program__cycle__end_date=timezone.datetime(2021, 7, 10, tzinfo=utc).date(),
            status=PaymentPlan.Status.ACCEPTED,
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
        assert cycle.status == ProgramCycle.ACTIVE

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
            dispersion_start_date=parse_date("2022-12-20"),
            dispersion_end_date=parse_date("2022-12-22"),
            currency="USD",
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
        with self.assertNumQueries(77):
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
        self.assertEqual(Payment.all_objects.filter(parent=pp).count(), 4)

        new_payment_ids = list(pp.payment_items.values_list("id", flat=True))
        new_payment_unicef_ids = list(pp.payment_items.values_list("unicef_id", flat=True))

        for p_id in new_payment_ids:
            self.assertNotIn(p_id, old_payment_ids)

        for p_unicef_id in new_payment_unicef_ids:
            self.assertNotIn(p_unicef_id, old_payment_unicef_ids)
