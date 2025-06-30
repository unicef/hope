import logging
from functools import partial
from typing import IO, TYPE_CHECKING, Any, Dict, Optional, Tuple

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

import graphene
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

from hct_mis_api.apps.account.permissions import PermissionMutation, Permissions
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.scalars import BigInt
from hct_mis_api.apps.core.utils import (
    check_concurrency_version_in_mutation,
    decode_id_string,
    decode_id_string_required,
)
from hct_mis_api.apps.core.validators import BaseValidator, raise_program_status_is
from hct_mis_api.apps.household.documents import get_individual_doc
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import (
    ImportData,
    KoboImportData,
    RegistrationDataImport,
)
from hct_mis_api.apps.registration_data.schema import RegistrationDataImportNode
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    merge_registration_data_import_task,
    pull_kobo_submissions_task,
    rdi_deduplication_task,
    registration_kobo_import_task,
    registration_program_population_import_task,
    registration_xlsx_import_task,
    validate_xlsx_import_task,
)
from hct_mis_api.apps.registration_datahub.inputs import (
    RegistrationKoboImportMutationInput,
    RegistrationProgramPopulationImportMutationInput,
    RegistrationXlsxImportMutationInput,
)
from hct_mis_api.apps.registration_datahub.schema import (
    ImportDataNode,
    KoboImportDataNode,
    XlsxRowErrorNode,
)
from hct_mis_api.apps.registration_datahub.utils import get_rdi_program_population
from hct_mis_api.apps.utils.elasticsearch_utils import (
    remove_elasticsearch_documents_by_matching_ids,
)
from hct_mis_api.apps.utils.mutations import ValidationErrorMutationMixin

if TYPE_CHECKING:
    from uuid import UUID

    from hct_mis_api.apps.account.models import User


logger = logging.getLogger(__name__)


@transaction.atomic()
def create_registration_data_import_objects(
    registration_data_import_data: Dict,
    user: "User",
    data_source: str,
) -> Tuple[RegistrationDataImport, ImportData, BusinessArea]:
    import_data_id = decode_id_string(registration_data_import_data.pop("import_data_id"))
    import_data_obj = ImportData.objects.get(id=import_data_id)

    business_area = BusinessArea.objects.get(slug=registration_data_import_data.pop("business_area_slug"))
    pull_pictures = registration_data_import_data.pop("pull_pictures", True)
    screen_beneficiary = registration_data_import_data.pop("screen_beneficiary", False)
    program_id = registration_data_import_data.pop("program_id", None)
    created_obj_hct = RegistrationDataImport(
        status=RegistrationDataImport.IMPORTING,
        imported_by=user,
        data_source=data_source,
        number_of_individuals=import_data_obj.number_of_individuals,
        number_of_households=import_data_obj.number_of_households,
        business_area=business_area,
        pull_pictures=pull_pictures,
        screen_beneficiary=screen_beneficiary,
        program_id=program_id,
        import_data=import_data_obj,
        **registration_data_import_data,
    )
    program = Program.objects.get(id=program_id)
    if program.biometric_deduplication_enabled:
        created_obj_hct.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_PENDING

    created_obj_hct.full_clean()
    created_obj_hct.save()

    return (
        created_obj_hct,
        import_data_obj,
        business_area,
    )


@transaction.atomic()
def create_registration_data_import_for_import_program_population(
    registration_data_import_data: Dict,
    user: "User",
    import_to_program_id: str,
) -> Tuple[RegistrationDataImport, BusinessArea]:
    business_area = BusinessArea.objects.get(slug=registration_data_import_data.pop("business_area_slug"))
    pull_pictures = registration_data_import_data.pop("pull_pictures", True)
    screen_beneficiary = registration_data_import_data.pop("screen_beneficiary", False)
    import_from_program_id = registration_data_import_data.pop("import_from_program_id")
    import_from_ids = registration_data_import_data.get("import_from_ids")

    households, individuals = get_rdi_program_population(import_from_program_id, import_to_program_id, import_from_ids)
    created_obj_hct = RegistrationDataImport(
        status=RegistrationDataImport.IMPORTING,
        imported_by=user,
        data_source=RegistrationDataImport.PROGRAM_POPULATION,
        number_of_individuals=individuals.count(),
        number_of_households=households.count(),
        business_area=business_area,
        pull_pictures=pull_pictures,
        screen_beneficiary=screen_beneficiary,
        program_id=import_to_program_id,
        **registration_data_import_data,
    )
    created_obj_hct.full_clean()
    created_obj_hct.save()

    return (
        created_obj_hct,
        business_area,
    )


class RegistrationXlsxImportMutation(BaseValidator, PermissionMutation, ValidationErrorMutationMixin):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        registration_data_import_data = RegistrationXlsxImportMutationInput(required=True)

    @classmethod
    def validate_import_data(cls, import_data_id: Optional[str]) -> None:
        import_data = get_object_or_404(ImportData, id=decode_id_string(import_data_id))
        if import_data.status != ImportData.STATUS_FINISHED:
            raise ValidationError("Cannot import file containing validation errors")

        if import_data.number_of_households == 0 and import_data.number_of_individuals == 0:  # pragma: no cover
            raise ValidationError("Cannot import empty form")

    @classmethod
    @transaction.atomic()
    @is_authenticated
    def processed_mutate(
        cls, root: Any, info: Any, registration_data_import_data: Dict
    ) -> "RegistrationXlsxImportMutation":
        cls.validate_import_data(registration_data_import_data.import_data_id)

        program_id: str = decode_id_string_required(info.context.headers.get("Program"))
        program = Program.objects.get(id=program_id)
        if program.status == Program.FINISHED:
            raise ValidationError("In order to proceed this action, program status must not be finished")

        registration_data_import_data["program_id"] = program_id
        (
            created_obj_hct,
            import_data_obj,
            business_area,
        ) = create_registration_data_import_objects(registration_data_import_data, info.context.user, "XLS")

        cls.has_permission(info, Permissions.RDI_IMPORT_DATA, business_area)

        if created_obj_hct.should_check_against_sanction_list() and not created_obj_hct.program.sanction_lists.exists():
            raise ValidationError("Cannot check against sanction list")
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            program_id,
            None,
            created_obj_hct,
        )

        created_obj_hct.status = RegistrationDataImport.IMPORT_SCHEDULED
        created_obj_hct.save(update_fields=["status"])

        transaction.on_commit(
            lambda: registration_xlsx_import_task.delay(
                registration_data_import_id=str(created_obj_hct.id),
                import_data_id=str(import_data_obj.id),
                business_area_id=str(business_area.id),
                program_id=str(program_id),
            )
        )

        return RegistrationXlsxImportMutation(registration_data_import=created_obj_hct)


class RegistrationProgramPopulationImportMutation(BaseValidator, PermissionMutation, ValidationErrorMutationMixin):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        registration_data_import_data = RegistrationProgramPopulationImportMutationInput(required=True)

    @classmethod
    @transaction.atomic()
    @is_authenticated
    def processed_mutate(
        cls, root: Any, info: Any, registration_data_import_data: Dict
    ) -> "RegistrationProgramPopulationImportMutation":
        import_to_program_id: str = decode_id_string_required(info.context.headers.get("Program"))
        program = Program.objects.get(id=import_to_program_id)
        import_from_program_id = decode_id_string_required(registration_data_import_data["import_from_program_id"])
        import_from_program = Program.objects.get(id=import_from_program_id)

        if program.status == Program.FINISHED:
            raise ValidationError("In order to proceed this action, program status must not be finished.")

        if program.beneficiary_group != import_from_program.beneficiary_group:
            raise ValidationError("Cannot import data from a program with a different Beneficiary Group.")

        if (
            program.data_collecting_type.code != import_from_program.data_collecting_type.code
            and program.data_collecting_type not in import_from_program.data_collecting_type.compatible_types.all()
        ):
            raise ValidationError("Cannot import data from a program with not compatible data collecting type.")

        registration_data_import_data["import_from_program_id"] = import_from_program_id
        (
            created_obj_hct,
            business_area,
        ) = create_registration_data_import_for_import_program_population(
            registration_data_import_data, info.context.user, import_to_program_id
        )

        cls.has_permission(info, Permissions.RDI_IMPORT_DATA, business_area)

        if created_obj_hct.should_check_against_sanction_list() and not created_obj_hct.program.sanction_lists.exists():
            raise ValidationError("Cannot check against sanction list")

        if created_obj_hct.number_of_households == 0 and created_obj_hct.number_of_individuals == 0:
            raise ValidationError("This action would result in importing 0 households and 0 individuals.")
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            import_to_program_id,
            None,
            created_obj_hct,
        )

        created_obj_hct.status = RegistrationDataImport.IMPORT_SCHEDULED
        created_obj_hct.deduplication_engine_status = (
            RegistrationDataImport.DEDUP_ENGINE_PENDING if program.biometric_deduplication_enabled else None
        )
        created_obj_hct.save(update_fields=["status", "deduplication_engine_status"])

        transaction.on_commit(
            lambda: registration_program_population_import_task.delay(
                registration_data_import_id=str(created_obj_hct.id),
                business_area_id=str(business_area.id),
                import_from_program_id=str(import_from_program_id),
                import_to_program_id=str(import_to_program_id),
            )
        )

        return RegistrationProgramPopulationImportMutation(registration_data_import=created_obj_hct)


class RegistrationDeduplicationMutation(BaseValidator, PermissionMutation):
    ok = graphene.Boolean()

    class Arguments:
        registration_data_import_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    def validate_object_status(cls, rdi_obj: RegistrationDataImport, *args: Any, **kwargs: Any) -> None:
        if rdi_obj.status != RegistrationDataImport.DEDUPLICATION_FAILED:
            logger.warning(
                "Deduplication can only be called when Registration Data Import status is Deduplication Failed"
            )
            raise ValidationError(
                "Deduplication can only be called when Registration Data Import status is Deduplication Failed"
            )

    @classmethod
    @is_authenticated
    @raise_program_status_is(Program.FINISHED)
    def mutate(
        cls, root: Any, info: Any, registration_data_import_id: Optional[str], **kwargs: Any
    ) -> "RegistrationDeduplicationMutation":
        registration_data_import_id = decode_id_string(registration_data_import_id)
        old_rdi_obj = RegistrationDataImport.objects.get(id=registration_data_import_id)
        rdi_obj = RegistrationDataImport.objects.get(id=registration_data_import_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), rdi_obj)
        cls.has_permission(info, Permissions.RDI_RERUN_DEDUPE, rdi_obj.business_area)

        cls.validate(rdi_obj=rdi_obj)

        rdi_obj.status = RegistrationDataImport.DEDUPLICATION
        rdi_obj.save()
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            rdi_obj.program_id,
            old_rdi_obj,
            rdi_obj,
        )
        rdi_deduplication_task.delay(registration_data_import_id=str(registration_data_import_id))

        return cls(ok=True)


class RegistrationKoboImportMutation(BaseValidator, PermissionMutation, ValidationErrorMutationMixin):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        registration_data_import_data = RegistrationKoboImportMutationInput(required=True)

    @classmethod
    @transaction.atomic()
    @is_authenticated
    def processed_mutate(
        cls, root: Any, info: Any, registration_data_import_data: Dict
    ) -> RegistrationXlsxImportMutation:
        RegistrationXlsxImportMutation.validate_import_data(registration_data_import_data.import_data_id)

        program_id: str = decode_id_string_required(info.context.headers.get("Program"))
        program = Program.objects.get(id=program_id)
        if program.status == Program.FINISHED:
            raise ValidationError("In order to proceed this action, program status must not be finished")

        registration_data_import_data["program_id"] = program_id
        (
            created_obj_hct,
            import_data_obj,
            business_area,
        ) = create_registration_data_import_objects(registration_data_import_data, info.context.user, "KOBO")

        cls.has_permission(info, Permissions.RDI_IMPORT_DATA, business_area)

        if created_obj_hct.should_check_against_sanction_list() and not created_obj_hct.program.sanction_lists.exists():
            raise ValidationError("Cannot check against sanction list")
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            program_id,
            None,
            created_obj_hct,
        )

        transaction.on_commit(
            lambda: registration_kobo_import_task.delay(
                registration_data_import_id=str(created_obj_hct.id),
                import_data_id=str(import_data_obj.id),
                business_area_id=str(business_area.id),
                program_id=str(program_id),
            )
        )

        return RegistrationXlsxImportMutation(registration_data_import=created_obj_hct)


class MergeRegistrationDataImportMutation(BaseValidator, PermissionMutation):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @transaction.atomic()
    @is_authenticated
    @raise_program_status_is(Program.FINISHED)
    def mutate(cls, root: Any, info: Any, id: Optional[str], **kwargs: Any) -> "MergeRegistrationDataImportMutation":
        decode_id = decode_id_string(id)
        old_obj_hct = RegistrationDataImport.objects.get(
            id=decode_id,
        )

        obj_hct = RegistrationDataImport.objects.get(
            id=decode_id,
        )
        check_concurrency_version_in_mutation(kwargs.get("version"), obj_hct)

        cls.has_permission(info, Permissions.RDI_MERGE_IMPORT, obj_hct.business_area)
        if not obj_hct.can_be_merged():
            raise ValidationError(f"Can't merge RDI {obj_hct} with {obj_hct.status} status")

        obj_hct.status = RegistrationDataImport.MERGE_SCHEDULED
        obj_hct.save()
        merge_registration_data_import_task.delay(registration_data_import_id=decode_id)
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            obj_hct.program_id,
            old_obj_hct,
            obj_hct,
        )
        return MergeRegistrationDataImportMutation(obj_hct)


class RefuseRegistrationDataImportMutation(BaseValidator, PermissionMutation):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        id = graphene.ID(required=True)
        refuse_reason = graphene.String(required=False)
        version = BigInt(required=False)

    @classmethod
    def validate_object_status(cls, *args: Any, **kwargs: Any) -> None:
        status = kwargs.get("status")
        if status != RegistrationDataImport.IN_REVIEW:
            logger.warning("Only In Review Registration Data Import can be refused")
            raise ValidationError("Only In Review Registration Data Import can be refused")

    @classmethod
    @transaction.atomic()
    @is_authenticated
    @raise_program_status_is(Program.FINISHED)
    def mutate(cls, root: Any, info: Any, id: Optional[str], **kwargs: Any) -> "RefuseRegistrationDataImportMutation":
        decode_id = decode_id_string(id)
        old_obj_hct = RegistrationDataImport.objects.get(id=decode_id)
        obj_hct = RegistrationDataImport.objects.get(id=decode_id)

        check_concurrency_version_in_mutation(kwargs.get("version"), obj_hct)

        cls.has_permission(info, Permissions.RDI_REFUSE_IMPORT, obj_hct.business_area)
        cls.validate(status=obj_hct.status)

        Household.all_objects.filter(registration_data_import=obj_hct).delete()
        refuse_reason = kwargs.get("refuse_reason")
        if refuse_reason:
            obj_hct.refuse_reason = refuse_reason
        obj_hct.status = RegistrationDataImport.REFUSED_IMPORT
        obj_hct.save()

        individuals_to_remove = Individual.all_objects.filter(registration_data_import=obj_hct)

        remove_elasticsearch_documents_by_matching_ids(
            list(individuals_to_remove.values_list("id", flat=True)),
            get_individual_doc(obj_hct.business_area.slug),
        )
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            obj_hct.program_id,
            old_obj_hct,
            obj_hct,
        )
        return RefuseRegistrationDataImportMutation(obj_hct)


class EraseRegistrationDataImportMutation(PermissionMutation):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @transaction.atomic()
    @is_authenticated
    @raise_program_status_is(Program.FINISHED)
    def mutate(cls, root: Any, info: Any, id: Optional[str], **kwargs: Any) -> "EraseRegistrationDataImportMutation":
        decode_id = decode_id_string(id)
        old_obj_hct = RegistrationDataImport.objects.get(id=decode_id)
        obj_hct = RegistrationDataImport.objects.get(id=decode_id)

        check_concurrency_version_in_mutation(kwargs.get("version"), obj_hct)

        cls.has_permission(info, Permissions.RDI_REFUSE_IMPORT, obj_hct.business_area)

        if obj_hct.status not in (
            RegistrationDataImport.IMPORT_ERROR,
            RegistrationDataImport.MERGE_ERROR,
            RegistrationDataImport.DEDUPLICATION_FAILED,
        ):
            msg = "RDI can be erased only when status is: IMPORT_ERROR, MERGE_ERROR, DEDUPLICATION_FAILED"
            logger.warning(msg)
            raise GraphQLError(msg)

        Household.all_objects.filter(registration_data_import=obj_hct).delete()

        obj_hct.erased = True
        obj_hct.save()

        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            obj_hct.program_id,
            old_obj_hct,
            obj_hct,
        )
        return EraseRegistrationDataImportMutation(registration_data_import=obj_hct)


class UploadImportDataXLSXFileAsync(PermissionMutation):
    import_data = graphene.Field(ImportDataNode)
    errors = graphene.List(XlsxRowErrorNode)

    class Arguments:
        file = Upload(required=True)
        business_area_slug = graphene.String(required=True)

    @classmethod
    @transaction.atomic()
    @is_authenticated
    def mutate(cls, root: Any, info: Any, file: IO, business_area_slug: str) -> "UploadImportDataXLSXFileAsync":
        cls.has_permission(info, Permissions.RDI_IMPORT_DATA, business_area_slug)
        program_id: str = decode_id_string_required(info.context.headers.get("Program"))
        import_data = ImportData.objects.create(
            file=file,
            data_type=ImportData.XLSX,
            status=ImportData.STATUS_PENDING,
            created_by_id=info.context.user.id,
            business_area_slug=business_area_slug,
        )
        transaction.on_commit(partial(validate_xlsx_import_task.delay, import_data.id, program_id))
        return UploadImportDataXLSXFileAsync(import_data, [])


class SaveKoboProjectImportDataAsync(PermissionMutation):
    import_data = graphene.Field(KoboImportDataNode)

    class Arguments:
        uid = Upload(required=True)
        business_area_slug = graphene.String(required=True)
        only_active_submissions = graphene.Boolean(required=True)
        pull_pictures = graphene.Boolean(required=True)

    @classmethod
    @is_authenticated
    def mutate(
        cls,
        root: Any,
        info: Any,
        uid: "UUID",
        business_area_slug: str,
        only_active_submissions: bool,
        pull_pictures: bool,
    ) -> "SaveKoboProjectImportDataAsync":
        cls.has_permission(info, Permissions.RDI_IMPORT_DATA, business_area_slug)
        program_id: str = decode_id_string_required(info.context.headers.get("Program"))

        import_data = KoboImportData.objects.create(
            data_type=ImportData.JSON,
            kobo_asset_id=uid,
            only_active_submissions=only_active_submissions,
            status=ImportData.STATUS_PENDING,
            business_area_slug=business_area_slug,
            created_by_id=info.context.user.id,
            pull_pictures=pull_pictures,
        )
        pull_kobo_submissions_task.delay(import_data.id, program_id)
        return SaveKoboProjectImportDataAsync(import_data=import_data)


class DeleteRegistrationDataImport(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        registration_data_import_id = graphene.String(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root: Any, info: Any, **kwargs: Any) -> "DeleteRegistrationDataImport":
        decoded_id = decode_id_string(kwargs.get("registration_data_import_id"))
        rdi_obj = RegistrationDataImport.objects.get(id=decoded_id)
        program_id = rdi_obj.program_id
        rdi_obj.delete()
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program_id, rdi_obj, None
        )
        return cls(ok=True)


class Mutations(graphene.ObjectType):
    upload_import_data_xlsx_file_async = UploadImportDataXLSXFileAsync.Field()
    delete_registration_data_import = DeleteRegistrationDataImport.Field()
    registration_xlsx_import = RegistrationXlsxImportMutation.Field()
    registration_program_population_import = RegistrationProgramPopulationImportMutation.Field()
    registration_kobo_import = RegistrationKoboImportMutation.Field()
    save_kobo_import_data_async = SaveKoboProjectImportDataAsync.Field()
    merge_registration_data_import = MergeRegistrationDataImportMutation.Field()
    refuse_registration_data_import = RefuseRegistrationDataImportMutation.Field()
    rerun_dedupe = RegistrationDeduplicationMutation.Field()
    erase_registration_data_import = EraseRegistrationDataImportMutation.Field()
