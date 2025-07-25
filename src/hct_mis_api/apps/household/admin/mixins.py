from typing import Iterable
from uuid import UUID

from django.contrib import messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.db.models import QuerySet
from django.db.transaction import atomic
from django.forms import Form
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils import timezone

from admin_extra_buttons.decorators import button

from hct_mis_api.apps.household.forms import (
    MassRestoreForm,
    MassWithdrawForm,
    WithdrawForm,
)
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.household.services.household_withdraw import HouseholdWithdraw


class HouseholdWithDrawnMixin:
    def _toggle_withdraw_status(
        self,
        request: HttpRequest,
        hh: Household,
        tickets: Iterable | None = None,
        comment: str | None = None,
        tag: str | None = None,
    ) -> HouseholdWithdraw:
        from hct_mis_api.apps.grievance.models import GrievanceTicket

        if tickets is None:
            tickets = GrievanceTicket.objects.belong_household(hh)
            if hh.withdrawn:
                tickets = filter(
                    lambda t: t.ticket.extras.get("status_before_withdrawn", False),
                    tickets,
                )
            else:
                tickets = filter(lambda t: t.ticket.status != GrievanceTicket.STATUS_CLOSED, tickets)
        service = HouseholdWithdraw(hh)
        service.change_tickets_status(tickets)
        if hh.withdrawn:
            service.unwithdraw()
            message = "{target} has been restored by {user}. {comment}"
            ticket_message = "Ticket reopened due to Household restore"
        else:
            service.withdraw(tag=tag)
            message = "{target} has been withdrawn by {user}. {comment}"
            ticket_message = "Ticket closed due to Household withdrawn"

        for individual in service.individuals:
            self.log_change(
                request,
                individual,
                message.format(target="Individual", user=request.user.username, comment=comment),
            )

        for ticket in tickets:
            self.log_change(request, ticket.ticket, ticket_message)
        self.log_change(
            request,
            hh,
            message.format(target="Household", user=request.user.username, comment=comment),
        )

        return service

    def has_withdrawn_permission(self, request: HttpRequest) -> bool:
        return request.user.has_perm("household.can_withdrawn")

    def mass_withdraw(self, request: HttpRequest, qs: QuerySet) -> TemplateResponse | None:
        context = self.get_common_context(request, title="Withdrawn")
        context["op"] = "withdraw"
        context["action"] = "mass_withdraw"
        context["ticket_operation"] = "close any ticket related to the household or his members"
        results = 0
        if "apply" in request.POST:
            form = MassWithdrawForm(request.POST)
            if form.is_valid():
                with atomic():
                    for hh in qs.filter(withdrawn=False):
                        service = self._toggle_withdraw_status(
                            request,
                            hh,
                            tag=form.cleaned_data["tag"],
                            comment=form.cleaned_data["reason"],
                        )
                        if service.household.withdraw:
                            results += 1
                self.message_user(request, f"Changed {results} Households.")
                return None
            context["form"] = form
            return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)
        context["form"] = MassWithdrawForm(
            initial={
                "_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME),
                "reason": "",
                "tag": "",
            }
        )
        return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)

    mass_withdraw.allowed_permissions = ["household.can_withdrawn"]

    def mass_unwithdraw(self, request: HttpRequest, qs: QuerySet) -> TemplateResponse | None:
        context = self.get_common_context(request, title="Restore")
        context["action"] = "mass_unwithdraw"
        context["op"] = "restore"
        context["ticket_operation"] = "reopen any previously closed tickets relating to the household or its members"
        context["queryset"] = qs
        results = 0
        if "apply" in request.POST:
            form = MassRestoreForm(request.POST)
            if form.is_valid():
                with atomic():
                    if form.cleaned_data["reopen_tickets"]:
                        tickets = None
                    else:
                        tickets = []
                    for hh in qs.filter(withdrawn=True):
                        service = self._toggle_withdraw_status(
                            request,
                            hh,
                            tickets=tickets,
                            comment=form.cleaned_data["reason"],
                        )
                        if not service.household.withdraw:
                            results += 1
                self.message_user(request, f"Changed {results} Households.")
                return None
            context["form"] = form
            return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)
        context["form"] = MassRestoreForm(
            initial={
                "reopen_tickets": True,
                "_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME),
            }
        )
        return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)

    mass_withdraw.allowed_permissions = ["withdrawn"]

    @button(permission="household.can_withdrawn")
    def withdraw(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect | TemplateResponse:
        from hct_mis_api.apps.grievance.models import GrievanceTicket

        context = self.get_common_context(request, pk)

        obj: Household = context["original"]
        context["status"] = "" if obj.withdrawn else "checked"

        tickets = GrievanceTicket.objects.belong_household(obj)
        if obj.withdrawn:
            msg = "Household successfully restored"
            context["title"] = "Restore"
            tickets = filter(lambda t: t.ticket.extras.get("status_before_withdrawn", False), tickets)
        else:
            context["title"] = "Withdrawn"
            msg = "Household successfully withdrawn"
            tickets = filter(lambda t: t.ticket.status != GrievanceTicket.STATUS_CLOSED, tickets)
        form: Form | WithdrawForm
        if request.method == "POST":
            form = WithdrawForm(request.POST)
            if form.is_valid():
                try:
                    with atomic():
                        self._toggle_withdraw_status(request, obj, tickets, tag=form.cleaned_data["tag"])
                        self.message_user(request, msg, messages.SUCCESS)
                        return HttpResponseRedirect(request.path)
                except Exception as e:
                    self.message_user(request, str(e), messages.ERROR)
        else:
            context["form"] = (
                Form() if obj.withdrawn else WithdrawForm(initial={"tag": timezone.now().strftime("%Y%m%d%H%M%S")})
            )

        context["tickets"] = tickets
        return TemplateResponse(request, "admin/household/household/withdrawn.html", context)
