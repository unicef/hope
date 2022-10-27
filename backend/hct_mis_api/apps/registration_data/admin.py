import logging
from typing import Optional

from django.contrib import admin, messages
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_extra_buttons.api import confirm_action
from admin_extra_buttons.decorators import button, link
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.documents import IndividualDocument
from hct_mis_api.apps.household.elasticsearch_utils import (
    remove_elasticsearch_documents_by_matching_ids,
)
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub import models as datahub_models
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    merge_registration_data_import_task,
)
from hct_mis_api.apps.registration_datahub.documents import ImportedIndividualDocument
from hct_mis_api.apps.registration_datahub.models import RegistrationDataImportDatahub
from hct_mis_api.apps.targeting.models import HouseholdSelection
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase
from hct_mis_api.apps.utils.security import is_root

logger = logging.getLogger(__name__)


@admin.register(RegistrationDataImport)
class RegistrationDataImportAdmin(HOPEModelAdminBase):
    list_display = ("name", "status", "import_date", "data_source", "business_area")
    search_fields = ("name",)
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("data_source", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("imported_by", AutoCompleteFilter),
    )
    date_hierarchy = "updated_at"
    raw_id_fields = ("imported_by", "business_area")
    advanced_filter_fields = (
        "status",
        "updated_at",
        ("imported_by__username", "imported by"),
        ("business_area__name", "business area"),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("business_area")

    @link(
        label="HUB RDI",
        # permission=lambda r, o: r.user.is_superuser,
        # visible=lambda btn: btn.original.status == RegistrationDataImport.IMPORT_ERROR,
    )
    def hub(self, button):
        obj = button.context.get("original")
        if obj:
            return reverse("admin:registration_datahub_registrationdataimportdatahub_change", args=[obj.datahub_id])

        button.visible = False

    @button(
        label="Re-run RDI",
        permission=lambda r, o: r.user.is_superuser,
        enabled=lambda btn: btn.original.status == RegistrationDataImport.IMPORT_ERROR,
    )
    def rerun_rdi(self, request, pk):
        obj = self.get_object(request, pk)
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

            rdi_datahub_obj = get_object_or_404(RegistrationDataImportDatahub, id=obj.datahub_id)
            business_area = BusinessArea.objects.get(slug=rdi_datahub_obj.business_area_slug)

            celery_task.delay(
                registration_data_import_id=str(rdi_datahub_obj.id),
                import_data_id=str(rdi_datahub_obj.import_data.id),
                business_area=str(business_area.id),
            )

            self.message_user(request, "RDI task has started")
        except Exception as e:
            logger.exception(e)
            self.message_user(request, "An error occurred while processing RDI task", messages.ERROR)

    @button(
        label="Re-run Merging RDI",
        permission=lambda r, o: r.user.is_superuser,
        enabled=lambda btn: btn.original.status == RegistrationDataImport.MERGE_ERROR,
    )
    def rerun_merge_rdi(self, request, pk):
        try:
            merge_registration_data_import_task.delay(registration_data_import_id=pk)

            self.message_user(request, "RDI Merge task has started")
        except Exception as e:
            logger.exception(e)
            self.message_user(request, "An error occurred while processing RDI Merge task", messages.ERROR)

    @button(
        permission=is_root,
        enabled=lambda btn: btn.original.status not in [RegistrationDataImport.MERGED, RegistrationDataImport.MERGING],
    )
    def delete_rdi(self, request, pk):
        try:
            if request.method == "POST":
                with transaction.atomic(using="default"):
                    with transaction.atomic(using="registration_datahub"):
                        rdi = RegistrationDataImport.objects.get(pk=pk)
                        rdi_name = rdi.name
                        rdi_datahub = datahub_models.RegistrationDataImportDatahub.objects.get(id=rdi.datahub_id)
                        datahub_individuals_ids = list(
                            datahub_models.ImportedIndividual.objects.filter(
                                registration_data_import=rdi_datahub
                            ).values_list("id", flat=True)
                        )
                        rdi_datahub.delete()
                        rdi.delete()
                        # remove elastic search records linked to individuals
                        remove_elasticsearch_documents_by_matching_ids(
                            datahub_individuals_ids, ImportedIndividualDocument
                        )
                        self.message_user(request, "RDI Deleted")
                        LogEntry.objects.log_action(
                            user_id=request.user.pk,
                            content_type_id=ContentType.objects.get_for_model(self.model).pk,
                            object_id=None,
                            object_repr=f"Removed RDI {rdi_name} id: {pk}",
                            action_flag=DELETION,
                            change_message="RDI removed",
                        )
                        return HttpResponseRedirect(
                            reverse("admin:registration_data_registrationdataimport_changelist")
                        )
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
    def delete_merged_rdi_visible(o, r):
        is_correct_status = o.status == RegistrationDataImport.MERGED
        is_not_used_in_targeting = HouseholdSelection.objects.filter(household__registration_data_import=o).count() == 0
        is_not_used_by_payment_record = PaymentRecord.objects.filter(household__registration_data_import=o).count() == 0
        return is_correct_status and is_not_used_in_targeting and is_not_used_by_payment_record

    @staticmethod
    def generate_query_for_all_grievances_tickets(rdi) -> Q:
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

    @button(
        permission=is_root,
        visible=lambda o, r: RegistrationDataImportAdmin.delete_merged_rdi_visible(o, r),
    )
    def delete_merged_rdi(self, request, pk) -> Optional[HttpResponse]:
        try:
            if request.method == "POST":
                with transaction.atomic(using="default"):
                    with transaction.atomic(using="registration_datahub"):
                        rdi = RegistrationDataImport.objects.get(pk=pk)
                        rdi_name = rdi.name
                        rdi_datahub = datahub_models.RegistrationDataImportDatahub.objects.get(id=rdi.datahub_id)
                        datahub_individuals_ids = list(
                            datahub_models.ImportedIndividual.objects.filter(
                                registration_data_import=rdi_datahub
                            ).values_list("id", flat=True)
                        )
                        individuals_ids = list(
                            Individual.objects.filter(registration_data_import=rdi).values_list("id", flat=True)
                        )
                        rdi_datahub.delete()
                        GrievanceTicket.objects.filter(
                            RegistrationDataImportAdmin.generate_query_for_all_grievances_tickets(rdi)
                        ).filter(business_area=rdi.business_area).delete()
                        rdi.delete()
                        # remove elastic search records linked to individuals
                        remove_elasticsearch_documents_by_matching_ids(
                            datahub_individuals_ids, ImportedIndividualDocument
                        )
                        remove_elasticsearch_documents_by_matching_ids(individuals_ids, IndividualDocument)
                        self.message_user(request, "RDI Deleted")
                        LogEntry.objects.log_action(
                            user_id=request.user.pk,
                            content_type_id=ContentType.objects.get_for_model(self.model).pk,
                            object_id=None,
                            object_repr=f"Removed RDI {rdi_name} id: {pk}",
                            action_flag=DELETION,
                            change_message="RDI removed",
                        )
                        return HttpResponseRedirect(
                            reverse("admin:registration_data_registrationdataimport_changelist")
                        )
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
            return None

    @button()
    def households(self, request, pk):
        url = reverse("admin:household_household_changelist")
        return HttpResponseRedirect(f"{url}?&registration_data_import__exact={pk}")
