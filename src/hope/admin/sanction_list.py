from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponseRedirect

from admin_extra_buttons.api import button, confirm_action

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.sanction_list.models import (
    SanctionList,
)


@admin.register(SanctionList)
class SanctionListAdmin(HOPEModelAdminBase):
    list_display = ("name",)

    @button()
    def refresh(self, request: HttpRequest, pk: str) -> None:
        try:
            sl = SanctionList.objects.get(pk=pk)
            sl.strategy.refresh()
            self.message_user(request, "Sanction List refreshed", messages.SUCCESS)
        except KeyError:
            self.message_user(request, "Configuration Problem", messages.ERROR)

    @button()
    def empty(self, request: HttpRequest, pk: str) -> None:
        sl = SanctionList.objects.get(pk=pk)

        def _delete(request: HttpRequest) -> HttpResponseRedirect:
            sl.entries.all().delete()
            return HttpResponseRedirect("..")

        return confirm_action(
            self,
            request,
            action=_delete,
            message="Continuing will delete all entries in this list",
            success_message="Sanction List emptied.",
            title="Empty sanction list",
        )
