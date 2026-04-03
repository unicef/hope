from typing import Any

from django.db.models import QuerySet

from hope.api.caches import (
    AreaLimitKeyBit,
    BusinessAreaAndProgramLastUpdatedKeyBit,
    KeyConstructorMixin,
)
from hope.apps.grievance.models import GrievanceTicket


class GrievanceTicketListKeyBit(BusinessAreaAndProgramLastUpdatedKeyBit):
    specific_view_cache_key = "grievance_ticket_list"

    def _get_queryset(
        self,
        business_area_slug: Any | None,
        program_code: Any | None,
        view_instance: Any | None,
    ) -> QuerySet:
        return GrievanceTicket.objects.filter(
            ignored=False,
            programs__code__in=[program_code],
            business_area__slug=business_area_slug,
        )


class GrievanceTicketListKeyConstructor(KeyConstructorMixin):
    ticket_list = GrievanceTicketListKeyBit()
    area_limits = AreaLimitKeyBit()
