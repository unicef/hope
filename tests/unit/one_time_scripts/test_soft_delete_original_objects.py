from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.one_time_scripts.soft_delete_original_objects import (
    soft_delete_original_objects,
)


class TestSoftDeleteOriginalObjects(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        program = ProgramFactory(business_area=cls.business_area)
        individual2 = IndividualFactory(household=None)
        cls.household = HouseholdFactory(
            program=program, business_area=cls.business_area, head_of_household=individual2
        )
        cls.individual = IndividualFactory(program=program, business_area=cls.business_area, household=None)
        cls.individual_role_in_hh = IndividualRoleInHouseholdFactory(
            household=cls.household, individual=IndividualFactory(household=None)
        )
        cls.document = DocumentFactory(individual=cls.individual)
        cls.individual_identity = IndividualIdentityFactory(individual=cls.individual)
        cls.bank_account_info = BankAccountInfoFactory(individual=cls.individual)

    def test_soft_delete_original_objects(self) -> None:
        soft_delete_original_objects()

        self.household.refresh_from_db()
        self.individual.refresh_from_db()
        self.individual_role_in_hh.refresh_from_db()
        self.document.refresh_from_db()
        self.individual_identity.refresh_from_db()
        self.bank_account_info.refresh_from_db()

        assert self.household.is_removed is False
        assert self.individual.is_removed is False
        assert self.individual_role_in_hh.is_removed is False
        assert self.document.is_removed is False
        assert self.individual_identity.is_removed is False
        assert self.bank_account_info.is_removed is False
