from typing import TYPE_CHECKING

from django.urls import reverse
from django_webtest import WebTest

from extras.test_utils.factories.account import BusinessAreaFactory, UserFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory

if TYPE_CHECKING:
    from hope.models.user import User


class BaseTest(WebTest):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        business_area = BusinessAreaFactory(name="Test")
        program = ProgramFactory(business_area=business_area)
        registration_data_import = RegistrationDataImportFactory()

        cls.household = HouseholdFactory.build(
            registration_data_import=registration_data_import,
            business_area=business_area,
            program=program,
        )
        cls.household.household_collection.save()
        cls.individual = IndividualFactory(
            registration_data_import=registration_data_import,
            household=cls.household,
            program=program,
        )
        cls.household.head_of_household = cls.individual
        cls.household.save()

        cls.user = UserFactory()
        cls.superuser: User = UserFactory(is_superuser=True, is_staff=True)


class HouseholdAdminTest(BaseTest):
    def test_hh_change(self) -> None:
        url = reverse("admin:household_household_change", args=[self.household.pk])
        res = self.app.get(url, user=self.superuser)  # noqa: F841


class IndividualAdminTest(BaseTest):
    def test_individual_change(self) -> None:
        url = reverse("admin:household_individual_change", args=[self.individual.pk])
        res = self.app.get(url, user=self.superuser)  # noqa: F841
