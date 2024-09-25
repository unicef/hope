import logging
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.targeting.services.xlsx_export_targeting_service import (
    XlsxExportTargetingService,
)

if TYPE_CHECKING:
    from uuid import UUID


logger = logging.getLogger(__name__)


@staff_member_required
def download_xlsx_households(request: HttpRequest, target_population_id: "UUID") -> HttpResponse:
    target_population = get_object_or_404(TargetPopulation, id=target_population_id)
    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = f"{target_population.name}.xlsx"
    response = HttpResponse(content_type=mimetype)
    response["Content-Disposition"] = f"attachment; filename={filename}"
    service = XlsxExportTargetingService(target_population)
    wb = service.generate_workbook()
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = bytes(tmp.read())
    response.write(file)

    return response
