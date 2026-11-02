from typing import Any

from django.db.models import Max
from rest_framework.request import Request
from rest_framework_extensions.key_constructor.bits import KeyBitBase

from hope.api.caches import (
    AreaLimitKeyBit,
    BusinessAreaAndProgramKeyBitMixin,
    KeyConstructorMixin,
)
from hope.apps.grievance.constants import MY_TASKS_TABS
from hope.apps.grievance.models import TicketSeen


class GrievanceTicketListKeyBit(BusinessAreaAndProgramKeyBitMixin):
    specific_view_cache_key = "grievance_ticket_list"


class MyTasksUnreadKeyBit(KeyBitBase):
    """A My Tasks list is per user and changes when they open a ticket, so neither may share a cache entry."""

    def get_data(  # noqa: PLR0913, PLR0917 – override of base method signature
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Request,
        args: tuple,
        kwargs: dict,
    ) -> str:
        if request.GET.get("my_tasks_tab") not in MY_TASKS_TABS:
            return ""
        last_seen = TicketSeen.objects.filter(user=request.user).aggregate(last=Max("seen_at"))["last"]
        return f"{request.user.pk}:{last_seen}"


class GrievanceTicketListKeyConstructor(KeyConstructorMixin):
    ticket_list = GrievanceTicketListKeyBit()
    area_limits = AreaLimitKeyBit()
    my_tasks_unread = MyTasksUnreadKeyBit()
