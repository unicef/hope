import json
import operator
import time
from io import StringIO

import graphene
import openpyxl
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import transaction
from graphene_file_upload.scalars import Upload

from core.airflow_api import AirflowApi
from core.kobo.api import KoboAPI
from core.kobo.common import count_population
from core.models import BusinessArea
from core.permissions import is_authenticated
from core.utils import decode_id_string
from core.validators import BaseValidator
from registration_data.models import RegistrationDataImport
from registration_data.schema import RegistrationDataImportNode
from registration_datahub.models import (
    ImportData,
    RegistrationDataImportDatahub,
)
from registration_datahub.schema import (
    ImportDataNode,
    XlsxRowErrorNode,
    KoboErrorNode,
)
from registration_datahub.validators import (
    UploadXLSXValidator,
    KoboProjectImportDataValidator,
)


def create_registration_data_import_objects(
    registration_data_import_data, user
):
    import_data_id = decode_id_string(
        registration_data_import_data.pop("import_data_id")
    )
    import_data_obj = ImportData.objects.get(id=import_data_id)

    business_area = BusinessArea.objects.get(
        slug=registration_data_import_data.pop("business_area_slug")
    )

    created_obj_datahub = RegistrationDataImportDatahub.objects.create(
        import_data=import_data_obj, **registration_data_import_data,
    )
    created_obj_hct = RegistrationDataImport.objects.create(
        status="IMPORTING",
        imported_by=user,
        data_source="XLS",
        number_of_individuals=import_data_obj.number_of_individuals,
        number_of_households=import_data_obj.number_of_households,
        business_area=business_area,
        **registration_data_import_data,
    )

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


class RegistrationXlsxImportMutationInput(graphene.InputObjectType):
    import_data_id = graphene.ID()
    name = graphene.String()
    business_area_slug = graphene.String()


class RegistrationKoboImportMutationInput(graphene.InputObjectType):
    import_data_id = graphene.String()
    name = graphene.String()
    business_area_slug = graphene.String()


class RegistrationXlsxImportMutation(BaseValidator, graphene.Mutation):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        registration_data_import_data = RegistrationXlsxImportMutationInput(
            required=True
        )

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, registration_data_import_data):
        (
            created_obj_datahub,
            created_obj_hct,
            import_data_obj,
            business_area,
        ) = create_registration_data_import_objects(
            registration_data_import_data, info.context.user
        )

        AirflowApi.start_dag(
            dag_id="CreateRegistrationDataImportXLSX",
            context={
                "registration_data_import_id": str(created_obj_datahub.id),
                "import_data_id": str(import_data_obj.id),
                "business_area": str(business_area.id),
            },
        )

        return RegistrationXlsxImportMutation(created_obj_hct)


class RegistrationKoboImportMutation(BaseValidator, graphene.Mutation):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        registration_data_import_data = RegistrationKoboImportMutationInput(
            required=True
        )

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, registration_data_import_data):
        (
            created_obj_datahub,
            created_obj_hct,
            import_data_obj,
            business_area,
        ) = create_registration_data_import_objects(
            registration_data_import_data, info.context.user
        )

        AirflowApi.start_dag(
            dag_id="RegistrationKoboImportOperator",
            context={
                "registration_data_import_id": str(created_obj_datahub.id),
                "import_data_id": str(import_data_obj.id),
                "business_area": str(business_area.id),
            },
        )

        return RegistrationXlsxImportMutation(created_obj_hct)


class MergeRegistrationDataImportMutation(BaseValidator, graphene.Mutation):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        id = graphene.ID(required=True)

    @classmethod
    def validate_object_status(cls, *args, **kwargs):
        status = kwargs.get("status")
        if status != "APPROVED":
            raise ValidationError(
                "Only Approved Registration Data Import "
                "can be merged into Population"
            )

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, id):
        decode_id = decode_id_string(id)
        obj_hct = RegistrationDataImport.objects.get(id=decode_id,)
        cls.validate(status=obj_hct.status)
        AirflowApi.start_dag(
            dag_id="MergeRegistrationImportData",
            context={"registration_data_import_id": decode_id,},
        )
        obj_hct.status = "MERGING"
        obj_hct.save()
        return MergeRegistrationDataImportMutation(obj_hct)


class ApproveRegistrationDataImportMutation(BaseValidator, graphene.Mutation):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        id = graphene.ID(required=True)

    @classmethod
    def validate_object_status(cls, *args, **kwargs):
        status = kwargs.get("status")
        if status != "IN_REVIEW":
            raise ValidationError(
                "Only In Review Registration Data Import can be Approved"
            )

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, id):
        decode_id = decode_id_string(id)

        obj = RegistrationDataImport.objects.select_for_update().get(
            id=decode_id,
        )
        cls.validate(status=obj.status)
        obj.status = "APPROVED"
        obj.save()
        return ApproveRegistrationDataImportMutation(obj)


class UnapproveRegistrationDataImportMutation(BaseValidator, graphene.Mutation):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        id = graphene.ID(required=True)

    @classmethod
    def validate_object_status(cls, *args, **kwargs):
        status = kwargs.get("status")
        if status != "APPROVED":
            raise ValidationError(
                "Only Approved Registration Data Import can be Unapproved"
            )

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, id):
        decode_id = decode_id_string(id)

        obj = RegistrationDataImport.objects.select_for_update().get(
            id=decode_id,
        )
        cls.validate(status=obj.status)
        obj.status = "IN_REVIEW"
        obj.save()
        return ApproveRegistrationDataImportMutation(obj)


class UploadImportDataXLSXFile(
    UploadXLSXValidator, graphene.Mutation,
):
    import_data = graphene.Field(ImportDataNode)
    errors = graphene.List(XlsxRowErrorNode)

    class Arguments:
        file = Upload(required=True)
        business_area_slug = graphene.String(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, file, business_area_slug):
        errors = cls.validate(file=file, business_area_slug=business_area_slug)

        if errors:
            errors.sort(key=operator.itemgetter("row_number", "header"))
            return UploadImportDataXLSXFile(None, errors)

        wb = openpyxl.load_workbook(file)

        hh_sheet = wb["Households"]
        ind_sheet = wb["Individuals"]

        number_of_households = 0
        number_of_individuals = 0

        # Could just return max_row if openpyxl won't count empty rows too
        for row in hh_sheet.iter_rows(min_row=3):
            if not any([cell.value for cell in row]):
                continue
            number_of_households += 1

        for row in ind_sheet.iter_rows(min_row=3):

            if not any([cell.value for cell in row]):
                continue
            number_of_individuals += 1

        created = ImportData.objects.create(
            file=file,
            number_of_households=number_of_households,
            number_of_individuals=number_of_individuals,
        )

        return UploadImportDataXLSXFile(created, [])


class SaveKoboProjectImportDataMutation(
    KoboProjectImportDataValidator, graphene.Mutation
):
    import_data = graphene.Field(ImportDataNode)
    errors = graphene.List(KoboErrorNode)

    class Arguments:
        uid = Upload(required=True)
        business_area_slug = graphene.String(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, uid, business_area_slug):
        kobo_api = KoboAPI(business_area_slug)

        submissions = kobo_api.get_project_submissions(uid)

        errors = cls.validate(submissions=submissions)

        if errors:
            errors.sort(key=operator.itemgetter("header"))
            return UploadImportDataXLSXFile(None, errors)

        number_of_households, number_of_individuals = count_population(
            submissions
        )

        import_file_name = f"project-uid-{uid}-{time.time()}.json"
        file = File(StringIO(json.dumps(submissions)), name=import_file_name)

        created = ImportData.objects.create(
            file=file,
            number_of_households=number_of_households,
            number_of_individuals=number_of_individuals,
        )

        return SaveKoboProjectImportDataMutation(created, [])


class DeleteRegistrationDataImport(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        registration_data_import_id = graphene.String(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, **kwargs):
        decoded_id = decode_id_string(kwargs.get("registration_data_import_id"))
        RegistrationDataImport.objects.get(id=decoded_id).delete()
        return cls(ok=True)


class Mutations(graphene.ObjectType):
    upload_import_data_xlsx_file = UploadImportDataXLSXFile.Field()
    delete_registration_data_import = DeleteRegistrationDataImport.Field()
    registration_xlsx_import = RegistrationXlsxImportMutation.Field()
    registration_kobo_import = RegistrationKoboImportMutation.Field()
    save_kobo_import_data = SaveKoboProjectImportDataMutation.Field()
    approve_registration_data_import = (
        ApproveRegistrationDataImportMutation.Field()
    )
    unapprove_registration_data_import = (
        UnapproveRegistrationDataImportMutation.Field()
    )
    merge_registration_data_import = MergeRegistrationDataImportMutation.Field()
