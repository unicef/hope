from .base import DjangoOperator


class RegistrationXLSXImportHourlyOperator(DjangoOperator):
    def execute(self, context, **kwargs):
        from core.models import BusinessArea
        from registration_datahub.models import RegistrationDataImportDatahub
        from registration_datahub.tasks.rdi_create import RdiXlsxCreateTask

        not_started_rdi = RegistrationDataImportDatahub.objects.filter(
            import_done=RegistrationDataImportDatahub.NOT_STARTED
        ).first()

        business_area = BusinessArea.objects.get(
            slug=not_started_rdi.business_area_slug
        )

        task = RdiXlsxCreateTask()
        task.execute(
            registration_data_import_id=str(not_started_rdi.id),
            import_data_id=str(not_started_rdi.import_data.id),
            business_area_id=str(business_area.id),
        )
