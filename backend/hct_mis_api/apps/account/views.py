from datetime import datetime

from django.http import HttpResponse

from openpyxl.writer.excel import save_virtual_workbook

from hct_mis_api.apps.account.export_users_xlsx import ExportUsersXlsx


def download_exported_users(request, business_area_slug) -> HttpResponse:
    export_class = ExportUsersXlsx(business_area_slug=business_area_slug)
    wb = export_class.get_exported_users_file()
    if wb is None:
        return HttpResponse("Nothing to export", content_type="text/plain")

    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    today = datetime.today()
    filename = f"exported_users_{business_area_slug}_{today}.xlsx"
    response = HttpResponse(content_type=mimetype)
    response["Content-Disposition"] = f"attachment; filename={filename}"

    response.write(save_virtual_workbook(wb))

    return response
