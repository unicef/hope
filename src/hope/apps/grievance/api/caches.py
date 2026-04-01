from hope.api.caches import (
    AreaLimitKeyBit,
    BusinessAreaAndProgramKeyBitMixin,
    KeyConstructorMixin,
)


class GrievanceTicketListKeyBit(BusinessAreaAndProgramKeyBitMixin):
    specific_view_cache_key = "grievance_ticket_list"


class GrievanceTicketListKeyConstructor(KeyConstructorMixin):
    household_list = GrievanceTicketListKeyBit()
    area_limits = AreaLimitKeyBit()
