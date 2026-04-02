from hope.api.caches import (
    AreaLimitKeyBit,
    BusinessAreaAndProgramKeyBitMixin,
    KeyConstructorMixin,
)


class GrievanceTicketListKeyBit(BusinessAreaAndProgramKeyBitMixin):
    specific_view_cache_key = "grievance_ticket_list"


class GrievanceTicketListKeyConstructor(KeyConstructorMixin):
    ticket_list = GrievanceTicketListKeyBit()
    area_limits = AreaLimitKeyBit()
