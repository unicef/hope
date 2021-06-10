import datetime
import logging

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.messages import DEFAULT_TAGS
from django.db import transaction
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_extra_urls.api import button
from admin_extra_urls.mixins import ExtraUrlMixin, _confirm_action
from adminfilters.filters import TextFieldFilter

logger = logging.getLogger(__name__)

from hct_mis_api.apps.cash_assist_datahub.models import (
    CashPlan,
    PaymentRecord,
    Programme,
    ServiceProvider,
    Session,
    TargetPopulation,
)
from hct_mis_api.apps.household import models as people
from hct_mis_api.apps.program import models as program
from hct_mis_api.apps.targeting import models as targeting
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24


class RollbackException(Exception):
    pass


@admin.register(Session)
class SessionAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_display = ("timestamp", "id", "source", "status", "last_modified_date", "business_area")
    date_hierarchy = "timestamp"
    list_filter = ("status", "source", TextFieldFilter.factory("business_area"))
    ordering = ("-timestamp",)

    @button()
    def execute_pull(self, request):
        from hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub import (
            PullFromDatahubTask,
        )

        if request.method == "POST":
            task = PullFromDatahubTask()
            task.execute()
            self.message_user(request, "Cash Assist Pull Finished", messages.SUCCESS)
        else:
            return _confirm_action(
                self,
                request,
                self.execute_pull,
                mark_safe(
                    """<h1>DO NOT CONTINUE IF YOU ARE NOT SURE WHAT YOU ARE DOING</h1>                
                        <h3>Import will only be simulated</h3> 
                        """
                ),
                "Successfully executed",
                template="admin_extra_urls/confirm.html",
            )

    @button(label="test import", permission=lambda r, o: r.user.is_superuser)
    def execute(self, request, pk):
        context = self.get_common_context(request, pk, title="Test Import")
        session: Session = context["original"]
        if request.method == "POST":
            from hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub import (
                PullFromDatahubTask,
            )

            runner = PullFromDatahubTask()
            try:
                with transaction.atomic(using="default"):
                    with transaction.atomic(using="cash_assist_datahub_ca"):
                        runner.copy_session(session)
                        raise RollbackException()
            except RollbackException:
                self.message_user(request, "Test Completed", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, str(e), messages.ERROR)
                logger.exception(e)

        else:
            return _confirm_action(
                self,
                request,
                self.execute,
                mark_safe(
                    """<h1>DO NOT CONTINUE IF YOU ARE NOT SURE WHAT YOU ARE DOING</h1>                
                <h3>Import will only be simulated</h3> 
                """
                ),
                "Successfully executed",
            )

    @button()
    def inspect(self, request, pk):
        context = self.get_common_context(request, pk)
        obj: Session = context["original"]
        context["title"] = f"Session {obj.pk} - {obj.timestamp} - {obj.status}"
        context["data"] = {}
        warnings = []
        errors = 0
        has_content = False
        if settings.SENTRY_URL:
            context["sentry_url"] = f"{settings.SENTRY_URL}?query=session.ca%3A%22{obj.pk}%22"

        if obj.status == obj.STATUS_EMPTY:
            warnings.append([messages.WARNING, f"Session is empty"])
        elif obj.status == obj.STATUS_FAILED:
            warnings.append([messages.ERROR, f"Session is failed"])
        elif obj.status == obj.STATUS_PROCESSING:
            elapsed = datetime.datetime.now() - obj.timestamp
            if elapsed.total_seconds() >= DAY:
                warnings.append([messages.ERROR, f"Session is running more than {elapsed}"])
            elif elapsed.total_seconds() >= HOUR:
                warnings.append([messages.WARNING, f"Session is running more than {elapsed}"])

        for model in [Programme, CashPlan, TargetPopulation, PaymentRecord, ServiceProvider]:
            count = model.objects.filter(session=pk).count()
            has_content = has_content or count
            context["data"][model] = {"count": count, "errors": [], "meta": model._meta}

        for prj in Programme.objects.filter(session=pk):
            if not program.Program.objects.filter(id=prj.mis_id).exists():
                errors += 1
                context["data"][Programme]["errors"].append(f"Program {prj.mis_id} not found in HOPE")

        for tp in TargetPopulation.objects.filter(session=pk):
            if not targeting.TargetPopulation.objects.filter(id=tp.mis_id).exists():
                errors += 1
                context["data"][TargetPopulation]["errors"].append(f"TargetPopulation {tp.mis_id} not found in HOPE")

        for pr in PaymentRecord.objects.filter(session=pk):
            if not people.Household.objects.filter(id=pr.household_mis_id).exists():
                errors += 1
                context["data"][PaymentRecord]["errors"].append(
                    f"PaymentRecord {pr.id} refers to unknown Household {pr.household_mis_id}"
                )

        if errors:
            warnings.append([messages.ERROR, f"{errors} Errors found"])

        if (obj.status == obj.STATUS_EMPTY) and has_content:
            warnings.append([messages.ERROR, f"Session marked as Empty but records found"])

        context["warnings"] = [(DEFAULT_TAGS[w[0]], w[1]) for w in warnings]

        return TemplateResponse(request, "admin/cash_assist_datahub/session/inspect.html", context)


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

    @button()
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
        from hct_mis_api.apps.household.models import Household, Individual

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
