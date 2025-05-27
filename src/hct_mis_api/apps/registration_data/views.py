from tempfile import NamedTemporaryFile

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.services.template_generator_service import \
    TemplateFileGeneratorService


def download_template(request: HttpRequest, program_id: str) -> HttpResponse:
    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = "registration_data_import_template.xlsx"
    response = HttpResponse(content_type=mimetype)
    response["Content-Disposition"] = f"attachment; filename={filename}"
    program = get_object_or_404(Program, id=program_id)
    template_generator_service = TemplateFileGeneratorService(program)
    wb = template_generator_service.create_workbook()
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = bytes(tmp.read())

    response.write(file)
    return response
