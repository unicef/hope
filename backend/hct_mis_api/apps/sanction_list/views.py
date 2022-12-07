from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse

from openpyxl.writer.excel import save_virtual_workbook

from hct_mis_api.apps.sanction_list.template_generator import TemplateFileGenerator


@login_required
def download_sanction_template(request: HttpRequest) -> HttpResponse:
    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = "sanction_list_check_template.xlsx"
    response = HttpResponse(content_type=mimetype)
    response["Content-Disposition"] = f"attachment; filename={filename}"
    response.write(save_virtual_workbook(TemplateFileGenerator.get_template_file()))

    return response
