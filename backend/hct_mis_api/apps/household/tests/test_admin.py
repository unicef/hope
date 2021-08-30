from django.urls import reverse

from django_webtest import WebTest

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


class BaseTest(WebTest):
    def setUp(self):
        self.household = HouseholdFactory.build(business_area=BusinessAreaFactory())
        self.individual = IndividualFactory(household=self.household)
        self.household.head_of_household = self.individual
        self.household.registration_data_import = RegistrationDataImportFactory()
        self.household.save()

        self.user = UserFactory()
        self.superuser: User = UserFactory(is_superuser=True, is_staff=True)


class HouseholdAdminTest(BaseTest):
    def test_hh_change(self):
        url = reverse("admin:household_household_change", args=[self.household.pk])
        res = self.app.get(url, user=self.superuser)


class IndividualAdminTest(BaseTest):
    def test_individual_change(self):
        url = reverse("admin:household_individual_change", args=[self.individual.pk])
        res = self.app.get(url, user=self.superuser)
