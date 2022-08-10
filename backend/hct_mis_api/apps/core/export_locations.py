import csv
from typing import Union

from django.http import HttpResponse

from django_countries.fields import Country

from hct_mis_api.apps.core.models import AdminArea


class ExportLocations:
    fields = [
        "list_name",
        "name",
        "label:English(EN)",
        "label:French(FR)",
        "label:Arabic(AR)",
        "label:Spanish(ES)",
        "filter",
    ]

    def __init__(self, country):
        self._country = country
        self._file_name = "locations.csv"
        self._matrix: list[Union[list[str], dict[str, str]]] = [self.fields]

    def export_to_file(self):
        admin_areas = self._load_admin_areas()
        response = self._prepare_response()

        filter_field = {
            1: self.result_for_level_one,
            2: self.result_for_level_two,
        }

        for admin_area in admin_areas:
            self._extend_matrix(admin_area, filter_field)

        self._write_to_file(response)
        return response

    def _write_to_file(self, response):
        writer = csv.DictWriter(response, self._matrix[0], extrasaction="ignore")
        writer.writeheader()
        for row in self._matrix[1:]:
            writer.writerow(row)

    def _extend_matrix(self, admin_area, filter_field):
        admin_area_data = {
            "list_name": f"admin{admin_area.admin_area_level.admin_level}",
            "name": admin_area.p_code,
            "label:English(EN)": f"{admin_area.title} - {admin_area.p_code}",
            "label:French(FR)": "",
            "label:Arabic(AR)": "",
            "label:Spanish(ES)": "",
            "filter": filter_field[admin_area.admin_area_level.admin_level](admin_area),
        }
        self._matrix.append(admin_area_data)

    def _prepare_response(self):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={self._file_name}"
        return response

    def _load_admin_areas(self):
        return AdminArea.objects.filter(
            tree_id=self._country.tree_id, admin_area_level__admin_level__in=[1, 2]
        ).order_by("admin_area_level__admin_level")

    @staticmethod
    def result_for_level_one(area):
        return Country(area.parent.p_code).alpha3

    @staticmethod
    def result_for_level_two(area):
        return area.parent.p_code
