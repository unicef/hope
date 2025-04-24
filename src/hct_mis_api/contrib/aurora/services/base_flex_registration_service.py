import abc
import base64
import hashlib
import logging
import uuid
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Union

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.transaction import atomic
from django.forms import modelform_factory

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import PendingHousehold, PendingIndividual
from hct_mis_api.apps.registration_data.models import ImportData, RegistrationDataImport
from hct_mis_api.apps.registration_datahub.celery_tasks import rdi_deduplication_task
from hct_mis_api.contrib.aurora.celery_tasks import process_flex_records_task
from hct_mis_api.contrib.aurora.models import Record, Registration
from hct_mis_api.contrib.aurora.rdi import AuroraProcessor

if TYPE_CHECKING:
    from uuid import UUID

logger = logging.getLogger(__name__)


class BaseRegistrationService(AuroraProcessor, abc.ABC):
    PROCESS_FLEX_RECORDS_TASK = process_flex_records_task

    def __init__(self, registration: Registration) -> None:
        self.registration = registration

    @atomic("default")
    def create_rdi(
        self, imported_by: Optional[Any], rdi_name: str = "rdi_name", is_open: bool = False
    ) -> RegistrationDataImport:
        project = self.registration.project
        programme = project.programme
        organization = project.organization
        business_area = BusinessArea.objects.get(slug=organization.slug)

        self.validate_data_collection_type()

        number_of_individuals = 0
        number_of_households = 0
        status = RegistrationDataImport.LOADING if is_open else RegistrationDataImport.IMPORTING

        import_data = ImportData.objects.create(
            status=ImportData.STATUS_PENDING,
            business_area_slug=business_area.slug,
            data_type=ImportData.FLEX_REGISTRATION,
            number_of_individuals=number_of_individuals,
            number_of_households=number_of_households,
            created_by_id=imported_by.id if imported_by else None,
        )
        rdi = RegistrationDataImport.objects.create(
            name=rdi_name,
            data_source=RegistrationDataImport.FLEX_REGISTRATION,
            imported_by=imported_by,
            number_of_individuals=number_of_individuals,
            number_of_households=number_of_households,
            business_area=business_area,
            status=status,
            program=programme,
            import_data=import_data,
            deduplication_engine_status=(
                RegistrationDataImport.DEDUP_ENGINE_PENDING if programme.biometric_deduplication_enabled else None
            ),
        )
        return rdi

    @abc.abstractmethod
    def create_household_for_rdi_household(self, record: Any, rdi_datahub: RegistrationDataImport) -> None:
        raise NotImplementedError

    def validate_data_collection_type(self) -> None:
        project = self.registration.project
        programme = project.programme
        data_collecting_type = programme.data_collecting_type
        business_area = BusinessArea.objects.get(slug=project.organization.slug)

        if not data_collecting_type:
            raise ValidationError("Program of given project does not have any Data Collecting Type")

        if data_collecting_type.deprecated:
            raise ValidationError("Data Collecting Type of program is deprecated")

        if data_collecting_type.limit_to.exists() and business_area not in data_collecting_type.limit_to.all():
            raise ValidationError(
                f"{business_area.slug.capitalize()} is not limited for DataCollectingType: {data_collecting_type.code}"
            )

    def process_records(
        self,
        rdi_id: "UUID",
        records_ids: Iterable,
    ) -> None:
        rdi = RegistrationDataImport.objects.get(id=rdi_id)
        import_data = rdi.import_data

        records_ids_to_import = (
            Record.objects.filter(id__in=records_ids)
            .exclude(status=Record.STATUS_IMPORTED)
            .exclude(ignored=True)
            .values_list("id", flat=True)
        )
        imported_records_ids = []
        records_with_error = []

        try:
            with atomic():
                for record_id in records_ids_to_import:
                    record = Record.objects.defer("data").get(id=record_id)
                    try:
                        self.create_household_for_rdi_household(record, rdi)
                        imported_records_ids.append(record_id)
                    except ValidationError as e:
                        logger.exception(e)
                        records_with_error.append((record, str(e)))

                # rollback if at least one Record is invalid
                if records_with_error:
                    transaction.set_rollback(True)

            if not records_with_error:
                number_of_individuals = PendingIndividual.objects.filter(registration_data_import=rdi).count()
                number_of_households = PendingHousehold.objects.filter(registration_data_import=rdi).count()

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
                Record.objects.filter(id__in=imported_records_ids).update(status=Record.STATUS_IMPORTED)

                if not rdi.business_area.postpone_deduplication:
                    transaction.on_commit(lambda: rdi_deduplication_task.delay(rdi.id))
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

    def _create_object_and_validate(self, data: Dict, model_class: Any, model_form: Optional[Any] = None) -> Any:
        files = {}
        if photo := data.get("photo"):
            files["photo"] = self._prepare_picture_from_base64(photo, str(uuid.uuid4()))
            del data["photo"]  # Remove the base64 from data since we're handling it as a file

        if model_form is None:
            ModelClassForm = modelform_factory(model_class, fields=list(data.keys()) + list(files.keys()))
        else:
            ModelClassForm = modelform_factory(
                model_class, form=model_form, fields=list(data.keys()) + list(files.keys())
            )

        form = ModelClassForm(data=data, files=files)  # type: ignore
        if not form.is_valid():
            raise ValidationError(form.errors)
        return form.save()

    def _prepare_picture_from_base64(self, certificate_picture: Any, document_number: str) -> Union[ContentFile, Any]:
        if certificate_picture:
            format_image = "jpg"
            name = hashlib.md5(document_number.encode()).hexdigest()
            certificate_picture = ContentFile(base64.b64decode(certificate_picture), name=f"{name}.{format_image}")
        return certificate_picture
