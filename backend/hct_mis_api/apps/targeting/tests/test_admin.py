from hct_mis_api.apps.household.tests.test_admin import BaseTest
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory


# temporary added test for AutoCompleteFilterTemp have to be removed after fix in AutoCompleteFilter
class HouseholdSelectionAdminTest(BaseTest):
    def test_household_selection_filtering_by_targeting(self) -> None:
        base_url = "/api/unicorn/targeting/householdselection/"
        targeting_removed = TargetPopulationFactory(name="Test TP for test", is_removed=True)
        targeting_1 = TargetPopulationFactory(name="Test TP for test 222")
        self.assertTrue(targeting_removed.is_removed)
        self.assertFalse(targeting_1.is_removed)

        # removed tp
        url = f"{base_url}?&target_population__exact={str(targeting_removed.id)}"
        res = self.app.get(url, user=self.superuser)  # noqa: F841
        self.assertEqual(res.status_code, 200)

        url = f"{base_url}?&target_population__exact={str(targeting_1.id)}"
        res = self.app.get(url, user=self.superuser)  # noqa: F841
        self.assertEqual(res.status_code, 200)

        # invalid id
        url = f"{base_url}?&target_population__exact=00000000-1111-0000-1111-faceb00c1111"
        res = self.app.get(url, user=self.superuser)  # noqa: F841
        self.assertEqual(res.status_code, 200)
