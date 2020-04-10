from django.http import HttpResponse
from openpyxl.writer.excel import save_virtual_workbook

from registration_datahub.template_generator import TemplateFileGenerator


def download_template(request):
    mimetype = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = "registration_data_import_template.xlsx"
    response = HttpResponse(content_type=mimetype)
    response["Content-Disposition"] = f"attachment; filename={filename}"
    response.write(
        save_virtual_workbook(TemplateFileGenerator.get_template_file())
    )

    return response
