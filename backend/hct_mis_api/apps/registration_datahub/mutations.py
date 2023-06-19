import logging
from functools import partial
from typing import IO, TYPE_CHECKING, Any, Dict, Optional, Tuple

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

import graphene
from graphene_file_upload.scalars import Upload

from hct_mis_api.apps.account.permissions import PermissionMutation, Permissions
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.scalars import BigInt
from hct_mis_api.apps.core.utils import (
    check_concurrency_version_in_mutation,
    decode_id_string,
)
from hct_mis_api.apps.core.validators import BaseValidator
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_data.schema import RegistrationDataImportNode
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    merge_registration_data_import_task,
    pull_kobo_submissions_task,
    rdi_deduplication_task,
    registration_kobo_import_task,
    registration_xlsx_import_task,
    validate_xlsx_import_task,
)
from hct_mis_api.apps.registration_datahub.documents import get_imported_individual_doc
from hct_mis_api.apps.registration_datahub.inputs import (
    RegistrationKoboImportMutationInput,
    RegistrationXlsxImportMutationInput,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportData,
    ImportedIndividual,
    KoboImportData,
    RegistrationDataImportDatahub,
)
from hct_mis_api.apps.registration_datahub.schema import (
    ImportDataNode,
    KoboImportDataNode,
    XlsxRowErrorNode,
)
from hct_mis_api.apps.utils.elasticsearch_utils import (
    remove_elasticsearch_documents_by_matching_ids,
)
from hct_mis_api.apps.utils.mutations import ValidationErrorMutationMixin

if TYPE_CHECKING:
    from uuid import UUID

    from hct_mis_api.apps.account.models import User


logger = logging.getLogger(__name__)


@transaction.atomic(using="default")
@transaction.atomic(using="registration_datahub")
def create_registration_data_import_objects(
    registration_data_import_data: Dict, user: "User", data_source: str
) -> Tuple[RegistrationDataImportDatahub, RegistrationDataImport, ImportData, BusinessArea]:
    import_data_id = decode_id_string(registration_data_import_data.pop("import_data_id"))
    import_data_obj = ImportData.objects.get(id=import_data_id)

    business_area = BusinessArea.objects.get(slug=registration_data_import_data.pop("business_area_slug"))
    pull_pictures = registration_data_import_data.pop("pull_pictures", True)
    screen_beneficiary = registration_data_import_data.pop("screen_beneficiary", False)
    created_obj_datahub = RegistrationDataImportDatahub.objects.create(
        business_area_slug=business_area.slug,
        import_data=import_data_obj,
        **registration_data_import_data,
    )
    created_obj_hct = RegistrationDataImport(
        status=RegistrationDataImport.IMPORTING,
        imported_by=user,
        data_source=data_source,
        number_of_individuals=import_data_obj.number_of_individuals,
        number_of_households=import_data_obj.number_of_households,
        business_area=business_area,
        pull_pictures=pull_pictures,
        screen_beneficiary=screen_beneficiary,
        **registration_data_import_data,
    )
    created_obj_hct.full_clean()
    created_obj_hct.save()

    created_obj_datahub.hct_id = created_obj_hct.id
    created_obj_datahub.save()

    created_obj_hct.datahub_id = created_obj_datahub.id
    created_obj_hct.save()

    return (
        created_obj_datahub,
        created_obj_hct,
        import_data_obj,
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

        if import_data.number_of_households == 0 and import_data.number_of_individuals == 0:
            raise ValidationError("Cannot import empty form")

    @classmethod
    @transaction.atomic(using="default")
    @transaction.atomic(using="registration_datahub")
    @is_authenticated
    def processed_mutate(
        cls, root: Any, info: Any, registration_data_import_data: Dict
    ) -> "RegistrationXlsxImportMutation":
        cls.validate_import_data(registration_data_import_data.import_data_id)

        (
            created_obj_datahub,
            created_obj_hct,
            import_data_obj,
            business_area,
        ) = create_registration_data_import_objects(registration_data_import_data, info.context.user, "XLS")

        cls.has_permission(info, Permissions.RDI_IMPORT_DATA, business_area)

        if (
            created_obj_hct.should_check_against_sanction_list()
            and not business_area.should_check_against_sanction_list()
        ):
            raise ValidationError("Cannot check against sanction list")
        # TODO: add 'program' arg or None
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, None, created_obj_hct
        )

        created_obj_hct.status = RegistrationDataImport.IMPORT_SCHEDULED
        created_obj_hct.save(update_fields=["status"])

        transaction.on_commit(
            lambda: registration_xlsx_import_task.delay(
                registration_data_import_id=str(created_obj_datahub.id),
                import_data_id=str(import_data_obj.id),
                business_area_id=str(business_area.id),
            )
        )

        return RegistrationXlsxImportMutation(registration_data_import=created_obj_hct)


class RegistrationDeduplicationMutation(BaseValidator, PermissionMutation):
    ok = graphene.Boolean()

    class Arguments:
        registration_data_import_datahub_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    def validate_object_status(cls, rdi_obj: RegistrationDataImport, *args: Any, **kwargs: Any) -> None:
        if rdi_obj.status != RegistrationDataImport.DEDUPLICATION_FAILED:
            logger.error(
                "Deduplication can only be called when Registration Data Import status is Deduplication Failed"
            )
            raise ValidationError(
                "Deduplication can only be called when Registration Data Import status is Deduplication Failed"
            )

    @classmethod
    @is_authenticated
    def mutate(
        cls, root: Any, info: Any, registration_data_import_datahub_id: Optional[str], **kwargs: Any
    ) -> "RegistrationDeduplicationMutation":
        old_rdi_obj = RegistrationDataImport.objects.get(datahub_id=registration_data_import_datahub_id)
        rdi_obj = RegistrationDataImport.objects.get(datahub_id=registration_data_import_datahub_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), rdi_obj)
        cls.has_permission(info, Permissions.RDI_RERUN_DEDUPE, rdi_obj.business_area)

        cls.validate(rdi_obj=rdi_obj)

        rdi_obj.status = RegistrationDataImport.DEDUPLICATION
        rdi_obj.save()
        # TODO: add 'program' arg or None
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, old_rdi_obj, rdi_obj
        )
        rdi_deduplication_task.delay(registration_data_import_id=str(registration_data_import_datahub_id))

        return cls(ok=True)


class RegistrationKoboImportMutation(BaseValidator, PermissionMutation, ValidationErrorMutationMixin):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        registration_data_import_data = RegistrationKoboImportMutationInput(required=True)

    @classmethod
    @transaction.atomic(using="default")
    @transaction.atomic(using="registration_datahub")
    @is_authenticated
    def processed_mutate(
        cls, root: Any, info: Any, registration_data_import_data: Dict
    ) -> RegistrationXlsxImportMutation:
        RegistrationXlsxImportMutation.validate_import_data(registration_data_import_data.import_data_id)

        (
            created_obj_datahub,
            created_obj_hct,
            import_data_obj,
            business_area,
        ) = create_registration_data_import_objects(registration_data_import_data, info.context.user, "KOBO")

        cls.has_permission(info, Permissions.RDI_IMPORT_DATA, business_area)

        if (
            created_obj_hct.should_check_against_sanction_list()
            and not business_area.should_check_against_sanction_list()
        ):
            raise ValidationError("Cannot check against sanction list")
        # TODO: add 'program' arg or None
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, None, created_obj_hct
        )

        transaction.on_commit(
            lambda: registration_kobo_import_task.delay(
                registration_data_import_id=str(created_obj_datahub.id),
                import_data_id=str(import_data_obj.id),
                business_area_id=str(business_area.id),
            )
        )

        return RegistrationXlsxImportMutation(registration_data_import=created_obj_hct)


class MergeRegistrationDataImportMutation(BaseValidator, PermissionMutation):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @transaction.atomic(using="default")
    @transaction.atomic(using="registration_datahub")
    @is_authenticated
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
        # TODO: add 'program' arg or None
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, old_obj_hct, obj_hct
        )
        return MergeRegistrationDataImportMutation(obj_hct)


class RefuseRegistrationDataImportMutation(BaseValidator, PermissionMutation):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    def validate_object_status(cls, *args: Any, **kwargs: Any) -> None:
        status = kwargs.get("status")
        if status != RegistrationDataImport.IN_REVIEW:
            logger.error("Only In Review Registration Data Import can be refused")
            raise ValidationError("Only In Review Registration Data Import can be refused")

    @classmethod
    @transaction.atomic(using="default")
    @transaction.atomic(using="registration_datahub")
    @is_authenticated
    def mutate(cls, root: Any, info: Any, id: Optional[str], **kwargs: Any) -> "RefuseRegistrationDataImportMutation":
        decode_id = decode_id_string(id)
        old_obj_hct = RegistrationDataImport.objects.get(id=decode_id)
        obj_hct = RegistrationDataImport.objects.get(id=decode_id)

        check_concurrency_version_in_mutation(kwargs.get("version"), obj_hct)

        cls.has_permission(info, Permissions.RDI_REFUSE_IMPORT, obj_hct.business_area)

        cls.validate(status=obj_hct.status)
        obj_hct.status = RegistrationDataImport.REFUSED_IMPORT
        obj_hct.save()

        imported_individuals_to_remove = ImportedIndividual.objects.filter(registration_data_import=obj_hct.datahub_id)

        remove_elasticsearch_documents_by_matching_ids(
            list(imported_individuals_to_remove.values_list("id", flat=True)),
            get_imported_individual_doc(obj_hct.business_area.slug),
        )
        # TODO: add 'program' arg or None
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, old_obj_hct, obj_hct
        )
        return RefuseRegistrationDataImportMutation(obj_hct)


class UploadImportDataXLSXFileAsync(PermissionMutation):
    import_data = graphene.Field(ImportDataNode)
    errors = graphene.List(XlsxRowErrorNode)

    class Arguments:
        file = Upload(required=True)
        business_area_slug = graphene.String(required=True)

    @classmethod
    @transaction.atomic(using="default")
    @transaction.atomic(using="registration_datahub")
    @is_authenticated
    def mutate(cls, root: Any, info: Any, file: IO, business_area_slug: str) -> "UploadImportDataXLSXFileAsync":
        cls.has_permission(info, Permissions.RDI_IMPORT_DATA, business_area_slug)
        import_data = ImportData.objects.create(
            file=file,
            data_type=ImportData.XLSX,
            status=ImportData.STATUS_PENDING,
            created_by_id=info.context.user.id,
            business_area_slug=business_area_slug,
        )
        transaction.on_commit(partial(validate_xlsx_import_task.delay, import_data.id))
        return UploadImportDataXLSXFileAsync(import_data, [])


class SaveKoboProjectImportDataAsync(PermissionMutation):
    import_data = graphene.Field(KoboImportDataNode)

    class Arguments:
        uid = Upload(required=True)
        business_area_slug = graphene.String(required=True)
        only_active_submissions = graphene.Boolean(required=True)

    @classmethod
    @is_authenticated
    def mutate(
        cls, root: Any, info: Any, uid: "UUID", business_area_slug: str, only_active_submissions: bool
    ) -> "SaveKoboProjectImportDataAsync":
        cls.has_permission(info, Permissions.RDI_IMPORT_DATA, business_area_slug)

        import_data = KoboImportData.objects.create(
            data_type=ImportData.JSON,
            kobo_asset_id=uid,
            only_active_submissions=only_active_submissions,
            status=ImportData.STATUS_PENDING,
            business_area_slug=business_area_slug,
            created_by_id=info.context.user.id,
        )
        pull_kobo_submissions_task.delay(import_data.id)
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
        rdi_obj.delete()
        # TODO: add 'program' arg or None
        log_create(RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, rdi_obj, None)
        return cls(ok=True)


class Mutations(graphene.ObjectType):
    upload_import_data_xlsx_file_async = UploadImportDataXLSXFileAsync.Field()
    delete_registration_data_import = DeleteRegistrationDataImport.Field()
    registration_xlsx_import = RegistrationXlsxImportMutation.Field()
    registration_kobo_import = RegistrationKoboImportMutation.Field()
    save_kobo_import_data_async = SaveKoboProjectImportDataAsync.Field()
    merge_registration_data_import = MergeRegistrationDataImportMutation.Field()
    refuse_registration_data_import = RefuseRegistrationDataImportMutation.Field()
    rerun_dedupe = RegistrationDeduplicationMutation.Field()
