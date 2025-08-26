import logging
from typing import Any

from constance import config
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from hope.api.caches import etag_decorator
from hope.apps.account.permissions import Permissions
from hope.models.log_entry import log_create
from hope.apps.core.api.mixins import (
    BaseViewSet,
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
)
from hope.apps.core.api.serializers import ChoiceSerializer
from hope.apps.core.utils import check_concurrency_version_in_mutation, to_choice_object
from hope.apps.household.documents import get_individual_doc
from hope.models.household import Household
from hope.models.individual import Individual
from hope.models.program import Program
from hope.apps.registration_data.api.caches import RDIKeyConstructor
from hope.apps.registration_data.api.serializers import (
    RefuseRdiSerializer,
    RegistrationDataImportCreateSerializer,
    RegistrationDataImportDetailSerializer,
    RegistrationDataImportListSerializer,
    RegistrationKoboImportSerializer,
    RegistrationXlsxImportSerializer,
)
from hope.apps.registration_data.filters import RegistrationDataImportFilter
from hope.models.registration_data_import import (
    RegistrationDataImport,
)
from hope.models.import_data import ImportData
from hope.models.kobo_import_data import KoboImportData
from hope.apps.registration_datahub.celery_tasks import (
    deduplication_engine_process,
    fetch_biometric_deduplication_results_and_process,
    merge_registration_data_import_task,
    rdi_deduplication_task,
    registration_kobo_import_task,
    registration_program_population_import_task,
    registration_xlsx_import_task,
)
from hope.apps.utils.elasticsearch_utils import (
    remove_elasticsearch_documents_by_matching_ids,
)

# Import moved inline to avoid circular dependency issues

logger = logging.getLogger(__name__)


class RegistrationDataImportViewSet(
    ProgramMixin,
    SerializerActionMixin,
    CountActionMixin,
    RetrieveModelMixin,
    ListModelMixin,
    BaseViewSet,
):
    queryset = RegistrationDataImport.objects.order_by("-created_at")
    serializer_classes_by_action = {
        "list": RegistrationDataImportListSerializer,
        "retrieve": RegistrationDataImportDetailSerializer,
        "refuse": RefuseRdiSerializer,
        "create": RegistrationDataImportCreateSerializer,
        "status_choices": ChoiceSerializer,
        "registration_xlsx_import": RegistrationXlsxImportSerializer,
        "registration_kobo_import": RegistrationKoboImportSerializer,
    }
    permissions_by_action = {
        "list": [
            Permissions.RDI_VIEW_LIST,
        ],
        "retrieve": [
            Permissions.RDI_VIEW_DETAILS,
        ],
        "create": [Permissions.RDI_IMPORT_DATA],
        "merge": [Permissions.RDI_MERGE_IMPORT],
        "erase": [Permissions.RDI_REFUSE_IMPORT],
        "refuse": [Permissions.RDI_REFUSE_IMPORT],
        "deduplicate": [Permissions.RDI_RERUN_DEDUPE],
        "run_deduplication": [Permissions.RDI_RERUN_DEDUPE],
        "status_choices": [
            Permissions.RDI_VIEW_LIST,
        ],
        "registration_xlsx_import": [Permissions.RDI_IMPORT_DATA],
        "registration_kobo_import": [Permissions.RDI_IMPORT_DATA],
    }
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = RegistrationDataImportFilter

    @etag_decorator(RDIKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=RDIKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["POST"], url_path="run-deduplication")
    def run_deduplication(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        deduplication_engine_process.delay(str(self.program.id))
        return Response({"message": "Deduplication process started"}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["GET"],
        url_path="webhookdeduplication",
        url_name="webhook-deduplication",
        permission_classes=[AllowAny],
    )
    def webhook_deduplication(
        self,
        request: Request,
        business_area_slug: str,
        program_slug: str,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        program = Program.objects.get(business_area__slug=business_area_slug, slug=program_slug)
        fetch_biometric_deduplication_results_and_process.delay(program.deduplication_set_id)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def merge(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        rdi = self.get_object()
        old_rdi = RegistrationDataImport.objects.get(
            id=rdi.id,
        )
        check_concurrency_version_in_mutation(kwargs.get("version"), rdi)

        if not rdi.can_be_merged():
            raise ValidationError(f"Can't merge RDI {rdi} with {rdi.status} status")

        rdi.status = RegistrationDataImport.MERGE_SCHEDULED
        rdi.save()
        merge_registration_data_import_task.delay(registration_data_import_id=rdi.id)
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            rdi.program_id,
            old_rdi,
            rdi,
        )
        return Response(
            status=status.HTTP_200_OK,
            data={"message": "Registration Data Import Merge Scheduled"},
        )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def erase(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        rdi = self.get_object()
        old_rdi = RegistrationDataImport.objects.get(
            id=rdi.id,
        )

        if rdi.status not in (
            RegistrationDataImport.IMPORT_ERROR,
            RegistrationDataImport.MERGE_ERROR,
            RegistrationDataImport.DEDUPLICATION_FAILED,
        ):
            msg = "RDI can be erased only when status is: IMPORT_ERROR, MERGE_ERROR, DEDUPLICATION_FAILED"
            logger.warning(msg)
            raise ValidationError(msg)

        Household.all_objects.filter(registration_data_import=rdi).delete()

        rdi.erased = True
        rdi.save()

        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            rdi.program_id,
            old_rdi,
            rdi,
        )
        return Response(
            status=status.HTTP_200_OK,
            data={"message": "Registration Data Import Erased"},
        )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def refuse(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rdi = self.get_object()
        old_rdi = RegistrationDataImport.objects.get(
            id=rdi.id,
        )

        if rdi.status != RegistrationDataImport.IN_REVIEW:
            logger.warning("Only In Review Registration Data Import can be refused")
            raise ValidationError("Only In Review Registration Data Import can be refused")

        Household.all_objects.filter(registration_data_import=rdi).delete()
        rdi.status = RegistrationDataImport.REFUSED_IMPORT
        rdi.refuse_reason = serializer.validated_data["reason"]
        rdi.save()
        # TODO: Copied from mutation, but in my opinion it is wrong
        individuals_to_remove = Individual.all_objects.filter(registration_data_import=rdi)
        remove_elasticsearch_documents_by_matching_ids(
            list(individuals_to_remove.values_list("id", flat=True)),
            get_individual_doc(rdi.business_area.slug),
        )

        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            rdi.program_id,
            old_rdi,
            rdi,
        )
        return Response(
            status=status.HTTP_200_OK,
            data={"message": "Registration Data Import Refused"},
        )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def deduplicate(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        rdi = self.get_object()
        old_rdi = RegistrationDataImport.objects.get(
            id=rdi.id,
        )

        if rdi.status != RegistrationDataImport.DEDUPLICATION_FAILED:
            logger.warning(
                "Deduplication can only be called when Registration Data Import status is Deduplication Failed"
            )
            raise ValidationError(
                "Deduplication can only be called when Registration Data Import status is Deduplication Failed"
            )
        rdi.status = RegistrationDataImport.DEDUPLICATION
        rdi.save()
        rdi_deduplication_task.delay(registration_data_import_id=str(rdi.id))
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            rdi.program_id,
            old_rdi,
            rdi,
        )
        return Response(
            status=status.HTTP_200_OK,
            data={"message": "Registration Data Import Erased"},
        )

    @extend_schema(
        request=RegistrationDataImportCreateSerializer,
        responses=RegistrationDataImportDetailSerializer,
    )
    @transaction.atomic
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registration_data_import = serializer.get_object(serializer.validated_data)
        import_from_program_id = serializer.validated_data["import_from_program_id"]
        import_from_program = Program.objects.get(id=import_from_program_id)
        if self.program.status == Program.FINISHED:
            raise ValidationError("In order to perform this action, program status must not be finished.")

        if self.program.beneficiary_group != import_from_program.beneficiary_group:
            raise ValidationError("Cannot import data from a program with a different Beneficiary Group.")

        if (
            self.program.data_collecting_type.code != import_from_program.data_collecting_type.code
            and self.program.data_collecting_type not in import_from_program.data_collecting_type.compatible_types.all()
        ):
            raise ValidationError("Cannot import data from a program with not compatible data collecting type.")
        if registration_data_import.should_check_against_sanction_list() and not self.program.screen_beneficiary:
            raise ValidationError("Cannot check against sanction list.")

        if registration_data_import.number_of_households == 0 and registration_data_import.number_of_individuals == 0:
            raise ValidationError("This action would result in importing 0 households and 0 individuals.")
        registration_data_import.status = RegistrationDataImport.IMPORT_SCHEDULED
        registration_data_import.deduplication_engine_status = (
            RegistrationDataImport.DEDUP_ENGINE_PENDING if self.program.biometric_deduplication_enabled else None
        )
        registration_data_import.save(update_fields=["status", "deduplication_engine_status"])
        transaction.on_commit(
            lambda: registration_program_population_import_task.delay(
                registration_data_import_id=str(registration_data_import.id),
                business_area_id=str(registration_data_import.business_area.id),
                import_from_program_id=str(import_from_program_id),
                import_to_program_id=str(self.program.id),
            )
        )
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            self.program.id,
            None,
            registration_data_import,
        )

        detail_serializer = RegistrationDataImportDetailSerializer(
            registration_data_import, context=self.get_serializer_context()
        )
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        responses=ChoiceSerializer(many=True),
        filters=False,
    )
    @action(
        detail=False,
        methods=["get"],
        pagination_class=None,
        url_path="status-choices",
    )
    def status_choices(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        status_choices = to_choice_object(RegistrationDataImport.STATUS_CHOICE)

        return Response(status=200, data=self.get_serializer(status_choices, many=True).data)

    @extend_schema(
        request=RegistrationXlsxImportSerializer,
        responses=RegistrationDataImportDetailSerializer,
    )
    @action(detail=False, methods=["post"], url_path="registration-xlsx-import")
    @transaction.atomic
    def registration_xlsx_import(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Import registration data from an XLSX file."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if self.program.status == Program.FINISHED:
            raise ValidationError("In order to perform this action, program status must not be finished.")

        validated_data = serializer.validated_data.copy()
        validated_data["business_area_slug"] = self.business_area.slug
        validated_data["program_id"] = str(self.program.id)

        # Validate import data exists and is finished
        import_data_id = validated_data["import_data_id"]
        import_data = ImportData.objects.filter(id=import_data_id).first()
        if not import_data:
            raise ValidationError("Import data not found")
        if import_data.status != ImportData.STATUS_FINISHED:
            raise ValidationError("Import data is not ready for import")

        # Create RDI objects inline instead of using GraphQL mutation helpers
        from hope.models.business_area import BusinessArea

        import_data_id = validated_data.pop("import_data_id")
        import_data_obj = ImportData.objects.get(id=import_data_id)
        business_area = BusinessArea.objects.get(slug=validated_data.pop("business_area_slug"))

        registration_data_import = RegistrationDataImport(
            status=RegistrationDataImport.IMPORTING,
            imported_by=request.user,
            data_source=RegistrationDataImport.XLS,
            number_of_individuals=import_data_obj.number_of_individuals,
            number_of_households=import_data_obj.number_of_households,
            business_area=business_area,
            screen_beneficiary=validated_data.pop("screen_beneficiary", False),
            program_id=validated_data.pop("program_id"),
            import_data=import_data_obj,
            **validated_data,
        )

        if self.program.biometric_deduplication_enabled:
            registration_data_import.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_PENDING

        registration_data_import.full_clean()
        registration_data_import.save()

        # Update status to IMPORT_SCHEDULED after save
        registration_data_import.status = RegistrationDataImport.IMPORT_SCHEDULED
        registration_data_import.save(update_fields=["status"])

        transaction.on_commit(
            lambda: registration_xlsx_import_task.delay(
                registration_data_import_id=str(registration_data_import.id),
                import_data_id=str(import_data_obj.id),
                business_area_id=str(business_area.id),
                program_id=str(self.program.id),
            )
        )

        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            registration_data_import.program_id,
            None,
            registration_data_import,
        )

        return Response(
            RegistrationDataImportDetailSerializer(
                registration_data_import, context=self.get_serializer_context()
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=RegistrationKoboImportSerializer,
        responses=RegistrationDataImportDetailSerializer,
    )
    @action(detail=False, methods=["post"], url_path="registration-kobo-import")
    @transaction.atomic
    def registration_kobo_import(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Import registration data from KoBo."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if self.program.status == Program.FINISHED:
            raise ValidationError("In order to perform this action, program status must not be finished.")

        validated_data = serializer.validated_data.copy()
        validated_data["business_area_slug"] = self.business_area.slug
        validated_data["program_id"] = str(self.program.id)

        # Validate import data exists and is finished
        import_data_id = validated_data["import_data_id"]
        import_data = KoboImportData.objects.filter(id=import_data_id).first()
        if not import_data:
            raise ValidationError("Kobo import data not found")
        if import_data.status != ImportData.STATUS_FINISHED:
            raise ValidationError("Kobo import data is not ready for import")

        # Create RDI objects inline instead of using GraphQL mutation helpers
        from hope.models.business_area import BusinessArea

        import_data_id = validated_data.pop("import_data_id")
        import_data_obj = KoboImportData.objects.get(id=import_data_id)
        business_area = BusinessArea.objects.get(slug=validated_data.pop("business_area_slug"))

        registration_data_import = RegistrationDataImport(
            status=RegistrationDataImport.IMPORTING,
            imported_by=request.user,
            data_source=RegistrationDataImport.KOBO,
            number_of_individuals=import_data_obj.number_of_individuals,
            number_of_households=import_data_obj.number_of_households,
            business_area=business_area,
            screen_beneficiary=validated_data.pop("screen_beneficiary", False),
            program_id=validated_data.pop("program_id"),
            import_data=import_data_obj,
            **validated_data,
        )

        if self.program.biometric_deduplication_enabled:
            registration_data_import.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_PENDING

        registration_data_import.full_clean()
        registration_data_import.save()

        # Update status to IMPORT_SCHEDULED after save
        registration_data_import.status = RegistrationDataImport.IMPORT_SCHEDULED
        registration_data_import.save(update_fields=["status"])

        transaction.on_commit(
            lambda: registration_kobo_import_task.delay(
                registration_data_import_id=str(registration_data_import.id),
                import_data_id=str(import_data_obj.id),
                business_area_id=str(business_area.id),
                program_id=str(self.program.id),
            )
        )

        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            registration_data_import.program_id,
            None,
            registration_data_import,
        )

        return Response(
            RegistrationDataImportDetailSerializer(
                registration_data_import, context=self.get_serializer_context()
            ).data,
            status=status.HTTP_201_CREATED,
        )
