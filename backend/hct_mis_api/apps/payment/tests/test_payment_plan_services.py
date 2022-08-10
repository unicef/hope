from graphql import GraphQLError
from unittest.mock import patch
from freezegun import freeze_time
from aniso8601 import parse_date

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.household.fixtures import IndividualFactory, HouseholdFactory, IndividualRoleInHouseholdFactory
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory, PaymentFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.household.models import ROLE_PRIMARY


from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.base_test_case import APITestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan


class TestPaymentPlanServices(APITestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.PAYMENT_MODULE_CREATE], BusinessArea.objects.get(slug="afghanistan")
        )

    def test_delete_open(self):
        pp = PaymentPlanFactory(status=PaymentPlan.Status.OPEN)
        self.assertEqual(pp.target_population.status, TargetPopulation.STATUS_DRAFT)

        pp = PaymentPlanService(payment_plan=pp).delete()
        self.assertEqual(pp.is_removed, True)
        pp.target_population.refresh_from_db()
        self.assertEqual(pp.target_population.status, TargetPopulation.STATUS_READY)

    def test_delete_locked(self):
        pp = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED)

        with self.assertRaises(GraphQLError):
            PaymentPlanService(payment_plan=pp).delete()

    @freeze_time("2020-10-10")
    def test_create_validation_errors(self):
        targeting = TargetPopulationFactory()

        input_data = dict(
            business_area_slug="afghanistan",
            targeting_id=self.id_to_base64(targeting.id, "Targeting"),
            start_date=parse_date("2021-10-10"),
            end_date=parse_date("2021-12-10"),
            dispersion_start_date=parse_date("2020-09-10"),
            dispersion_end_date=parse_date("2020-09-11"),
            currency="USD",
        )

        with self.assertRaisesMessage(GraphQLError, "PaymentPlan can not be created in provided Business Area"):
            pp = PaymentPlanService().create(input_data=input_data, user=self.user)
        self.business_area.is_payment_plan_applicable = True
        self.business_area.save()

        with self.assertRaisesMessage(
            GraphQLError, f"TargetPopulation id:{targeting.id} does not exist or is not in status Ready"
        ):
            pp = PaymentPlanService().create(input_data=input_data, user=self.user)
        targeting.status = TargetPopulation.STATUS_READY
        targeting.save()

        with self.assertRaisesMessage(GraphQLError, "TargetPopulation should have related Program defined"):
            pp = PaymentPlanService().create(input_data=input_data, user=self.user)
        targeting.program = ProgramFactory()
        targeting.save()

        with self.assertRaisesMessage(
            GraphQLError, f"Dispersion End Date [{input_data['dispersion_end_date']}] cannot be a past date"
        ):
            pp = PaymentPlanService().create(input_data=input_data, user=self.user)

    @freeze_time("2020-10-10")
    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_create(self, get_exchange_rate_mock):
        targeting = TargetPopulationFactory()

        self.business_area.is_payment_plan_applicable = True
        self.business_area.save()

        targeting.status = TargetPopulation.STATUS_READY
        targeting.program = ProgramFactory()

        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        primary_collector_1 = IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        primary_collector_2 = IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)

        targeting.households.set([hh1, hh2])
        targeting.save()

        input_data = dict(
            business_area_slug="afghanistan",
            targeting_id=self.id_to_base64(targeting.id, "Targeting"),
            start_date=parse_date("2021-10-10"),
            end_date=parse_date("2021-12-10"),
            dispersion_start_date=parse_date("2020-09-10"),
            dispersion_end_date=parse_date("2020-11-10"),
            currency="USD",
        )

        pp = PaymentPlanService().create(input_data=input_data, user=self.user)

        pp.refresh_from_db()
        self.assertEqual(pp.target_population.status, TargetPopulation.STATUS_ASSIGNED)
        self.assertEqual(pp.total_households_count, 2)
        self.assertEqual(pp.total_individuals_count, 4)
        self.assertEqual(pp.payments.count(), 2)

    @freeze_time("2020-10-10")
    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_update_validation_errors(self, get_exchange_rate_mock):
        pp = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED)
        new_targeting = TargetPopulationFactory()

        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        primary_collector_1 = IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        primary_collector_2 = IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)
        new_targeting.households.set([hh1, hh2])
        new_targeting.save()

        input_data = dict(
            targeting_id=self.id_to_base64(new_targeting.id, "Targeting"),
            start_date=parse_date("2021-10-10"),
            end_date=parse_date("2021-12-10"),
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
        new_targeting.status = TargetPopulation.STATUS_READY
        new_targeting.save()

        with self.assertRaisesMessage(GraphQLError, "TargetPopulation should have related Program defined"):
            pp = PaymentPlanService(payment_plan=pp).update(input_data=input_data)
        new_targeting.program = ProgramFactory()
        new_targeting.save()

        with self.assertRaisesMessage(
            GraphQLError, f"Dispersion End Date [{input_data['dispersion_end_date']}] cannot be a past date"
        ):
            pp = PaymentPlanService(payment_plan=pp).update(input_data=input_data)

    @freeze_time("2020-10-10")
    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_update(self, get_exchange_rate_mock):
        pp = PaymentPlanFactory()
        hoh1 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        p1 = PaymentFactory(payment_plan=pp, excluded=False, household=hh1)
        self.assertEqual(pp.payments.count(), 1)

        new_targeting = TargetPopulationFactory()
        new_targeting.status = TargetPopulation.STATUS_READY
        new_targeting.program = ProgramFactory()
        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        primary_collector_1 = IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        primary_collector_2 = IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)
        new_targeting.households.set([hh1, hh2])
        new_targeting.save()

        with freeze_time("2020-11-10"):  # just to compare updated_at
            # test start_date update
            old_pp_updated_at = pp.updated_at
            old_pp_start_date = pp.start_date
            updated_pp_1 = PaymentPlanService(payment_plan=pp).update(
                input_data=dict(start_date=parse_date("2021-12-10"))
            )
            updated_pp_1.refresh_from_db()
            self.assertNotEqual(old_pp_updated_at, updated_pp_1.updated_at)
            self.assertEqual(updated_pp_1.payments.count(), 1)
            self.assertNotEqual(old_pp_start_date, updated_pp_1.start_date)

            # test targeting update, payments recreation triggered
            old_pp_targeting = updated_pp_1.target_population
            old_pp_exchange_rate = updated_pp_1.exchange_rate
            old_pp_total_households_count = updated_pp_1.total_households_count

            updated_pp_2 = PaymentPlanService(payment_plan=pp).update(
                input_data=dict(targeting_id=self.id_to_base64(new_targeting.id, "Targeting"))
            )
            updated_pp_2.refresh_from_db()
            self.assertNotEqual(old_pp_exchange_rate, updated_pp_2.exchange_rate)
            self.assertNotEqual(old_pp_total_households_count, updated_pp_2.total_households_count)
            self.assertEqual(updated_pp_2.payments.count(), 2)
            self.assertEqual(updated_pp_2.target_population, new_targeting)
            self.assertEqual(updated_pp_2.target_population.status, TargetPopulation.STATUS_ASSIGNED)
            self.assertEqual(updated_pp_2.program, updated_pp_2.target_population.program)
            self.assertEqual(old_pp_targeting.status, TargetPopulation.STATUS_READY)
