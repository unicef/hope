from admin_extra_urls.api import action
from admin_extra_urls.mixins import ExtraUrlMixin
from adminfilters.filters import TextFieldFilter
from django.contrib import admin, messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.messages import DEFAULT_TAGS
from django.template.response import TemplateResponse
from django.urls import reverse

from hct_mis_api.apps.program.models import Program as HopeProgram
from hct_mis_api.apps.targeting.models import TargetPopulation as HopeTargetPopulation

from hct_mis_api.apps.cash_assist_datahub.models import (
    CashPlan,
    Session,
    TargetPopulation,
    Programme,
    ServiceProvider,
    PaymentRecord,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(Session)
class SessionAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_display = ("timestamp", "id", "source", "status", "last_modified_date", "business_area")
    date_hierarchy = "timestamp"
    list_filter = ("status", "source", TextFieldFilter.factory("business_area"))
    ordering = ("timestamp",)

    @action()
    def inspect(self, request, pk):
        opts = self.model._meta
        ctx = {
            "opts": opts,
            "app_label": "account",
            "change": True,
            "is_popup": False,
            "save_as": False,
            "has_delete_permission": False,
            "has_add_permission": False,
            "has_change_permission": True,
            "original": Session.objects.get(pk=pk),
            "data": {},
        }
        warnings = []
        for model in [PaymentRecord, CashPlan, Programme, ServiceProvider, TargetPopulation]:
            ctx["data"][model] = {"count": model.objects.filter(session=pk).count(), "meta": model._meta}
        for prj in Programme.objects.filter(session=pk):
            if not HopeProgram.objects.filter(id=prj.mis_id):
                warnings.append([messages.ERROR, f"Program {prj.mis_id} not found in HOPE"])

        for tp in TargetPopulation.objects.filter(session=pk):
            if not HopeTargetPopulation.objects.filter(id=tp.mis_id):
                warnings.append([messages.ERROR, f"TargetPopulation {tp.mis_id} not found in HOPE"])

        ctx["warnings"] = [(DEFAULT_TAGS[w[0]], w[1]) for w in warnings]
        return TemplateResponse(request, "admin/cash_assist_datahub/session/inspect.html", ctx)


@admin.register(CashPlan)
class CashPlanAdmin(HOPEModelAdminBase):
    list_display = ("session", "name", "status", "business_area", "cash_plan_id")
    list_filter = ("status", TextFieldFilter.factory("session__id"), TextFieldFilter.factory("business_area"))
    date_hierarchy = "session__timestamp"
    raw_id_fields = ("session",)


@admin.register(PaymentRecord)
class PaymentRecordAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ("session", "business_area", "status", "full_name")
    raw_id_fields = ("session",)
    date_hierarchy = "session__timestamp"
    list_filter = (
        "status",
        "delivery_type",
        TextFieldFilter.factory("session__id"),
        TextFieldFilter.factory("business_area"),
    )

    @action()
    def inspect(self, request, pk):
        opts = self.model._meta
        payment_record: PaymentRecord = PaymentRecord.objects.get(pk=pk)
        ctx = {
            "opts": opts,
            "app_label": "account",
            "change": True,
            "is_popup": False,
            "save_as": False,
            "has_delete_permission": False,
            "has_add_permission": False,
            "has_change_permission": True,
            "original": payment_record,
            "data": {},
        }
        from hct_mis_api.apps.core.models import BusinessArea
        from hct_mis_api.apps.household.models import Individual, Household

        # ba = BusinessArea.objects.get(code=payment_record.business_area)
        for field_name, model, rk in [
            ("business_area", BusinessArea, "code"),
            ("household_mis_id", Household, "pk"),
            ("head_of_household_mis_id", Individual, "pk"),
            ("target_population_mis_id", TargetPopulation, "pk"),
        ]:
            instance = model.objects.filter(**{rk: getattr(payment_record, field_name)}).first()
            details = None
            if instance:
                details = reverse(admin_urlname(model._meta, "change"), args=[instance.pk])
            ctx["data"][model] = {"instance": instance, "details": details, "meta": model._meta}

        return TemplateResponse(request, "admin/cash_assist_datahub/payment_record/inspect.html", ctx)


@admin.register(ServiceProvider)
class ServiceProviderAdmin(HOPEModelAdminBase):
    list_display = ("session", "business_area", "full_name", "short_name", "country")
    raw_id_fields = ("session",)
    date_hierarchy = "session__timestamp"
    search_fields = ("full_name",)
    list_filter = (TextFieldFilter.factory("session__id"), TextFieldFilter.factory("business_area"))


@admin.register(Programme)
class ProgrammeAdmin(HOPEModelAdminBase):
    list_display = ("session", "mis_id", "ca_id", "ca_hash_id")
    raw_id_fields = ("session",)
    date_hierarchy = "session__timestamp"
    list_filter = (
        TextFieldFilter.factory("session__id"),
        TextFieldFilter.factory("ca_hash_id"),
        TextFieldFilter.factory("mis_id"),
        TextFieldFilter.factory("ca_id"),
    )


@admin.register(TargetPopulation)
class TargetPopulationAdmin(HOPEModelAdminBase):
    list_display = ("session", "mis_id", "ca_id", "ca_hash_id")
    raw_id_fields = ("session",)
    date_hierarchy = "session__timestamp"
    list_filter = (
        TextFieldFilter.factory("session__id"),
        TextFieldFilter.factory("ca_hash_id"),
        TextFieldFilter.factory("mis_id"),
        TextFieldFilter.factory("ca_id"),
    )
