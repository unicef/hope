import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from openpyxl.writer.excel import save_virtual_workbook

from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.targeting.services.xlsx_export_targeting_service import XlsxExportTargetingService

logger = logging.getLogger(__name__)


@staff_member_required
def download_xlsx_households(request, target_population_id):
    target_population = get_object_or_404(TargetPopulation, id=target_population_id)
    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = f"{target_population.name}.xlsx"
    response = HttpResponse(content_type=mimetype)
    response["Content-Disposition"] = f"attachment; filename={filename}"
    service = XlsxExportTargetingService(target_population)
    response.write(save_virtual_workbook(service.generate_workbook()))

    return response
