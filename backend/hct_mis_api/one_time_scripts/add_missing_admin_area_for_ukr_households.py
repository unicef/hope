import csv
import os

from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import Household


def update_admin_area_for_households() -> None:
    households_admin_area_file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "files",
        "admin_areas_for_UKR_HH.csv",
    )
    with open(households_admin_area_file_path) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=";")
        for row in csv_reader:
            if household := Household.objects.filter(unicef_id=row["unicef_id"]).first():
                household.admin1 = Area.objects.filter(p_code=row["admin1_area_id"]).first()
                household.admin2 = Area.objects.filter(p_code=row["admin2_area_id"]).first()
                household.admin3 = Area.objects.filter(p_code=row["admin3_area_id"]).first()
                household.save(update_fields=["admin1", "admin2", "admin3"])
        print("Updated admin areas for specified UKR households")
