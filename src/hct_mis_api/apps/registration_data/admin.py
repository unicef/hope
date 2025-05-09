import logging
from typing import Any
from uuid import UUID

from django.contrib import admin, messages
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_extra_buttons.api import confirm_action
from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin
from adminfilters.querystring import QueryStringFilter

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.celery_tasks import enroll_households_to_program_task
from hct_mis_api.apps.household.documents import get_individual_doc
from hct_mis_api.apps.household.forms import MassEnrollForm
from hct_mis_api.apps.household.models import Individual, PendingIndividual
from hct_mis_api.apps.payment.models import Payment
from hct_mis_api.apps.registration_data.models import (
    DeduplicationEngineSimilarityPair,
    ImportData,
    KoboImportData,
    RegistrationDataImport,
)
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    merge_registration_data_import_task,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase
from hct_mis_api.apps.utils.elasticsearch_utils import (
    remove_elasticsearch_documents_by_matching_ids,
)
from hct_mis_api.apps.utils.security import is_root

logger = logging.getLogger(__name__)


@admin.register(RegistrationDataImport)
class RegistrationDataImportAdmin(AdminAutoCompleteSearchMixin, HOPEModelAdminBase):
    list_display = (
        "name",
        "business_area",
        "program",
        "status",
        "data_source",
        "import_date",
        "imported_by",
        "deduplication_engine_status",
        "number_of_individuals",
        "number_of_households",
        "screen_beneficiary",
        "pull_pictures",
        "excluded",
        "erased",
        "deduplication_engine_status",
    )
    search_fields = ("name",)
    list_filter = (
        QueryStringFilter,
        ("status", ChoicesFieldComboFilter),
        ("data_source", ChoicesFieldComboFilter),
        ("business_area", LinkedAutoCompleteFilter.factory(parent=None)),
        ("program", LinkedAutoCompleteFilter.factory(parent="business_area")),
        ("imported_by", AutoCompleteFilter),
        "data_source",
        "screen_beneficiary",
        "pull_pictures",
        "excluded",
        "erased",
        "deduplication_engine_status",
    )
    date_hierarchy = "updated_at"
    raw_id_fields = ("imported_by", "business_area", "program", "import_data")
    advanced_filter_fields = (
        "status",
        "updated_at",
        ("imported_by__username", "imported by"),
        ("business_area__name", "business area"),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("business_area", "program", "imported_by")

    @button(
        label="Re-run RDI",
        permission="registration_data.rerun_rdi",
        enabled=lambda btn: btn.original.status == RegistrationDataImport.IMPORT_ERROR,
    )
    def rerun_rdi(self, request: HttpRequest, pk: UUID) -> None:
        obj = self.get_object(request, str(pk))
        try:
            if obj.data_source == RegistrationDataImport.XLS:
                from hct_mis_api.apps.registration_datahub.celery_tasks import (
                    registration_xlsx_import_task,
                )

                celery_task = registration_xlsx_import_task
            else:
                from hct_mis_api.apps.registration_datahub.celery_tasks import (
                    registration_kobo_import_task,
                )

                celery_task = registration_kobo_import_task

            business_area = obj.business_area

            celery_task.delay(
                registration_data_import_id=str(obj.id),
                import_data_id=str(obj.import_data.id),
                business_area_id=str(business_area.id),
                program_id=str(obj.program_id),
            )

            self.message_user(request, "RDI task has started")
        except Exception as e:
            logger.exception(e)
            self.message_user(request, "An error occurred while processing RDI task", messages.ERROR)

    @button(
        label="Re-run Merging RDI",
        permission="registration_data.rerun_rdi",
        enabled=lambda btn: btn.original.status == RegistrationDataImport.MERGE_ERROR,
    )
    def rerun_merge_rdi(self, request: HttpRequest, pk: UUID) -> None:
        try:
            merge_registration_data_import_task.delay(registration_data_import_id=pk)

            self.message_user(request, "RDI Merge task has started")
        except Exception as e:
            logger.exception(e)
            self.message_user(request, "An error occurred while processing RDI Merge task", messages.ERROR)

    @staticmethod
    def _delete_rdi(rdi: RegistrationDataImport) -> None:
        pending_individuals_ids = list(
            PendingIndividual.objects.filter(registration_data_import=rdi).values_list("id", flat=True)
        )
        rdi.delete()
        # remove elastic search records linked to individuals
        business_area_slug = rdi.business_area.slug
        remove_elasticsearch_documents_by_matching_ids(pending_individuals_ids, get_individual_doc(business_area_slug))

    @button(
        permission=is_root,
        enabled=lambda btn: btn.original.status not in [RegistrationDataImport.MERGED, RegistrationDataImport.MERGING],
    )
    def delete_rdi(self, request: HttpRequest, pk: UUID) -> Any:  # TODO: typing
        try:
            if request.method == "POST":
                with transaction.atomic():
                    rdi = RegistrationDataImport.objects.get(pk=pk)
                    rdi_name = rdi.name
                    self._delete_rdi(rdi)
                    self.message_user(request, "RDI Deleted")
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(self.model).pk,
                        object_id=None,  # type: ignore # Argument "object_id" to "log_action" of "LogEntryManager" has incompatible type "None"; expected "Union[int, str, UUID]"
                        object_repr=f"Removed RDI {rdi_name} id: {pk}",
                        action_flag=DELETION,
                        change_message="RDI removed",
                    )
                    return HttpResponseRedirect(reverse("admin:registration_data_registrationdataimport_changelist"))
            else:
                return confirm_action(
                    self,
                    request,
                    self.delete_rdi,
                    mark_safe(
                        """<h1>DO NOT CONTINUE IF YOU ARE NOT SURE WHAT YOU ARE DOING</h1>
                    <h3>All households connected to this Registration data import will be deleted</h3>
                    """
                    ),
                    "Successfully executed",
                )
        except Exception as e:
            logger.exception(e)
            self.message_user(request, "An error occurred while processing RDI delete", messages.ERROR)

    @staticmethod
    def delete_merged_rdi_visible(rdi: RegistrationDataImport) -> bool:
        is_correct_status = rdi.status == RegistrationDataImport.MERGED
        is_not_used_by_payment_record = Payment.objects.filter(household__registration_data_import=rdi).count() == 0
        return is_correct_status and is_not_used_by_payment_record

    @staticmethod
    def generate_query_for_all_grievances_tickets(rdi: RegistrationDataImport) -> Q:
        details_related_names = [
            "referral_ticket_details__household",
            "negative_feedback_ticket_details__household",
            "positive_feedback_ticket_details__household",
            "needs_adjudication_ticket_details__golden_records_individual",
            "needs_adjudication_ticket_details__possible_duplicate",
            "system_flagging_ticket_details__golden_records_individual",
            "system_flagging_ticket_details__golden_records_individual",
            "delete_individual_ticket_details__individual",
            "add_individual_ticket_details__household",
            "individual_data_update_ticket_details__individual",
            "household_data_update_ticket_details__household",
            "sensitive_ticket_details__household",
            "sensitive_ticket_details__individual",
            "complaint_ticket_details__household",
            "complaint_ticket_details__individual",
        ]
        query = Q()
        for related_name in details_related_names:
            query |= Q(**{f"{related_name}__registration_data_import": rdi})
        return query

    @staticmethod
    def _delete_merged_rdi(rdi: RegistrationDataImport) -> None:
        individuals_ids = list(Individual.objects.filter(registration_data_import=rdi).values_list("id", flat=True))
        GrievanceTicket.objects.filter(
            RegistrationDataImportAdmin.generate_query_for_all_grievances_tickets(rdi)
        ).filter(business_area=rdi.business_area).delete()
        rdi.delete()
        # remove elastic search records linked to individuals
        business_area_slug = rdi.business_area.slug
        remove_elasticsearch_documents_by_matching_ids(individuals_ids, get_individual_doc(business_area_slug))

    @button(
        permission=is_root,
        visible=lambda btn: RegistrationDataImportAdmin.delete_merged_rdi_visible(btn.original),
    )
    def delete_merged_rdi(self, request: HttpRequest, pk: UUID) -> HttpResponse | None:
        try:
            rdi = RegistrationDataImport.objects.get(pk=pk)
            if request.method == "POST":
                with transaction.atomic():
                    rdi_name = rdi.name
                    self._delete_merged_rdi(rdi)
                    self.message_user(request, "RDI Deleted")
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(self.model).pk,
                        object_id=None,  # type: ignore # Argument "object_id" to "log_action" of "LogEntryManager" has incompatible type "None"; expected "Union[int, str, UUID]"
                        object_repr=f"Removed RDI {rdi_name} id: {pk}",
                        action_flag=DELETION,
                        change_message="RDI removed",
                    )
                    return HttpResponseRedirect(reverse("admin:registration_data_registrationdataimport_changelist"))
            else:
                number_of_households = rdi.households.count()
                number_of_individuals = rdi.individuals.count()
                number_of_household_selections = Payment.objects.filter(
                    parent__household__registration_data_import=rdi,
                ).count()
                return confirm_action(
                    self,
                    request,
                    self.delete_rdi,
                    mark_safe(
                        f"""<h1>DO NOT CONTINUE IF YOU ARE NOT SURE WHAT YOU ARE DOING</h1>
                    <h3>Deleting the RDI will also result in the removal of related households, individuals, and their associated grievance tickets.</h3>
                    <h3>Consequently, these households will no longer be part of any Target Population, if they were included previously.</h3>
                    <br>
                    <h4>This action will result in removing: {number_of_households} Households, {number_of_individuals} Individuals and {number_of_household_selections} Payments</h4>
                    """
                    ),
                    "Successfully executed",
                )
        except Exception as e:
            logger.exception(e)
            self.message_user(request, "An error occurred while processing RDI delete", messages.ERROR)
            return None

    @button(permission="household.view_household")
    def households(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect:
        obj = self.get_object(request, str(pk))
        url = reverse("admin:household_household_changelist")
        return HttpResponseRedirect(f"{url}?&qs=registration_data_import__exact={obj.id}")

    @button(permission="program.enroll_beneficiaries")
    def enroll_to_program(self, request: HttpRequest, pk: UUID) -> HttpResponse | None:
        url = reverse("admin:registration_data_registrationdataimport_change", args=[pk])
        qs = RegistrationDataImport.objects.filter(pk=pk).first().households.all()
        if not qs.exists():
            self.message_user(request, "No households found in this RDI", level=messages.ERROR)
            return None
        context = self.get_common_context(request, title="Mass enroll households to another program")
        business_area_id = qs.first().business_area_id
        if "apply" in request.POST or "acknowledge" in request.POST:
            form = MassEnrollForm(request.POST, business_area_id=business_area_id, households=qs)
            if form.is_valid():
                program_for_enroll = form.cleaned_data["program_for_enroll"]
                households_ids = list(qs.distinct("unicef_id").values_list("id", flat=True))
                enroll_households_to_program_task.delay(
                    households_ids=households_ids,
                    program_for_enroll_id=str(program_for_enroll.id),
                    user_id=str(request.user.id),
                )
                self.message_user(
                    request,
                    f"Enrolling households to program: {program_for_enroll}",
                    level=messages.SUCCESS,
                )
                return HttpResponseRedirect(url)
        form = MassEnrollForm(request.POST, business_area_id=business_area_id, households=qs)
        context["form"] = form
        context["action"] = "mass_enroll_to_another_program"
        context["enroll_from"] = "RDI"
        return TemplateResponse(request, "admin/household/household/enroll_households_to_program.html", context)


@admin.register(ImportData)
class ImportDataAdmin(HOPEModelAdminBase):
    search_fields = ("business_area_slug",)
    list_display = ("business_area_slug", "status", "data_type", "number_of_households", "number_of_individuals")
    list_filter = (
        "status",
        "data_type",
        ("created_by_id", AutoCompleteFilter),
    )


@admin.register(KoboImportData)
class KoboImportDataDataAdmin(HOPEModelAdminBase):
    search_fields = ("business_area_slug",)
    list_display = (
        "business_area_slug",
        "status",
        "data_type",
        "kobo_asset_id",
        "number_of_households",
        "number_of_individuals",
        "only_active_submissions",
        "pull_pictures",
    )
    list_filter = (
        "status",
        "data_type",
        ("created_by_id", AutoCompleteFilter),
        "only_active_submissions",
        "pull_pictures",
    )


@admin.register(DeduplicationEngineSimilarityPair)
class DeduplicationEngineSimilarityPairAdmin(HOPEModelAdminBase):
    list_display = ("program", "individual1", "individual2", "similarity_score")
    list_filter = (("program", AutoCompleteFilter),)
    raw_id_fields = ("program", "individual1", "individual2")
    search_fields = ("program", "individual1", "individual2")
