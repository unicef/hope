from datetime import datetime

from django.core.mail import send_mail
from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string
from openpyxl import load_workbook

from sanction_list.models import UploadedXLSXFile, SanctionListIndividual


class CheckAgainstSanctionListTask:
    def execute(self, uploaded_file_id):
        uploaded_file = UploadedXLSXFile.objects.get(id=uploaded_file_id)
        wb = load_workbook(uploaded_file.file, data_only=True)
        sheet = wb.worksheets[0]
        headers = [cell.value for cell in sheet[1] if cell.value]
        filter_query = Q()

        for row in sheet.iter_rows(min_row=2):
            if not any([cell.value for cell in row]):
                continue

            filter_values = {
                "first_name": {
                    "value": None,
                    "lookup_expr": "first_name__iexact",
                },
                "second_name": {
                    "value": None,
                    "lookup_expr": "second_name__iexact",
                },
                "third_name": {
                    "value": None,
                    "lookup_expr": "third_name__iexact",
                },
                "date_of_birth": {
                    "value": None,
                    "lookup_expr": "date_of_birth",
                },
                "year_of_birth": {
                    "value": None,
                    "lookup_expr": "year_of_birth__lte",
                },
                "second_year_of_birth": {
                    "value": None,
                    "lookup_expr": "second_year_of_birth__gte",
                },
            }

            for cell, header in zip(row, headers):
                value = cell.value
                header_as_key = header.replace(" ", "_").lower().strip()
                if header_as_key == "date_of_birth":
                    if isinstance(value, (int, float, str)):
                        value = int(value)
                        if value:
                            filter_values["year_of_birth"]["value"] = value
                            filter_values["second_year_of_birth"][
                                "value"
                            ] = value
                            continue

                    elif isinstance(value, datetime):
                        value = value.date()
                if value:
                    filter_values[header_as_key]["value"] = value

            query = Q(
                **{
                    data_dict["lookup_expr"]: data_dict["value"]
                    for data_dict in filter_values.values()
                    if data_dict["value"] is not None
                }
            )

            filter_query |= query

        result = SanctionListIndividual.objects.order_by("first_name").filter(
            filter_query
        )

        if not result.exists():
            return

        send_mail(
            "Sanction List Check",
            render_to_string(
                "sanction_list/check_results.html",
                {"results": result, "results_count": result.count()},
            ),
            settings.EMAIL_HOST_USER,
            [uploaded_file.associated_email],
        )
