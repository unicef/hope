from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.core.utils import get_program_id_from_headers
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_datahub.template_generator import (
    TemplateFileGenerator,
)


def download_template(request: HttpRequest) -> HttpResponse:
    program_id = get_program_id_from_headers(request.headers)
    parse_result = urlparse(request.headers["Referer"])
    business_area_slug = parse_result.path[1:].split("/")[0]
    if program_id:
        program = get_object_or_404(Program, id=program_id)
        is_program_for_social_worker = program.data_collecting_type.type == DataCollectingType.Type.SOCIAL
    else:
        # TODO change after FE update
        is_program_for_social_worker = True
    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = (
        "registration_data_import_template_social_worker.xlsx"
        if is_program_for_social_worker
        else "registration_data_import_template.xlsx"
    )
    response = HttpResponse(content_type=mimetype)
    response["Content-Disposition"] = f"attachment; filename={filename}"

    wb = TemplateFileGenerator.get_template_file(business_area_slug, is_program_for_social_worker)

    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = bytes(tmp.read())

    response.write(file)
    return response
