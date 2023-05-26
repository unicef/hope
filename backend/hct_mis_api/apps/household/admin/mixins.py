from typing import Iterable, Optional, Union
from uuid import UUID

from django.contrib import messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.db.models import QuerySet
from django.db.transaction import atomic
from django.forms import Form
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone

from admin_extra_buttons.decorators import button

from hct_mis_api.apps.household.forms import (
    AddToTargetPopulationForm,
    CreateTargetPopulationForm,
    MassRestoreForm,
    MassWithdrawForm,
    RestoreForm,
    WithdrawForm,
)
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.household.services.household_withdraw import HouseholdWithdraw
from hct_mis_api.apps.targeting.services.targeting_stats_refresher import refresh_stats


class HouseholdWithDrawnMixin:
    def _toggle_withdraw_status(
        self,
        request: HttpRequest,
        hh: Household,
        tickets: Optional[Iterable] = None,
        comment: Optional[str] = None,
        tag: Optional[str] = None,
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

    def mass_withdraw(self, request: HttpRequest, qs: QuerySet) -> Optional[TemplateResponse]:
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
            else:
                context["form"] = form
                return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)
        else:
            context["form"] = MassWithdrawForm(
                initial={
                    "_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME),
                    "reason": "",
                    "tag": "",
                }
            )
            return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)

    mass_withdraw.allowed_permissions = ["household.can_withdrawn"]

    def mass_unwithdraw(self, request: HttpRequest, qs: QuerySet) -> Optional[TemplateResponse]:
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
            else:
                context["form"] = form
                return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)
        else:
            context["form"] = RestoreForm(
                initial={
                    "reopen_tickets": True,
                    "_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME),
                }
            )
            return TemplateResponse(request, "admin/household/household/mass_withdrawn.html", context)

    mass_withdraw.allowed_permissions = ["withdrawn"]

    @button(permission="household.can_withdrawn")
    def withdraw(self, request: HttpRequest, pk: UUID) -> Union[HttpResponseRedirect, TemplateResponse]:
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
        form: Union[Form, WithdrawForm]
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


class CustomTargetPopulationMixin:
    def add_to_target_population(self, request: HttpRequest, qs: QuerySet) -> Optional[HttpResponse]:
        from hct_mis_api.apps.core.models import BusinessArea
        from hct_mis_api.apps.targeting.models import TargetPopulation

        context = self.get_common_context(request, title="Extend TargetPopulation")
        tp: TargetPopulation
        ba: BusinessArea
        if "apply" in request.POST:
            form = AddToTargetPopulationForm(request.POST, read_only=True)
            if form.is_valid():
                tp = form.cleaned_data["target_population"]
                ba = tp.business_area
                population = qs.filter(business_area=ba)
                context["target_population"] = tp
                context["population"] = population
                context["queryset"] = qs
                if population.count() != qs.count():
                    context["mixed_household"] = True
        elif "confirm" in request.POST:
            form = AddToTargetPopulationForm(request.POST)
            if form.is_valid():
                tp = form.cleaned_data["target_population"]
                ba = tp.business_area
                population = qs.filter(business_area=ba)
                with atomic():
                    tp.households.add(*population)
                    refresh_stats(tp)
                    tp.save()
                url = reverse("admin:targeting_targetpopulation_change", args=[tp.pk])
                return HttpResponseRedirect(url)
        else:
            form = AddToTargetPopulationForm(
                initial={
                    "_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME),
                    "action": "add_to_target_population",
                }
            )
        context["form"] = form
        return TemplateResponse(request, "admin/household/household/add_target_population.html", context)

    add_to_target_population.allowed_permissions = ["create_target_population"]

    def create_target_population(self, request: HttpRequest, qs: QuerySet) -> Optional[HttpResponse]:
        context = self.get_common_context(request, title="Create TargetPopulation")
        if "apply" in request.POST:
            form = CreateTargetPopulationForm(request.POST, read_only=True)
            if form.is_valid():
                program = form.cleaned_data["program"]
                ba = program.business_area
                population = qs.filter(business_area=ba)
                context["program"] = program
                context["population"] = population
                context["queryset"] = qs
                if population.count() != qs.count():
                    context["mixed_household"] = True
        elif "confirm" in request.POST:
            form = CreateTargetPopulationForm(request.POST)
            if form.is_valid():
                from hct_mis_api.apps.targeting.models import TargetPopulation

                program = form.cleaned_data["program"]
                ba = program.business_area
                population = qs.filter(business_area=ba)
                with atomic():
                    tp = TargetPopulation.objects.create(
                        targeting_criteria=None,
                        created_by=request.user,
                        name=form.cleaned_data["name"],
                        business_area=ba,
                        program=program,
                    )
                    tp.households.set(population)
                    refresh_stats(tp)
                    tp.save()
                url = reverse("admin:targeting_targetpopulation_change", args=[tp.pk])
                return HttpResponseRedirect(url)
        else:
            form = CreateTargetPopulationForm(
                initial={
                    "_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME),
                    "action": "create_target_population",
                }
            )
        context["form"] = form
        return TemplateResponse(request, "admin/household/household/create_target_population.html", context)

    create_target_population.allowed_permissions = ["create_target_population"]

    def has_create_target_population_permission(self, request: HttpRequest) -> bool:
        return request.user.has_perm("targeting.add_target_population")
