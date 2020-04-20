import operator

import graphene
import openpyxl
from django.core.exceptions import ValidationError
from django.db import transaction
from graphene_file_upload.scalars import Upload

from core.permissions import is_authenticated
from core.utils import decode_id_string
from core.validators import BaseValidator
from household.models import Household, Individual
from registration_data.models import RegistrationDataImport
from registration_data.schema import RegistrationDataImportNode
from registration_datahub.models import (
    ImportData,
    RegistrationDataImportDatahub,
    ImportedHousehold,
    ImportedIndividual,
)
from registration_datahub.schema import ImportDataNode, XlsxRowErrorNode
from registration_datahub.validators import UploadXLSXValidator


class CreateRegistrationDataImportExcelInput(graphene.InputObjectType):
    import_data_id = graphene.ID()
    name = graphene.String()


class CreateRegistrationDataImport(BaseValidator, graphene.Mutation):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        registration_data_import_data = CreateRegistrationDataImportExcelInput(
            required=True
        )

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, registration_data_import_data):
        import_data_id = decode_id_string(
            registration_data_import_data.pop("import_data_id")
        )
        import_data_obj = ImportData.objects.get(id=import_data_id)

        created_obj_datahub = RegistrationDataImportDatahub.objects.create(
            import_data=import_data_obj, **registration_data_import_data,
        )
        created_obj_hct = RegistrationDataImport.objects.create(
            status="IN_REVIEW",
            imported_by=info.context.user,
            data_source="XLS",
            number_of_individuals=import_data_obj.number_of_individuals,
            number_of_households=import_data_obj.number_of_households,
            **registration_data_import_data,
        )

        created_obj_datahub.hct_id = created_obj_hct.id
        created_obj_datahub.save()

        created_obj_hct.datahub_id = created_obj_datahub.id
        created_obj_hct.save()

        # take file and run AirFlow job to add Households and Individuals

        return CreateRegistrationDataImport(created_obj_hct)


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

        obj_hub = RegistrationDataImportDatahub.objects.select_for_update().get(
            hct_id=decode_id,
        )

        obj_hct = RegistrationDataImport.objects.select_for_update().get(
            id=decode_id,
        )

        cls.validate(status=obj_hct.status)

        with transaction.atomic():
            # move individuals and households to hct db
            imported_households = ImportedHousehold.objects.filter(
                registration_data_import=obj_hub,
            )
            imported_individuals = ImportedIndividual.objects.filter(
                registration_data_import=obj_hub,
            )

            imported_households_as_values = imported_households.values(
                "household_ca_id",
                "consent",
                "residence_status",
                "nationality",
                "family_size",
                "address",
                "location",
                "representative",
                "head_of_household",
                "registration_date",
            )
            imported_individuals_as_values = imported_individuals.values(
                "individual_ca_id",
                "full_name",
                "first_name",
                "middle_name",
                "last_name",
                "dob",
                "sex",
                "estimated_dob",
                "nationality",
                "martial_status",
                "phone_number",
                "phone_number_alternative",
                "identification_type",
                "identification_number",
                "household",
                "work_status",
                "disability",
            )

            households_to_create = (
                Household(
                    **{
                        **hh,
                        "representative": None,
                        "head_of_household": None,
                        # TODO: cannot be empty should we also have Location,
                        #  GatewayType models in registration datahub
                        "location": None,
                    }
                )
                for hh in imported_households_as_values
            )

            Household.objects.bulk_create(households_to_create)

            individuals_to_create = (
                Individual(**ind) for ind in imported_individuals_as_values
            )

            Individual.objects.bulk_create(individuals_to_create)

            # TODO: update household head and representative

            # cleanup datahub
            imported_households.delete()
            imported_individuals.delete()

            obj_hct.status = "MERGED"
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

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, file):
        # TODO: Is it good approach?
        #  consult this with Janek
        errors = cls.validate(file=file)

        if errors:
            errors.sort(key=operator.itemgetter('row_number', 'header'))
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
            xlsx_file=file,
            number_of_households=number_of_households,
            number_of_individuals=number_of_individuals,
        )

        return UploadImportDataXLSXFile(created, [])


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
    create_registration_data_import = CreateRegistrationDataImport.Field()
    approve_registration_data_import = (
        ApproveRegistrationDataImportMutation.Field()
    )
    unapprove_registration_data_import = (
        UnapproveRegistrationDataImportMutation.Field()
    )
    merge_registration_data_import = MergeRegistrationDataImportMutation.Field()
