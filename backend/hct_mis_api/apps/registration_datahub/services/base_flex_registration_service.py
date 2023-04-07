import abc
import base64
import hashlib
import logging
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Type, Union

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.transaction import atomic
from django.forms import modelform_factory

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    process_flex_records_task,
    rdi_deduplication_task,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportData,
    ImportedHousehold,
    ImportedIndividual,
    Record,
    RegistrationDataImportDatahub,
)

if TYPE_CHECKING:
    from uuid import UUID

logger = logging.getLogger(__name__)


class BaseRegistrationService(abc.ABC):
    BUSINESS_AREA_SLUG = ""
    REGISTRATION_ID = tuple()
    PROCESS_FLEX_RECORDS_TASK = process_flex_records_task

    @atomic("default")
    @atomic("registration_datahub")
    def create_rdi(self, imported_by: Optional[Any], rdi_name: str = "rdi_name") -> RegistrationDataImport:
        business_area = BusinessArea.objects.get(slug=self.BUSINESS_AREA_SLUG)
        number_of_individuals = 0
        number_of_households = 0

        rdi = RegistrationDataImport.objects.create(
            name=rdi_name,
            data_source=RegistrationDataImport.FLEX_REGISTRATION,
            imported_by=imported_by,
            number_of_individuals=number_of_individuals,
            number_of_households=number_of_households,
            business_area=business_area,
            status=RegistrationDataImport.IMPORTING,
        )

        import_data = ImportData.objects.create(
            status=ImportData.STATUS_PENDING,
            business_area_slug=business_area.slug,
            data_type=ImportData.FLEX_REGISTRATION,
            number_of_individuals=number_of_individuals,
            number_of_households=number_of_households,
            created_by_id=imported_by.id if imported_by else None,
        )
        rdi_datahub = RegistrationDataImportDatahub.objects.create(
            name=rdi_name,
            hct_id=rdi.id,
            import_data=import_data,
            import_done=RegistrationDataImportDatahub.NOT_STARTED,
            business_area_slug=business_area.slug,
        )
        rdi.datahub_id = rdi_datahub.id
        rdi.save(update_fields=("datahub_id",))
        return rdi

    @abc.abstractmethod
    def create_household_for_rdi_household(self, record: Record, rdi_datahub: RegistrationDataImportDatahub) -> None:
        raise NotImplementedError

    def process_records(
        self,
        rdi_id: "UUID",
        records_ids: Iterable,
    ) -> None:
        rdi = RegistrationDataImport.objects.get(id=rdi_id)
        rdi_datahub = RegistrationDataImportDatahub.objects.get(id=rdi.datahub_id)
        import_data = rdi_datahub.import_data

        records_ids_to_import = (
            Record.objects.filter(id__in=records_ids)
            .exclude(status=Record.STATUS_IMPORTED)
            .exclude(ignored=True)
            .values_list("id", flat=True)
        )
        imported_records_ids = []
        records_with_error = []

        try:
            with atomic("registration_datahub"):
                for record_id in records_ids_to_import:
                    record = Record.objects.defer("data").get(id=record_id)
                    try:
                        self.create_household_for_rdi_household(record, rdi_datahub)
                        imported_records_ids.append(record_id)
                    except ValidationError as e:
                        logger.exception(e)
                        records_with_error.append((record, str(e)))

                # rollback if at least one Record is invalid
                if records_with_error:
                    transaction.set_rollback(True, using="registration_datahub")

            if not records_with_error:
                number_of_individuals = ImportedIndividual.objects.filter(registration_data_import=rdi_datahub).count()
                number_of_households = ImportedHousehold.objects.filter(registration_data_import=rdi_datahub).count()

                import_data.number_of_individuals = number_of_individuals
                rdi.number_of_individuals = number_of_individuals
                import_data.number_of_households = number_of_households
                rdi.number_of_households = number_of_households
                rdi.status = RegistrationDataImport.DEDUPLICATION

                rdi.save(
                    update_fields=(
                        "number_of_individuals",
                        "number_of_households",
                        "status",
                    )
                )
                import_data.save(
                    update_fields=(
                        "number_of_individuals",
                        "number_of_households",
                    )
                )
                Record.objects.filter(id__in=imported_records_ids).update(
                    status=Record.STATUS_IMPORTED, registration_data_import=rdi_datahub
                )
                if not rdi.business_area.postpone_deduplication:
                    transaction.on_commit(lambda: rdi_deduplication_task.delay(rdi_datahub.id))
                else:
                    rdi.status = RegistrationDataImport.IN_REVIEW
                    rdi.save()

            else:
                # at least one Record from records_ids_to_import has error
                rdi.status = RegistrationDataImport.IMPORT_ERROR
                rdi.error_message = "Records with errors were found during processing"
                rdi.save(
                    update_fields=(
                        "status",
                        "error_message",
                    )
                )
                # mark invalid Records
                for record, error in records_with_error:
                    record.mark_as_invalid(error)

        except Exception as e:
            rdi.status = RegistrationDataImport.IMPORT_ERROR
            rdi.error_message = str(e)
            rdi.save(
                update_fields=(
                    "status",
                    "error_message",
                )
            )
            raise

    def _create_object_and_validate(self, data: Dict, model_class: Type) -> Any:
        ModelClassForm = modelform_factory(model_class, fields=list(data.keys()))
        form = ModelClassForm(data)
        if not form.is_valid():
            raise ValidationError(form.errors)
        return form.save()

    def _prepare_picture_from_base64(self, certificate_picture: Any, document_number: str) -> Union[ContentFile, Any]:
        if certificate_picture:
            format_image = "jpg"
            name = hashlib.md5(document_number.encode()).hexdigest()
            certificate_picture = ContentFile(base64.b64decode(certificate_picture), name=f"{name}.{format_image}")
        return certificate_picture

    def _check_registration_id(self, record_registration: int, error_msg: str = "") -> None:
        if record_registration not in self.REGISTRATION_ID:
            raise ValidationError(error_msg)
