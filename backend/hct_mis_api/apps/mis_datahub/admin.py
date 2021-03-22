import logging

from django.contrib import admin, messages
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from admin_extra_urls.decorators import button, href
from admin_extra_urls.mixins import ExtraUrlMixin, _confirm_action
from adminfilters.filters import TextFieldFilter
from smart_admin.mixins import FieldsetMixin as SmartFieldsetMixin

from hct_mis_api.apps.household import models as households
from hct_mis_api.apps.mis_datahub.models import (
    Document,
    Household,
    Individual,
    IndividualRoleInHousehold,
    Program,
    Session,
    TargetPopulation,
)
from hct_mis_api.apps.program import models as programs
from hct_mis_api.apps.targeting import models as targeting
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase

logger = logging.getLogger(__name__)


@admin.register(Household)
class HouseholdAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_filter = (TextFieldFilter.factory("session__id"), TextFieldFilter.factory("business_area"))
    raw_id_fields = ("session",)

    @href()
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
class IndividualAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_display = ("session", "unicef_id", "mis_id", "household_mis_id", "family_name", "given_name")
    list_filter = (
        TextFieldFilter.factory("session__id"),
        TextFieldFilter.factory("unicef_id"),
        TextFieldFilter.factory("mis_id"),
        TextFieldFilter.factory("household_mis_id"),
        TextFieldFilter.factory("business_area"),
    )
    raw_id_fields = ("session",)

    @href()
    def household(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            url = reverse("admin:mis_datahub_household_changelist")
            # http://localhost:9000/api/admin/mis_datahub/individual/?session=1&household_mis_id|iexact=87eb7e38-088d-42e4-ba1d-0b96bc32605a
            return f"{url}?session={obj.pk}&household_mis_id={obj.mis_id}"
        else:
            button.visible = False


@admin.register(IndividualRoleInHousehold)
class IndividualRoleInHouseholdAdmin(HOPEModelAdminBase):
    list_filter = (TextFieldFilter.factory("session__id"), TextFieldFilter.factory("business_area"))


@admin.register(Session)
class SessionAdmin(SmartFieldsetMixin, ExtraUrlMixin, admin.ModelAdmin):
    list_display = ("timestamp", "id", "source", "status", "last_modified_date", "business_area")
    date_hierarchy = "timestamp"
    list_filter = ("status", "source", TextFieldFilter.factory("business_area"))
    ordering = ("timestamp",)

    @href()
    def target_population(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            url = reverse("admin:mis_datahub_targetpopulation_changelist")
            return f"{url}?session={obj.pk}"
        else:
            button.visible = False

    @href()
    def individuals(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            url = reverse("admin:mis_datahub_individual_changelist")
            return f"{url}?session={obj.pk}"
        else:
            button.visible = False

    @href()
    def households(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            url = reverse("admin:mis_datahub_household_changelist")
            return f"{url}?session={obj.pk}"
        else:
            button.visible = False

    @button()
    def inspect(self, request, pk):
        context = self.get_common_context(request)
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
            return _confirm_action(
                self,
                request,
                self.reset_sync_date,
                "Continuing will reset last_sync_date of any" " object linked to this Session.",
                "Successfully executed",
            )


@admin.register(TargetPopulation)
class TargetPopulationAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_filter = (TextFieldFilter.factory("session__id"), TextFieldFilter.factory("business_area"))
    raw_id_fields = ("session",)

    @href()
    def individuals(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            url = reverse("admin:mis_datahub_individual_changelist")
            return f"{url}?session={obj.session.pk}"
        else:
            button.visible = False

    @href()
    def households(self, button):
        if "original" in button.context:
            obj = button.context["original"]
            url = reverse("admin:mis_datahub_household_changelist")
            return f"{url}?session={obj.session.pk}"
        else:
            button.visible = False


@admin.register(Program)
class ProgramAdmin(HOPEModelAdminBase):
    list_filter = (TextFieldFilter.factory("session__id"), TextFieldFilter.factory("business_area"))


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("type", "number")
    list_filter = (TextFieldFilter.factory("session__id"), TextFieldFilter.factory("business_area"))
    raw_id_fields = ("session",)
