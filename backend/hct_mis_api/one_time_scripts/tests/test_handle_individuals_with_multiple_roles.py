from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import (
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    IndividualRoleInHousehold,
)
from hct_mis_api.one_time_scripts.handle_individuals_with_multiple_roles import (
    update_individuals_with_multiple_roles,
)


class TestHandleIndividualsWithMultipleRoles(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        business_area = create_afghanistan()
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={"size": 1, "business_area": business_area},
            individuals_data=[{}],
        )
        IndividualRoleInHouseholdFactory(household=cls.household, individual=cls.individuals[0], role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=cls.household, individual=cls.individuals[0], role=ROLE_ALTERNATE)

    def test_handle_individuals_with_multiple_roles_within_household(self) -> None:
        roles_count = IndividualRoleInHousehold.objects.filter(
            household=self.household, individual=self.individuals[0]
        ).count()
        self.assertEqual(roles_count, 2)
        update_individuals_with_multiple_roles()
        roles_count = IndividualRoleInHousehold.objects.filter(
            household=self.household, individual=self.individuals[0]
        ).count()
        self.assertEqual(roles_count, 1)
