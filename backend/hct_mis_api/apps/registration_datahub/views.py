from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

from django.http import HttpRequest, HttpResponse

from hct_mis_api.apps.registration_datahub.template_generator import (
    TemplateFileGenerator,
)


def download_template(request: HttpRequest) -> HttpResponse:
    # program = request.headers["Program"]
    # TODO: based on Program.DCT generate xlsx file
    parse_result = urlparse(request.headers["Referer"])
    business_area_slug = parse_result.path[1:].split("/")[0]

    is_program_for_social_worker = False

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
