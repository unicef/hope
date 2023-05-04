from datetime import timedelta
from typing import Any
from unittest import mock

from django.utils import timezone

from aniso8601 import parse_date
from freezegun import freeze_time
from graphql import GraphQLError
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
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
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import Payment, PaymentPlan
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import TargetPopulation


class TestPaymentPlanServices(APITestCase):
    databases = ("default",)

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.PM_CREATE], BusinessArea.objects.get(slug="afghanistan")
        )

    def test_delete_open(self) -> None:
        pp: PaymentPlan = PaymentPlanFactory(status=PaymentPlan.Status.OPEN)
        self.assertEqual(pp.target_population.status, TargetPopulation.STATUS_OPEN)

        pp = PaymentPlanService(payment_plan=pp).delete()
        self.assertEqual(pp.is_removed, True)
        pp.target_population.refresh_from_db()
        self.assertEqual(pp.target_population.status, TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE)

    def test_delete_locked(self) -> None:
        pp = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED)

        with self.assertRaises(GraphQLError):
            PaymentPlanService(payment_plan=pp).delete()

    @freeze_time("2020-10-10")
    def test_create_validation_errors(self) -> None:
        targeting = TargetPopulationFactory()

        input_data = dict(
            business_area_slug="afghanistan",
            targeting_id=self.id_to_base64(targeting.id, "Targeting"),
            start_date=timezone.datetime(2021, 10, 10, tzinfo=utc),
            end_date=timezone.datetime(2021, 12, 10, tzinfo=utc),
            dispersion_start_date=parse_date("2020-09-10"),
            dispersion_end_date=parse_date("2020-09-11"),
            currency="USD",
        )

        with self.assertRaisesMessage(GraphQLError, "PaymentPlan can not be created in provided Business Area"):
            PaymentPlanService.create(input_data=input_data, user=self.user)
        self.business_area.is_payment_plan_applicable = True
        self.business_area.save()

        with self.assertRaisesMessage(
            GraphQLError,
            f"TargetPopulation id:{targeting.id} does not exist or is not in status 'Ready for Payment Module'",
        ):
            PaymentPlanService.create(input_data=input_data, user=self.user)
        targeting.status = TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE
        targeting.save()

        with self.assertRaisesMessage(GraphQLError, "TargetPopulation should have related Program defined"):
            PaymentPlanService.create(input_data=input_data, user=self.user)
        targeting.program = ProgramFactory()
        targeting.save()

        with self.assertRaisesMessage(
            GraphQLError, f"Dispersion End Date [{input_data['dispersion_end_date']}] cannot be a past date"
        ):
            PaymentPlanService.create(input_data=input_data, user=self.user)

    @freeze_time("2020-10-10")
    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_create(self, get_exchange_rate_mock: Any) -> None:
        targeting = TargetPopulationFactory()

        self.business_area.is_payment_plan_applicable = True
        self.business_area.save()

        targeting.status = TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE
        targeting.program = ProgramFactory(
            start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
        )

        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)

        targeting.households.set([hh1, hh2])
        targeting.save()

        input_data = dict(
            business_area_slug="afghanistan",
            targeting_id=self.id_to_base64(targeting.id, "Targeting"),
            start_date=timezone.datetime(2021, 10, 10, tzinfo=utc),
            end_date=timezone.datetime(2021, 12, 10, tzinfo=utc),
            dispersion_start_date=parse_date("2020-09-10"),
            dispersion_end_date=parse_date("2020-11-10"),
            currency="USD",
        )

        with mock.patch(
            "hct_mis_api.apps.payment.services.payment_plan_services.prepare_payment_plan_task"
        ) as mock_prepare_payment_plan_task:
            with self.assertNumQueries(5):
                pp = PaymentPlanService.create(input_data=input_data, user=self.user)
            self.assertEqual(mock_prepare_payment_plan_task.delay.call_args, mock.call(pp.id))

        self.assertEqual(pp.status, PaymentPlan.Status.PREPARING)
        self.assertEqual(pp.target_population.status, TargetPopulation.STATUS_ASSIGNED)
        self.assertEqual(pp.total_households_count, 0)
        self.assertEqual(pp.total_individuals_count, 0)
        self.assertEqual(pp.payment_items.count(), 0)

        with self.assertNumQueries(10):
            prepare_payment_plan_task.delay(pp.id)
        pp.refresh_from_db()
        self.assertEqual(pp.status, PaymentPlan.Status.OPEN)
        self.assertEqual(pp.total_households_count, 2)
        self.assertEqual(pp.total_individuals_count, 4)
        self.assertEqual(pp.payment_items.count(), 2)

    @freeze_time("2020-10-10")
    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_update_validation_errors(self, get_exchange_rate_mock: Any) -> None:
        pp = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED)
        new_targeting = TargetPopulationFactory(program=None)

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
            start_date=timezone.datetime(2021, 10, 10, tzinfo=utc),
            end_date=timezone.datetime(2021, 12, 10, tzinfo=utc),
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

        with self.assertRaisesMessage(GraphQLError, "TargetPopulation should have related Program defined"):
            pp = PaymentPlanService(payment_plan=pp).update(input_data=input_data)
        new_targeting.program = ProgramFactory()
        new_targeting.save()

        with self.assertRaisesMessage(
            GraphQLError, f"Dispersion End Date [{input_data['dispersion_end_date']}] cannot be a past date"
        ):
            PaymentPlanService(payment_plan=pp).update(input_data=input_data)

    @freeze_time("2020-10-10")
    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_update(self, get_exchange_rate_mock: Any) -> None:
        pp = PaymentPlanFactory(total_households_count=1)
        hoh1 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        PaymentFactory(parent=pp, household=hh1)
        self.assertEqual(pp.payment_items.count(), 1)

        new_targeting = TargetPopulationFactory()
        new_targeting.status = TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE
        new_targeting.program = ProgramFactory(
            start_date=timezone.datetime(2021, 11, 10, tzinfo=utc).date(),
        )
        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)
        new_targeting.households.set([hh1, hh2])
        new_targeting.save()

        with freeze_time("2020-11-10"):
            # test targeting update, payments recreation triggered
            old_pp_targeting = pp.target_population
            old_pp_exchange_rate = pp.exchange_rate
            old_pp_updated_at = pp.updated_at

            updated_pp_1 = PaymentPlanService(payment_plan=pp).update(
                input_data=dict(targeting_id=self.id_to_base64(new_targeting.id, "Targeting"))
            )
            updated_pp_1.refresh_from_db()
            self.assertNotEqual(old_pp_updated_at, updated_pp_1.updated_at)
            self.assertNotEqual(old_pp_exchange_rate, updated_pp_1.exchange_rate)
            self.assertEqual(updated_pp_1.total_households_count, 2)
            self.assertEqual(updated_pp_1.payment_items.count(), 2)
            self.assertEqual(updated_pp_1.target_population, new_targeting)
            self.assertEqual(updated_pp_1.target_population.status, TargetPopulation.STATUS_ASSIGNED)
            self.assertEqual(updated_pp_1.program, updated_pp_1.target_population.program)
            self.assertEqual(old_pp_targeting.status, TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE)

            # test start_date update
            old_pp_start_date = pp.start_date
            updated_pp_2 = PaymentPlanService(payment_plan=pp).update(
                input_data=dict(start_date=timezone.datetime(2021, 12, 10, tzinfo=utc))
            )
            updated_pp_2.refresh_from_db()
            self.assertNotEqual(old_pp_start_date, updated_pp_2.start_date)

    @freeze_time("2020-10-10")
    def test_cannot_create_payment_plan_with_start_date_earlier_than_in_program(self) -> None:
        self.business_area.is_payment_plan_applicable = True
        self.business_area.save()

        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)

        targeting = TargetPopulationFactory(status=TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE)
        targeting.program = ProgramFactory(
            start_date=timezone.datetime(2021, 5, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2021, 8, 10, tzinfo=utc).date(),
        )
        targeting.households.set([hh1, hh2])
        targeting.save()

        input_data = dict(
            business_area_slug="afghanistan",
            targeting_id=self.id_to_base64(targeting.id, "Targeting"),
            start_date=parse_date("2021-04-10"),
            end_date=parse_date("2021-07-10"),
            dispersion_start_date=parse_date("2020-09-10"),
            dispersion_end_date=parse_date("2020-11-10"),
            currency="USD",
        )

        with self.assertRaisesMessage(GraphQLError, "Start date cannot be earlier than start date in the program"):
            PaymentPlanService.create(input_data=input_data, user=self.user)

    @freeze_time("2020-10-10")
    def test_cannot_create_payment_plan_with_end_date_later_than_in_program(self) -> None:
        self.business_area.is_payment_plan_applicable = True
        self.business_area.save()

        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)

        targeting = TargetPopulationFactory(status=TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE)
        targeting.program = ProgramFactory(
            start_date=timezone.datetime(2021, 5, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2021, 8, 10, tzinfo=utc).date(),
        )
        targeting.households.set([hh1, hh2])
        targeting.save()

        input_data = dict(
            business_area_slug="afghanistan",
            targeting_id=self.id_to_base64(targeting.id, "Targeting"),
            start_date=parse_date("2021-05-11"),
            end_date=parse_date("2021-09-10"),
            dispersion_start_date=parse_date("2020-09-10"),
            dispersion_end_date=parse_date("2020-11-10"),
            currency="USD",
        )

        with self.assertRaisesMessage(GraphQLError, "End date cannot be later that end date in the program"):
            PaymentPlanService.create(input_data=input_data, user=self.user)

    @freeze_time("2020-10-10")
    def test_cannot_update_payment_plan_with_start_date_earlier_than_in_program(self) -> None:
        pp = PaymentPlanFactory(
            total_households_count=1,
            start_date=timezone.datetime(2021, 6, 10, tzinfo=utc),
            end_date=timezone.datetime(2021, 7, 10, tzinfo=utc),
        )
        hoh1 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        PaymentFactory(parent=pp, household=hh1)
        new_targeting = TargetPopulationFactory(status=TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE)
        new_targeting.program = ProgramFactory(
            start_date=timezone.datetime(2021, 5, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2021, 8, 10, tzinfo=utc).date(),
        )
        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)
        new_targeting.households.set([hh1, hh2])
        new_targeting.save()
        pp.target_population = new_targeting
        pp.save()

        with self.assertRaisesMessage(GraphQLError, "Start date cannot be earlier than start date in the program"):
            PaymentPlanService(payment_plan=pp).update(
                input_data=dict(start_date=timezone.datetime(2021, 4, 10, tzinfo=utc))  # datetime
            )
            PaymentPlanService(payment_plan=pp).update(input_data=dict(end_date=parse_date("2021-04-10")))  # date

    @freeze_time("2020-10-10")
    def test_cannot_update_payment_plan_with_end_date_later_than_in_program(self) -> None:
        pp = PaymentPlanFactory(
            total_households_count=1,
            start_date=timezone.datetime(2021, 6, 10, tzinfo=utc),
            end_date=timezone.datetime(2021, 7, 10, tzinfo=utc),
        )
        hoh1 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        PaymentFactory(parent=pp, household=hh1)
        new_targeting = TargetPopulationFactory(status=TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE)
        new_targeting.program = ProgramFactory(
            start_date=timezone.datetime(2021, 5, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2021, 8, 10, tzinfo=utc).date(),
        )
        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)
        new_targeting.households.set([hh1, hh2])
        new_targeting.save()
        pp.target_population = new_targeting
        pp.save()

        with self.assertRaisesMessage(GraphQLError, "End date cannot be later that end date in the program"):
            PaymentPlanService(payment_plan=pp).update(
                input_data=dict(end_date=timezone.datetime(2021, 9, 10, tzinfo=utc))  # datetime
            )
            PaymentPlanService(payment_plan=pp).update(input_data=dict(end_date=parse_date("2021-09-10")))  # date

    @freeze_time("2020-10-10")
    def test_create_follow_up_pp(self) -> None:
        pp = PaymentPlanFactory(
            total_households_count=1,
            start_date=timezone.datetime(2021, 6, 10, tzinfo=utc),
            end_date=timezone.datetime(2021, 7, 10, tzinfo=utc),
        )

        new_targeting = TargetPopulationFactory(status=TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE)
        new_targeting.program = ProgramFactory(
            start_date=timezone.datetime(2021, 5, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2021, 8, 10, tzinfo=utc).date(),
        )

        payments = []

        for _ in range(4):
            hoh = IndividualFactory(household=None)
            hh = HouseholdFactory(head_of_household=hoh)
            IndividualRoleInHouseholdFactory(household=hh, individual=hoh, role=ROLE_PRIMARY)
            IndividualFactory.create_batch(2, household=hh)
            payment = PaymentFactory(parent=pp, household=hh, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
            payments.append(payment)

        new_targeting.households.set([p.household for p in payments])
        new_targeting.save()
        pp.target_population = new_targeting
        pp.save()

        dispersion_start_date = pp.dispersion_start_date + timedelta(days=1)
        dispersion_end_date = pp.dispersion_end_date + timedelta(days=1)

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

        with self.assertNumQueries(4):
            follow_up_pp = PaymentPlanService(pp).create_follow_up(
                self.user, dispersion_start_date, dispersion_end_date
            )

        self.assertEqual(follow_up_pp.status, PaymentPlan.Status.PREPARING)
        self.assertEqual(follow_up_pp.target_population, pp.target_population)
        self.assertEqual(follow_up_pp.program, pp.program)
        self.assertEqual(follow_up_pp.program_cycle, pp.program_cycle)
        self.assertEqual(follow_up_pp.business_area, pp.business_area)
        self.assertEqual(follow_up_pp.created_by, self.user)
        self.assertEqual(follow_up_pp.currency, pp.currency)
        self.assertEqual(follow_up_pp.dispersion_start_date, dispersion_start_date)
        self.assertEqual(follow_up_pp.dispersion_end_date, dispersion_end_date)
        self.assertEqual(follow_up_pp.start_date, pp.start_date)
        self.assertEqual(follow_up_pp.end_date, pp.end_date)
        self.assertEqual(follow_up_pp.total_households_count, 0)
        self.assertEqual(follow_up_pp.total_individuals_count, 0)
        self.assertEqual(follow_up_pp.payment_items.count(), 0)

        self.assertEqual(pp.follow_ups.count(), 1)

        with self.assertNumQueries(12):
            prepare_follow_up_payment_plan_task(follow_up_pp.id)

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

        with self.assertNumQueries(4):
            follow_up_pp_2 = PaymentPlanService(pp).create_follow_up(
                self.user, dispersion_start_date, dispersion_end_date
            )

        self.assertEqual(pp.follow_ups.count(), 2)

        with self.assertNumQueries(12):
            prepare_follow_up_payment_plan_task(follow_up_pp_2.id)

        self.assertEqual(follow_up_pp_2.payment_items.count(), 1)
        self.assertEqual(
            {follow_up_payment.source_payment.id},
            set(follow_up_pp_2.payment_items.values_list("source_payment_id", flat=True)),
        )
