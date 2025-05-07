from typing import Any, Optional

from django.db.models import QuerySet

from rest_framework_extensions.key_constructor.bits import KeyBitBase

from hct_mis_api.api.caches import (
    BusinessAreaAndProgramLastUpdatedKeyBit,
    KeyConstructorMixin, AreaLimitKeyBit,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import Household, Individual


class GrievanceTicketListKeyBit(BusinessAreaAndProgramLastUpdatedKeyBit):
    specific_view_cache_key = "grievance_ticket_list"

    def _get_queryset(
        self, business_area_slug: Optional[Any], program_slug: Optional[Any], view_instance: Optional[Any]
    ) -> QuerySet:
        return GrievanceTicket.object.filter(
            ignored=False,
            programs__slug__in=[program_slug],
            business_area__slug=business_area_slug,
        )

class GrievanceTicketListKeyConstructor(KeyConstructorMixin):
    household_list = GrievanceTicketListKeyBit()
    area_limits = AreaLimitKeyBit()
