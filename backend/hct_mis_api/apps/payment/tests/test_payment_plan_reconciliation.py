# scenario:
# targeting is there
# payment plan is created
# locked
# entitlements calculated
# FSPs set
# FSP locked
# payments have FSPs assigned
# we receive reconciliations from FSPs
# once we have all, the payment plan is reconciliated
# once this is done, FSP (with limit) may be used in another payment plan


from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory, PaymentPlan
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory, TargetingCriteriaFactory, TargetPopulation


class TestPaymentPlanReconciliation(APITestCase):
    @classmethod
    def create_household_and_individual(cls):
        household, individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "business_area": cls.business_area,
            },
            individuals_data=[{}],
        )
        return household, individuals[0]

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(
            cls.user,
            [Permissions.PAYMENT_MODULE_CREATE, Permissions.PAYMENT_MODULE_VIEW_DETAILS],
            cls.business_area,
        )

        cls.registration_data_import = RegistrationDataImportFactory(business_area=cls.business_area)

        cls.household_1, cls.individual_1 = cls.create_household_and_individual()
        cls.household_2, cls.individual_2 = cls.create_household_and_individual()
        cls.household_3, cls.individual_3 = cls.create_household_and_individual()

    def test_receiving_reconciliations_from_fsp(self):
        target_population = TargetPopulationFactory(
            created_by=self.user,
            candidate_list_targeting_criteria=(TargetingCriteriaFactory()),
            business_area=self.business_area,
            status=TargetPopulation.STATUS_LOCKED,
        )

        self.payment_plan = PaymentPlanFactory(
            total_households_count=4, target_population=target_population, status=PaymentPlan.Status.LOCKED
        )

        # entitlement calculation
