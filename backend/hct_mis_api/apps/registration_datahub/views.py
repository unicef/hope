from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

from django.http import HttpRequest, HttpResponse

from hct_mis_api.apps.registration_datahub.template_generator import (
    TemplateFileGenerator,
)


def download_template(request: HttpRequest) -> HttpResponse:
    parse_result = urlparse(request.headers["Referer"])
    business_area_slug = parse_result.path[1:].split("/")[0]

    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = "registration_data_import_template.xlsx"
    response = HttpResponse(content_type=mimetype)
    response["Content-Disposition"] = f"attachment; filename={filename}"

    wb = TemplateFileGenerator.get_template_file(business_area_slug)
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = bytes(tmp.read())

    response.write(file)
    return response
