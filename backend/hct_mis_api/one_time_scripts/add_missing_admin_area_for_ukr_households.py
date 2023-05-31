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
        admin_areas = {}
        for row in csv_reader:
            admin1_p_code, admin2_p_code, admin3_p_code = (
                row["admin1_area_id"],
                row["admin2_area_id"],
                row["admin3_area_id"],
            )
            for p_code in [admin1_p_code, admin2_p_code, admin3_p_code]:
                if p_code not in admin_areas:
                    admin_areas[p_code] = Area.objects.filter(p_code=p_code).first()
            updated = Household.objects.filter(unicef_id=row["unicef_id"]).update(
                admin_area=admin_areas[admin3_p_code],
                admin1=admin_areas[admin1_p_code],
                admin2=admin_areas[admin2_p_code],
                admin3=admin_areas[admin3_p_code],
            )
            if not updated:
                print(f"Household specified in the file is not found in the database ({row['unicef_id']})")
        print("Updated admin areas for specified UKR households")
