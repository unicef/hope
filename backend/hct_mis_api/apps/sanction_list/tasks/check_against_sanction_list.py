from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.forms import model_to_dict
from django.template.loader import render_to_string
from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter
from openpyxl.writer.excel import save_virtual_workbook

from sanction_list.models import UploadedXLSXFile, SanctionListIndividual


class CheckAgainstSanctionListTask:
    @staticmethod
    def _get_row(data, row_num_mapping):
        for row_num, values in row_num_mapping.items():
            has_matching_names = (
                values["first_name"]["value"].lower()
                == data["first_name"].lower()
                and values["second_name"]["value"].lower()
                == data["second_name"].lower()
                and values["third_name"]["value"].lower()
                == data["third_name"].lower()
            )
            has_matching_dob = (
                values["date_of_birth"]["value"] is not None
                and values["date_of_birth"]["value"] == data["date_of_birth"]
            )
            if has_matching_names and has_matching_dob:
                return row_num

            has_matching_years = False
            all_values_exist = all(
                [
                    data["year_of_birth"],
                    data["second_year_of_birth"],
                    values["year_of_birth"]["value"],
                ]
            )
            if all_values_exist:
                has_matching_years = (
                    data["year_of_birth"]
                    <= values["year_of_birth"]["value"]
                    <= data["second_year_of_birth"]
                )
            if has_matching_names and has_matching_years:
                return row_num

    def execute(self, uploaded_file_id, original_file_name):
        today = datetime.now()
        uploaded_file = UploadedXLSXFile.objects.get(id=uploaded_file_id)
        wb = load_workbook(uploaded_file.file, data_only=True)
        sheet = wb.worksheets[0]
        headers = {cell.value: cell.column for cell in sheet[1] if cell.value}
        filter_query = Q()
        row_num_mapping = {}

        for index, row in enumerate(sheet.iter_rows(min_row=2)):
            if not any([cell.value for cell in row]):
                continue

            filter_values = {
                "first_name": {
                    "value": "",
                    "lookup_expr": "first_name__iexact",
                },
                "second_name": {
                    "value": "",
                    "lookup_expr": "second_name__iexact",
                },
                "third_name": {
                    "value": "",
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

            for cell, header in zip(row, headers.keys()):
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

            row_num_mapping[index] = {**filter_values}
            query = Q(
                **{
                    data_dict["lookup_expr"]: data_dict["value"]
                    for data_dict in filter_values.values()
                    if data_dict["value"]
                }
            )

            filter_query |= query

        raw_result = SanctionListIndividual.objects.order_by(
            "first_name"
        ).filter(filter_query)

        if not raw_result.exists():
            return

        result = [
            {
                **model_to_dict(individual),
                "row_number": self._get_row(
                    model_to_dict(individual), row_num_mapping
                ),
            }
            for individual in raw_result
        ]

        context = {
            "results": result,
            "results_count": len(result),
            "file_name": original_file_name,
            "today_date": datetime.now(),
        }
        text_body = render_to_string("sanction_list/check_results.txt", context)
        html_body = render_to_string(
            "sanction_list/check_results.html", context
        )
        subject = (
            f"Sanction List Check - file: {original_file_name}, "
            f"date: {today.strftime('%Y-%m-%d %I:%M %p')}"
        )

        attachment_wb = Workbook()
        attachment_ws = attachment_wb.active
        attachment_ws.title = "Sanction List Check Results"

        header_row_names = (
            "FIRST NAME",
            "SECOND NAME",
            "THIRD NAME",
            "DATE OF BIRTH",
            "ORIGINAL FILE ROW NUMBER",
        )
        attachment_ws.append(header_row_names)

        for individual in result:
            year_of_birth = ""
            if individual["year_of_birth"]:
                year_of_birth = (
                    individual["year_of_birth"]
                    if individual["year_of_birth"]
                    == individual["second_year_of_birth"]
                    else f"{individual['year_of_birth']} - "
                    f"{individual['second_year_of_birth']}"
                )
            attachment_ws.append(
                (
                    individual["first_name"],
                    individual["second_name"],
                    individual["third_name"],
                    individual["date_of_birth"] or year_of_birth,
                    individual["row_number"],
                )
            )
        for i in range(1, len(header_row_names) + 1):
            attachment_ws.column_dimensions[get_column_letter(i)].width = 30
        attachment = save_virtual_workbook(attachment_wb)

        msg = EmailMultiAlternatives(
            subject=subject,
            from_email=settings.EMAIL_HOST_USER,
            to=[uploaded_file.associated_email],
            body=text_body,
        )
        msg.attach(
            f"{subject}.xlsx", attachment, "application/vnd.ms-excel",
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
