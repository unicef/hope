from typing import Any, Dict, Optional, Sequence, Tuple, Union
from uuid import UUID

from django.conf import settings
from django.contrib import admin
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.db.models import JSONField, QuerySet
from django.http import HttpRequest, HttpResponse

from admin_extra_buttons.buttons import Button
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin, confirm_action
from adminactions.helpers import AdminActionPermMixin
from adminfilters.mixin import AdminFiltersMixin
from jsoneditor.forms import JSONEditor
from smart_admin.mixins import DisplayAllMixin as SmartDisplayAllMixin

from hct_mis_api.apps.administration.widgets import JsonWidget
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.utils.security import is_root


class SoftDeletableAdminMixin(admin.ModelAdmin):
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = self.model.all_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_list_filter(self, request: HttpRequest) -> Tuple:
        return tuple(list(super().get_list_filter(request)) + ["is_removed"])


class IsOriginalAdminMixin(admin.ModelAdmin):
    def get_list_filter(self, request: HttpRequest) -> Tuple:
        return tuple(list(super().get_list_filter(request)) + ["is_original"])


class JSONWidgetMixin:
    json_enabled = False

    def formfield_for_dbfield(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if isinstance(db_field, JSONField):
            if is_root(request) or settings.DEBUG or self.json_enabled:
                kwargs = {"widget": JSONEditor}
            else:
                kwargs = {"widget": JsonWidget}
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class LastSyncDateResetMixin:
    @button()
    def reset_sync_date(self, request: HttpRequest) -> Optional[HttpResponse]:
        if request.method == "POST":
            self.get_queryset(request).update(last_sync_at=None)
        else:
            return confirm_action(
                self,
                request,
                self.reset_sync_date,
                "Continuing will reset all records last_sync_date field.",
                "Successfully executed",
                title="aaaaa",
            )
        return None

    @button(label="reset sync date")
    def reset_sync_date_single(self, request: HttpRequest, pk: UUID) -> Optional[HttpResponse]:
        if request.method == "POST":
            self.get_queryset(request).filter(id=pk).update(last_sync_at=None)
        else:
            return confirm_action(
                self,
                request,
                self.reset_sync_date,
                "Continuing will reset last_sync_date field.",
                "Successfully executed",
            )
        return None


class HopeModelAdminMixin(ExtraButtonsMixin, SmartDisplayAllMixin, AdminActionPermMixin, AdminFiltersMixin):
    pass


class HOPEModelAdminBase(HopeModelAdminMixin, JSONWidgetMixin, admin.ModelAdmin):
    list_per_page = 50

    def get_fields(self, request: HttpRequest, obj: Optional[Any] = None) -> Sequence[Union[str, Sequence[str]]]:
        return super().get_fields(request, obj)

    def get_actions(self, request: HttpRequest) -> Dict:
        actions = super().get_actions(request)
        if "delete_selected" in actions and not is_root(request):
            del actions["delete_selected"]
        return actions

    def count_queryset(self, request: HttpRequest, queryset: QuerySet) -> None:
        count = queryset.count()
        self.message_user(request, f"Selection contains {count} records")


class HUBBusinessAreaFilter(SimpleListFilter):
    parameter_name = "ba"
    title = "Business Area"
    template = "adminfilters/combobox.html"

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> QuerySet:
        from hct_mis_api.apps.core.models import BusinessArea

        return BusinessArea.objects.values_list("code", "name").distinct()

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value():
            return queryset.filter(session__business_area=self.value()).distinct()
        return queryset


class BusinessAreaForCollectionsListFilter(admin.SimpleListFilter):
    model_filter_field = "households__business_area__id"
    title = "business area"
    parameter_name = "business_area__exact"
    template = "adminfilters/combobox.html"

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> QuerySet:
        return BusinessArea.objects.all().values_list("id", "name")

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value():
            return queryset.filter(**{self.model_filter_field: self.value()}).distinct()
        return queryset


class BusinessAreaForHouseholdCollectionListFilter(BusinessAreaForCollectionsListFilter):
    model_filter_field = "households__business_area__id"


class BusinessAreaForIndividualCollectionListFilter(BusinessAreaForCollectionsListFilter):
    model_filter_field = "individuals__business_area__id"


def is_enabled(btn: Button) -> bool:
    return btn.request.user.is_superuser


def get_payment_plan_from_button_context(btn: Button) -> Optional[PaymentPlan]:
    if btn:
        payment_plan_id = btn.request.resolver_match.kwargs.get("object_id")
        return PaymentPlan.objects.get(id=payment_plan_id)
    return None


def is_payment_plan_in_status(btn: Button, status: str) -> bool:
    if payment_plan := get_payment_plan_from_button_context(btn):
        return payment_plan.status == status
    return False


def is_background_action_in_status(btn: Button, background_status: str) -> bool:
    if payment_plan := get_payment_plan_from_button_context(btn):
        return payment_plan.background_action_status == background_status
    return False


def is_preparing_payment_plan(btn: Button) -> bool:
    return is_payment_plan_in_status(btn, PaymentPlan.Status.PREPARING)


def is_locked_payment_plan(btn: Button) -> bool:
    return is_payment_plan_in_status(btn, PaymentPlan.Status.LOCKED)


def is_accepted_payment_plan(btn: Button) -> bool:
    return is_payment_plan_in_status(btn, PaymentPlan.Status.ACCEPTED)


def is_importing_entitlements_xlsx_file(btn: Button) -> bool:
    return is_background_action_in_status(btn, PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS)


def is_importing_reconciliation_xlsx_file(btn: Button) -> bool:
    return is_background_action_in_status(btn, PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION)


def is_exporting_xlsx_file(btn: Button) -> bool:
    return is_background_action_in_status(btn, PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING)


class PaymentPlanCeleryTasksMixin:
    @button(visible=lambda btn: is_preparing_payment_plan(btn), enabled=lambda btn: is_enabled(btn))
    def restart_preparing_payment_plan(self, request: HttpRequest, pk: UUID) -> Optional[HttpResponse]:
        """preparing Payment Plan"""

        if request.method == "POST":
            pass
        else:
            return confirm_action(
                modeladmin=self,
                request=request,
                action=self.restart_preparing_payment_plan,
                message="Do you confirm to restart payment plan task?",
                success_message="Successfully executed",
            )
        return None

    @button(
        visible=lambda btn: is_importing_entitlements_xlsx_file(btn) and is_locked_payment_plan(btn),
        enabled=lambda btn: is_enabled(btn),
    )
    def restart_importing_entitlements_xlsx_file(self, request: HttpRequest, pk: UUID) -> Optional[HttpResponse]:
        """importing entitlement file"""

        if request.method == "POST":
            pass
        else:
            return confirm_action(
                modeladmin=self,
                request=request,
                action=self.restart_importing_entitlements_xlsx_file,
                message="Do you confirm to restart importing entitlements xlsx file task?",
            )
        return None

    @button(
        visible=lambda btn: is_importing_reconciliation_xlsx_file(btn) and is_accepted_payment_plan(btn),
        enabled=lambda btn: is_enabled(btn),
    )
    def restart_importing_reconciliation_xlsx_file(self, request: HttpRequest, pk: UUID) -> Optional[HttpResponse]:
        """importing payment plan list (from xlsx)"""

        if request.method == "POST":
            pass
        else:
            return confirm_action(
                modeladmin=self,
                request=request,
                action=self.restart_importing_reconciliation_xlsx_file,
                message="Do you confirm to restart importing entitlements xlsx file task?",
            )
        return None

    @button(
        visible=lambda btn: is_exporting_xlsx_file(btn) and is_locked_payment_plan(btn),
        enabled=lambda btn: is_enabled(btn),
    )
    def restart_exporting_template_for_entitlement(self, request: HttpRequest, pk: UUID) -> Optional[HttpResponse]:
        """exporting template for entitlement"""

        if request.method == "POST":
            pass
        else:
            return confirm_action(
                modeladmin=self,
                request=request,
                action=self.restart_exporting_template_for_entitlement,
                message="Do you confirm to restart exporting xlsx file task?",
                success_message="Successfully executed",
            )
        return None

    @button(
        visible=lambda btn: is_exporting_xlsx_file(btn) and is_accepted_payment_plan(btn),
        enabled=lambda btn: is_enabled(btn),
    )
    def restart_exporting_exporting_payment_plan_list(self, request: HttpRequest, pk: UUID) -> Optional[HttpResponse]:
        """exporting payment plan list"""

        if request.method == "POST":
            pass
        else:
            return confirm_action(
                modeladmin=self,
                request=request,
                action=self.restart_exporting_exporting_payment_plan_list,
                message="Do you confirm to restart exporting xlsx file task?",
                success_message="Successfully executed",
            )
        return None
