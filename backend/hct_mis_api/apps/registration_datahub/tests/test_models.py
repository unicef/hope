from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.registration_datahub.fixtures import ImportedHouseholdFactory


class TestImportedHousehold(TestCase):
    databases = {"default", "registration_datahub"}

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

    def test_admin_areas_set(self) -> None:
        imported_household = ImportedHouseholdFactory(admin1=self.area1.p_code, admin1_title=self.area1.name)
        imported_household.set_admin_areas()
        imported_household.save()
        imported_household.refresh_from_db()

        self.assertEqual(imported_household.admin_area, self.area1.p_code)
        self.assertEqual(imported_household.admin_area_title, self.area1.name)
        self.assertEqual(imported_household.admin1, self.area1.p_code)
        self.assertEqual(imported_household.admin1_title, self.area1.name)
        self.assertEqual(imported_household.admin2, "")
        self.assertEqual(imported_household.admin2_title, "")
        self.assertEqual(imported_household.admin3, "")
        self.assertEqual(imported_household.admin3_title, "")
        self.assertEqual(imported_household.admin4, "")
        self.assertEqual(imported_household.admin4_title, "")

        imported_household = ImportedHouseholdFactory(admin4=self.area4.p_code, admin4_title=self.area4.name)
        imported_household.set_admin_areas()
        imported_household.save()
        imported_household.refresh_from_db()

        self.assertEqual(imported_household.admin_area, self.area4.p_code)
        self.assertEqual(imported_household.admin_area_title, self.area4.name)
        self.assertEqual(imported_household.admin1, "")
        self.assertEqual(imported_household.admin1_title, "")
        self.assertEqual(imported_household.admin2, "")
        self.assertEqual(imported_household.admin2_title, "")
        self.assertEqual(imported_household.admin3, "")
        self.assertEqual(imported_household.admin3_title, "")
        self.assertEqual(imported_household.admin4, self.area4.p_code)
        self.assertEqual(imported_household.admin4_title, self.area4.name)
