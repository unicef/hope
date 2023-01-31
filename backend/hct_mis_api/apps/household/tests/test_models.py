from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import create_household


class TestHousehold(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        area_type_level_1 = AreaTypeFactory(
            name="State1",
            area_level=1,
        )
        area_type_level_2 = AreaTypeFactory(
            name="State2",
            area_level=2,
        )
        area_type_level_3 = AreaTypeFactory(
            name="State3",
            area_level=3,
        )
        area_type_level_4 = AreaTypeFactory(
            name="State4",
            area_level=4,
        )
        cls.area1 = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code="area1")
        cls.area2 = AreaFactory(name="City Test2", area_type=area_type_level_2, p_code="area2", parent=cls.area1)
        cls.area3 = AreaFactory(name="City Test3", area_type=area_type_level_3, p_code="area3", parent=cls.area2)
        cls.area4 = AreaFactory(name="City Test4", area_type=area_type_level_4, p_code="area4", parent=cls.area3)

    def test_household_admin_areas_set(self) -> None:
        household, (individual) = create_household(household_args={"size": 1, "business_area": self.business_area})
        household.admin_area = self.area1
        household.admin1 = self.area1
        household.save()

        household.set_admin_areas()
        household.refresh_from_db()

        self.assertEqual(household.admin_area, self.area1)
        self.assertEqual(household.admin1, self.area1)
        self.assertEqual(household.admin2, None)
        self.assertEqual(household.admin3, None)
        self.assertEqual(household.admin4, None)

        household.set_admin_areas(self.area4)
        household.refresh_from_db()

        self.assertEqual(household.admin_area, self.area4)
        self.assertEqual(household.admin1, self.area1)
        self.assertEqual(household.admin2, self.area2)
        self.assertEqual(household.admin3, self.area3)
        self.assertEqual(household.admin4, self.area4)

        household.set_admin_areas(self.area3)
        household.refresh_from_db()

        self.assertEqual(household.admin_area, self.area3)
        self.assertEqual(household.admin1, self.area1)
        self.assertEqual(household.admin2, self.area2)
        self.assertEqual(household.admin3, self.area3)
        self.assertEqual(household.admin4, None)
