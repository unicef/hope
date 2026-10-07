from datetime import datetime
from tempfile import NamedTemporaryFile

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.utils.http import content_disposition_header

from hope.apps.account.export_users_xlsx import ExportUsersXlsx
from hope.apps.account.permissions import Permissions, check_permissions


@login_required
def download_exported_users(request: HttpRequest, business_area_slug: str) -> HttpResponse:
    if not check_permissions(request.user, [Permissions.USER_MANAGEMENT_VIEW_LIST], business_area=business_area_slug):
        raise PermissionDenied
    export_class = ExportUsersXlsx(business_area_slug=business_area_slug)
    wb = export_class.get_exported_users_file()
    if wb is None:
        return HttpResponse("Nothing to export", content_type="text/plain")

    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    today = datetime.today()
    filename = f"exported_users_{business_area_slug}_{today}.xlsx"
    response = HttpResponse(content_type=mimetype)
    response["Content-Disposition"] = content_disposition_header(True, filename)

    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = bytes(tmp.read())
    response.write(file)

    return response
