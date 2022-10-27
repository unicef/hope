import logging
from typing import Any, Dict, List

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.messages import DEFAULT_TAGS
from django.db import transaction
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from admin_extra_buttons.api import button
from admin_extra_buttons.decorators import link
from admin_extra_buttons.mixins import confirm_action
from adminfilters.filters import ChoicesFieldComboFilter, ValueFilter
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.cash_assist_datahub.models import (
    CashPlan,
    PaymentRecord,
    Programme,
    ServiceProvider,
    Session,
    TargetPopulation,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household import models as people
from hct_mis_api.apps.program import models as program
from hct_mis_api.apps.targeting import models as targeting
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase
from hct_mis_api.apps.utils.admin import HUBBusinessAreaFilter as BusinessAreaFilter

logger = logging.getLogger(__name__)

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24


class RollbackException(Exception):
    pass


@admin.register(Session)
class SessionAdmin(HOPEModelAdminBase):
    list_display = ("timestamp", "id", "status", "last_modified_date", "business_area", "run_time")
    date_hierarchy = "timestamp"
    list_filter = (
        BusinessAreaFilter,
        ("status", ChoicesFieldComboFilter),
        "source",
        "last_modified_date",
    )
    ordering = ("-timestamp",)
    exclude = ("traceback",)
    readonly_fields = ("timestamp", "last_modified_date", "sentry_id", "source", "business_area")

    def run_time(self, obj):
        if obj.status in (obj.STATUS_PROCESSING, obj.STATUS_LOADING):
            elapsed = timezone.now() - obj.timestamp
            if elapsed.total_seconds() >= HOUR:
                return elapsed

    @button(permission="account.can_debug")
    def pull(self, request):
        from hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub import (
            PullFromDatahubTask,
        )

        try:
            ret = PullFromDatahubTask().execute()
            if ret["failures"]:
                raise Exception(ret)
            else:
                self.message_user(request, ret, messages.SUCCESS)
        except Exception as e:
            msg = f"{e.__class__.__name__}: {str(e)}"
            self.message_user(request, msg, messages.ERROR)

    @button()
    def simulate_import(self, request, pk):
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
                msg = f"{e.__class__.__name__}: {str(e)}"
                if session.sentry_id:
                    url = f"{settings.SENTRY_URL}?query={session.sentry_id}"
                    sentry_url = f'<a href="{url}" target="_sentry" >View on Sentry<a/>'
                    msg = mark_safe(f"{msg} - {sentry_url}")

                self.message_user(request, msg, messages.ERROR)
                logger.exception(e)

        else:
            return confirm_action(
                self,
                request,
                self.simulate_import,
                mark_safe(
                    """<h1>DO NOT CONTINUE IF YOU ARE NOT SURE WHAT YOU ARE DOING</h1>
                <h3>Import will only be simulated</h3>
                """
                ),
                "Successfully executed",
            )

    @link(html_attrs={"target": "_new"}, permission="account.can_debug")
    def view_error_on_sentry(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            if obj.sentry_id:
                return f"{settings.SENTRY_URL}?query={obj.sentry_id}"

        button.visible = False

    @button(visible=lambda btn: btn.original.traceback, permission="account.can_debug")
    def view_error(self, request, pk):
        context = self.get_common_context(request, pk)
        return TemplateResponse(request, "admin/cash_assist_datahub/session/debug.html", context)

    @button(permission="account.can_inspect")
    def inspect(self, request, pk):
        context: Dict[str, Any] = self.get_common_context(request, pk)
        obj: Session = context["original"]
        context["title"] = f"Session {obj.pk} - {obj.timestamp} - {obj.status}"
        context["data"] = {}
        warnings: List[List] = []
        errors = 0
        errors = 0
        has_content = False
        if settings.SENTRY_URL and obj.sentry_id:
            context["sentry_url"] = f"{settings.SENTRY_URL}?query={obj.sentry_id}"

        if obj.status == obj.STATUS_EMPTY:
            warnings.append([messages.WARNING, "Session is empty"])
        elif obj.status == obj.STATUS_FAILED:
            warnings.append([messages.ERROR, "Session is failed"])
        elif obj.status == obj.STATUS_PROCESSING:
            elapsed = timezone.now() - obj.timestamp
            if elapsed.total_seconds() >= DAY:
                warnings.append([messages.ERROR, f"Session is running more than {elapsed}"])
            elif elapsed.total_seconds() >= HOUR:
                warnings.append([messages.WARNING, f"Session is running more than {elapsed}"])

        for model in (Programme, CashPlan, TargetPopulation, PaymentRecord, ServiceProvider):
            count = model.objects.filter(session=pk).count()
            has_content = has_content or count
            context["data"][model] = {"count": count, "warnings": [], "errors": [], "meta": model._meta}

        for prj in Programme.objects.filter(session=pk):
            if not program.Program.objects.filter(id=prj.mis_id).exists():
                errors += 1
                context["data"][Programme]["errors"].append(f"Program {prj.mis_id} not found in HOPE")

        for tp in TargetPopulation.objects.filter(session=pk):
            if not targeting.TargetPopulation.objects.filter(id=tp.mis_id).exists():
                errors += 1
                context["data"][TargetPopulation]["errors"].append(f"TargetPopulation {tp.mis_id} not found in HOPE")

        svs = []
        for sv in ServiceProvider.objects.filter(session=pk):
            svs.append(sv.ca_id)

        session_cacheplans = CashPlan.objects.filter(session=pk).values_list("cash_plan_id", flat=True)
        hope_cacheplans = program.CashPlan.objects.filter(business_area__code=obj.business_area).values_list(
            "ca_id", flat=True
        )
        known_cacheplans = list(session_cacheplans) + list(hope_cacheplans)

        for pr in PaymentRecord.objects.filter(session=pk):
            if pr.service_provider_ca_id not in svs:
                errors += 1
                context["data"][PaymentRecord]["errors"].append(
                    f"PaymentRecord uses ServiceProvider {pr.service_provider_ca_id} that is not present in the Session"
                )
            if pr.cash_plan_ca_id not in known_cacheplans:
                errors += 1
                context["data"][PaymentRecord]["errors"].append(
                    f"PaymentRecord is part of an  unknown CashPlan {pr.cash_plan_ca_id}"
                )

            if not people.Household.objects.filter(id=pr.household_mis_id).exists():
                errors += 1
                context["data"][PaymentRecord]["errors"].append(
                    f"PaymentRecord {pr.id} refers to unknown Household {pr.household_mis_id}"
                )

        if errors:
            warnings.append([messages.ERROR, f"{errors} Errors found"])

        if (obj.status == obj.STATUS_EMPTY) and has_content:
            warnings.append([messages.ERROR, "Session marked as Empty but records found"])

        area = BusinessArea.objects.filter(code=obj.business_area.strip()).first()
        context["area"] = area
        if not area:
            warnings.append([messages.ERROR, "Invalid Business Area"])

        context["warnings"] = [(DEFAULT_TAGS[w[0]], w[1]) for w in warnings]
        return TemplateResponse(request, "admin/cash_assist_datahub/session/inspect.html", context)


@admin.register(CashPlan)
class CashPlanAdmin(HOPEModelAdminBase):
    list_display = ("session", "name", "status", "business_area", "cash_plan_id")
    list_filter = (
        "status",
        ("cash_plan_id", ValueFilter),
        ("session__id", ValueFilter),
        BusinessAreaFilter,
    )
    date_hierarchy = "session__timestamp"
    raw_id_fields = ("session",)

    @link()
    def payment_records(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            url = reverse("admin:cash_assist_datahub_paymentrecord_changelist")
            return f"{url}?cash_plan_ca_id|iexact={obj.cash_plan_id}"
        else:
            button.visible = False


@admin.register(PaymentRecord)
class PaymentRecordAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = ("session", "business_area", "status", "full_name", "service_provider_ca_id")
    raw_id_fields = ("session",)
    date_hierarchy = "session__timestamp"
    list_filter = (
        "status",
        "delivery_type",
        "service_provider_ca_id",
        ("ca_id", ValueFilter),
        ("cash_plan_ca_id", ValueFilter),
        ("session__id", ValueFilter),
        BusinessAreaFilter,
    )

    @button(permission="account.can_inspect")
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
        for field_name, model, rk in (
            ("business_area", BusinessArea, "code"),
            ("household_mis_id", Household, "pk"),
            ("head_of_household_mis_id", Individual, "pk"),
            ("target_population_mis_id", TargetPopulation, "pk"),
        ):
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
    list_filter = (("session__id", ValueFilter), BusinessAreaFilter)


@admin.register(Programme)
class ProgrammeAdmin(HOPEModelAdminBase):
    list_display = ("session", "mis_id", "ca_id", "ca_hash_id")
    raw_id_fields = ("session",)
    date_hierarchy = "session__timestamp"
    list_filter = (
        ("session__id", ValueFilter),
        ("ca_hash_id", ValueFilter),
        ("mis_id", ValueFilter),
        ("ca_id", ValueFilter),
    )


@admin.register(TargetPopulation)
class TargetPopulationAdmin(HOPEModelAdminBase):
    list_display = ("session", "mis_id", "ca_id", "ca_hash_id")
    raw_id_fields = ("session",)
    date_hierarchy = "session__timestamp"
    list_filter = (
        ("session__id", ValueFilter),
        ("ca_hash_id", ValueFilter),
        ("mis_id", ValueFilter),
        ("ca_id", ValueFilter),
    )
