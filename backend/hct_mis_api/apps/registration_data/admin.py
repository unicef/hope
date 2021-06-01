import logging

from admin_extra_urls.decorators import button
from admin_extra_urls.extras import ExtraUrlMixin
from adminfilters.filters import ChoicesFieldComboFilter
from django.contrib import admin, messages
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    merge_registration_data_import_task,
)
from hct_mis_api.apps.registration_datahub.models import RegistrationDataImportDatahub
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase

logger = logging.getLogger(__name__)


@admin.register(RegistrationDataImport)
class RegistrationDataImportAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("data_source", ChoicesFieldComboFilter),
    )
    date_hierarchy = "updated_at"

    @button(
        label="Re-run RDI",
        permission=lambda r, o: r.user.is_superuser,
        visible=lambda o: o.status == RegistrationDataImport.IMPORT_ERROR,
    )
    def rerun_rdi(self, request, pk):
        obj = self.get_object(request, pk)
        try:
            if obj.data_source == RegistrationDataImport.XLS:
                from hct_mis_api.apps.registration_datahub.celery_tasks import registration_xlsx_import_task

                celery_task = registration_xlsx_import_task
            else:
                from hct_mis_api.apps.registration_datahub.celery_tasks import registration_kobo_import_task

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
        visible=lambda o: o.status == RegistrationDataImport.MERGE_ERROR,
    )
    def rerun_merge_rdi(self, request, pk):
        try:
            merge_registration_data_import_task.delay(registration_data_import_id=pk)

            self.message_user(request, "RDI Merge task has started")
        except Exception as e:
            logger.exception(e)
            self.message_user(request, "An error occurred while processing RDI Merge task", messages.ERROR)
