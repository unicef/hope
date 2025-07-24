from typing import Any, Optional

from django.db.models import QuerySet

from hct_mis_api.api.caches import (
    AreaLimitKeyBit,
    BusinessAreaAndProgramLastUpdatedKeyBit,
    KeyConstructorMixin,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket


class GrievanceTicketListKeyBit(BusinessAreaAndProgramLastUpdatedKeyBit):
    specific_view_cache_key = "grievance_ticket_list"

    def _get_queryset(
        self, business_area_slug: Optional[Any], program_slug: Optional[Any], view_instance: Optional[Any]
    ) -> QuerySet:
        return GrievanceTicket.objects.filter(
            ignored=False,
            programs__slug__in=[program_slug],
            business_area__slug=business_area_slug,
        )


class GrievanceTicketListKeyConstructor(KeyConstructorMixin):
    household_list = GrievanceTicketListKeyBit()
    area_limits = AreaLimitKeyBit()
