from django.http import HttpResponse, HttpRequest

from openpyxl.writer.excel import save_virtual_workbook

from hct_mis_api.apps.registration_datahub.template_generator import (
    TemplateFileGenerator,
)


def download_template(request: HttpRequest) -> HttpResponse:
    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = "registration_data_import_template.xlsx"
    response = HttpResponse(content_type=mimetype)
    response["Content-Disposition"] = f"attachment; filename={filename}"
    response.write(save_virtual_workbook(TemplateFileGenerator.get_template_file()))

    return response
