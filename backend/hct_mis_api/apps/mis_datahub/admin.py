import logging

from django.contrib import admin, messages
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_extra_buttons.decorators import button, link
from admin_extra_buttons.mixins import confirm_action
from adminfilters.filters import ValueFilter
from smart_admin.mixins import FieldsetMixin as SmartFieldsetMixin

from hct_mis_api.apps.household import models as households
from hct_mis_api.apps.mis_datahub.models import (
    Document,
    DownPayment,
    FundsCommitment,
    Household,
    Individual,
    IndividualRoleInHousehold,
    Program,
    Session,
    TargetPopulation,
    TargetPopulationEntry,
)
from hct_mis_api.apps.program import models as programs
from hct_mis_api.apps.targeting import models as targeting
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase
from hct_mis_api.apps.utils.admin import HUBBusinessAreaFilter as BusinessAreaFilter
from hct_mis_api.apps.utils.security import is_root

logger = logging.getLogger(__name__)


class HUBAdminMixin(HOPEModelAdminBase):
    @button(label="Truncate", css_class="btn-danger", permission=is_root)
    def truncate(self, request):
        if not request.headers.get("x-root-access") == "XMLHttpRequest":
            self.message_user(request, "You are not allowed to perform this action", messages.ERROR)
            return
        if request.method == "POST":
            with atomic():
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(self.model).pk,
                    object_id=None,
                    object_repr=f"TRUNCATE TABLE {self.model._meta.verbose_name}",
                    action_flag=DELETION,
                    change_message="truncate table",
                )
                from django.db import connections

                conn = connections[self.model.objects.db]
                cursor = conn.cursor()
                cursor.execute(f"TRUNCATE TABLE '{self.model._meta.db_table}' RESTART IDENTITY CASCADE")
        else:
            return confirm_action(
                self,
                request,
                self.truncate,
                mark_safe(
                    """
<h1 class="color-red"><b>This is a low level system feature</b></h1>                                      
<h1 class="color-red"><b>Continuing irreversibly delete all table content</b></h1>
                                       
                                       """
                ),
                "Successfully executed",
            )


@admin.register(Household)
class HouseholdAdmin(HUBAdminMixin):
    list_filter = (("session__id", ValueFilter), BusinessAreaFilter)

    raw_id_fields = ("session",)

    @link()
    def members_sent_to_the_hub(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            url = reverse("admin:mis_datahub_individual_changelist")
            # http://localhost:9000/api/admin/mis_datahub/individual/?session=1&household_mis_id|iexact=87eb7e38-088d-42e4-ba1d-0b96bc32605a
            return f"{url}?session={obj.pk}&household_mis_id={obj.mis_id}"
        else:
            button.visible = False

    @button()
    def see_hope_record(self, request, pk):
        obj = self.get_object(request, pk)
        hh = households.Household.objects.get(id=obj.mis_id)
        url = reverse("admin:household_individual_change", args=[hh.pk])
        return HttpResponseRedirect(url)


@admin.register(Individual)
class IndividualAdmin(HUBAdminMixin):
    list_display = ("session", "unicef_id", "mis_id", "household_mis_id", "family_name", "given_name")
    list_filter = (
        BusinessAreaFilter,
        ("session__id", ValueFilter),
        ("unicef_id", ValueFilter),
        ("mis_id", ValueFilter),
        ("household_mis_id", ValueFilter),
    )
    raw_id_fields = ("session",)

    @link()
    def household(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            url = reverse("admin:mis_datahub_household_changelist")
            # http://localhost:9000/api/admin/mis_datahub/individual/?session=1&household_mis_id|iexact=87eb7e38-088d-42e4-ba1d-0b96bc32605a
            return f"{url}?session={obj.pk}&household_mis_id={obj.mis_id}"
        else:
            button.visible = False


@admin.register(FundsCommitment)
class FundsCommitmentAdmin(HUBAdminMixin):
    filters = (BusinessAreaFilter,)


@admin.register(DownPayment)
class DownPaymentAdmin(HUBAdminMixin):
    filters = (
        BusinessAreaFilter,
        ("rec_serial_number", ValueFilter),
        "create_date",
        "mis_sync_flag",
        "ca_sync_flag",
    )


@admin.register(IndividualRoleInHousehold)
class IndividualRoleInHouseholdAdmin(HUBAdminMixin):
    list_filter = (("session__id", ValueFilter),)


@admin.register(Session)
class SessionAdmin(SmartFieldsetMixin, HUBAdminMixin):
    list_display = ("timestamp", "id", "source", "status", "last_modified_date", "business_area")
    date_hierarchy = "timestamp"
    list_filter = (
        "status",
        BusinessAreaFilter,
    )
    ordering = ("-timestamp",)
    search_fields = ("id",)

    @link()
    def target_population(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            url = reverse("admin:mis_datahub_targetpopulation_changelist")
            return f"{url}?session={obj.pk}"
        else:
            button.visible = False

    @link()
    def individuals(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            url = reverse("admin:mis_datahub_individual_changelist")
            return f"{url}?session={obj.pk}"
        else:
            button.visible = False

    @link()
    def households(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            url = reverse("admin:mis_datahub_household_changelist")
            return f"{url}?session={obj.pk}"
        else:
            button.visible = False

    @button(permission="account.can_inspect")
    def inspect(self, request, pk):
        context = self.get_common_context(request, pk)
        obj = context["original"]
        context["title"] = f"Session {obj.pk} - {obj.timestamp} - {obj.status}"
        context["data"] = {}
        for model in [
            Program,
            TargetPopulation,
            Household,
            Individual,
            IndividualRoleInHousehold,
            TargetPopulationEntry,
            Document,
        ]:
            context["data"][model] = {"count": model.objects.filter(session=pk).count(), "meta": model._meta}

        return TemplateResponse(request, "admin/mis_datahub/session/inspect.html", context)

    @button()
    def reset_sync_date(self, request, pk):
        if request.method == "POST":
            try:
                with atomic():
                    obj = self.get_object(request, pk)
                    # Programs
                    hub_program_ids = Program.objects.filter(session=obj.id).values_list("mis_id", flat=True)
                    programs.Program.objects.filter(id__in=hub_program_ids).update(last_sync_at=None)
                    # Documents
                    hub_document_ids = Document.objects.filter(session=obj.id).values_list("mis_id", flat=True)
                    households.Document.objects.filter(id__in=hub_document_ids).update(last_sync_at=None)
                    # HH / Ind
                    for hub_tp in TargetPopulation.objects.filter(session=obj.id):
                        tp = targeting.TargetPopulation.objects.get(id=hub_tp.mis_id)
                        tp.households.update(last_sync_at=None)
                        households.Individual.objects.filter(household__target_populations=tp).update(last_sync_at=None)

                    self.message_user(request, "Done", messages.SUCCESS)

            except Exception as e:
                logger.exception(e)
                self.message_user(request, str(e), messages.ERROR)
            # for m in [hope_models.Household, hope_models.Individual]:
            #     hh = hope_models.Household.objects.filter(id__in=Household.)
            #     m.objects(request).update(last_sync_at=None)
        else:
            return confirm_action(
                self,
                request,
                self.reset_sync_date,
                "Continuing will reset last_sync_date of any" " object linked to this Session.",
                "Successfully executed",
            )


@admin.register(TargetPopulationEntry)
class TargetPopulationEntryAdmin(HUBAdminMixin):
    list_filter = (("session__id", ValueFilter),)
    raw_id_fields = ("session",)


@admin.register(TargetPopulation)
class TargetPopulationAdmin(HUBAdminMixin):
    # list_display = ('name', )
    list_filter = (("session__id", ValueFilter), BusinessAreaFilter)
    raw_id_fields = ("session",)
    search_fields = ("name",)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

    @link()
    def individuals(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            url = reverse("admin:mis_datahub_individual_changelist")
            return f"{url}?session={obj.session.pk}"
        else:
            button.visible = False

    @link()
    def households(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            url = reverse("admin:mis_datahub_household_changelist")
            return f"{url}?session={obj.session.pk}"
        else:
            button.visible = False


@admin.register(Program)
class ProgramAdmin(HUBAdminMixin):
    list_filter = (("session__id", ValueFilter), BusinessAreaFilter)
    search_fields = ("name",)
    raw_id_fields = ("session",)


@admin.register(Document)
class DocumentAdmin(HUBAdminMixin):
    list_display = ("type", "number")
    list_filter = (("session__id", ValueFilter), BusinessAreaFilter)
    raw_id_fields = ("session",)
