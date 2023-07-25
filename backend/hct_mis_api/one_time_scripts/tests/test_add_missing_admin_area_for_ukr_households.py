import csv
import os
from io import StringIO
from unittest import mock

from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.one_time_scripts.add_missing_admin_area_for_ukr_households import (
    update_admin_area_for_households,
)


class TestUpdateAdminAreaFromFile(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.test_file_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "files",
            "test_file_admin_areas_for_UKR_HH.csv",
        )
        with open(cls.test_file_path) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=";")
            data = next(csv_reader)
            unicef_id = data["unicef_id"]
            admin1_area_id = data["admin1_area_id"]
            admin2_area_id = data["admin2_area_id"]
            admin3_area_id = data["admin3_area_id"]

        business_area = create_afghanistan()
        cls.household, _ = create_household(household_args={"business_area": business_area})
        cls.household.unicef_id = unicef_id
        cls.household.save()

        area_type_level_1 = AreaTypeFactory(name="State1", area_level=1)
        area_type_level_2 = AreaTypeFactory(name="State2", area_level=2)
        area_type_level_3 = AreaTypeFactory(name="State3", area_level=3)
        cls.area1 = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code=admin1_area_id)
        cls.area2 = AreaFactory(name="City Test2", area_type=area_type_level_2, p_code=admin2_area_id, parent=cls.area1)
        cls.area3 = AreaFactory(name="City Test3", area_type=area_type_level_3, p_code=admin3_area_id, parent=cls.area2)

    def test_update_household_admin_areas(self) -> None:
        with mock.patch("sys.stdout", new=StringIO()), mock.patch("os.path.join") as mock_join:
            mock_join.return_value = self.test_file_path
            update_admin_area_for_households()
        self.household.refresh_from_db()
        self.assertEqual(self.household.admin_area, self.area3)
        self.assertEqual(self.household.admin1, self.area1)
        self.assertEqual(self.household.admin2, self.area2)
        self.assertEqual(self.household.admin3, self.area3)
