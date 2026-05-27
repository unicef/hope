from admin_extra_buttons.api import button, confirm_action
from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from hope.admin.utils import HOPEModelAdminBase
from hope.models import SanctionList


@admin.register(SanctionList)
class SanctionListAdmin(HOPEModelAdminBase):
    list_display = ("name",)
    search_fields = ("name",)

    @button(permission="sanction_list.refresh_sanction_list")
    def refresh(self, request: HttpRequest, pk: str) -> None:
        try:
            sl = SanctionList.objects.get(pk=pk)
            sl.strategy.refresh()
            self.message_user(request, "Sanction List refreshed", messages.SUCCESS)
        except KeyError:
            self.message_user(request, "Configuration Problem", messages.ERROR)

    @button(permission="sanction_list.empty_sanction_list")
    def empty(self, request: HttpRequest, pk: str) -> HttpResponse:
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
