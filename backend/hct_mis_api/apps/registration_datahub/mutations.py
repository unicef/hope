import operator
from functools import reduce

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
    def merge_household(
        cls, imported_household, household_values, registration_obj
    ):
        imported_individuals_as_values = imported_household.individuals.values(
            "id",
            "photo",
            "full_name",
            "given_name",
            "middle_name",
            "family_name",
            "relationship",
            "role",
            "sex",
            "birth_date",
            "estimated_birth_date",
            "marital_status",
            "phone_no",
            "phone_no_alternative",
            "disability",
            "flex_fields",
        )

        def id_reducer(old, new):
            old[new.id] = new
            return old

        imported_individuals_as_values_id_dict = reduce(
            id_reducer, imported_household.individuals.all(), {}
        )
        individuals_to_add = []
        del household_values["id"]
        household = Household(**{**household_values})
        household.registration_data_import = registration_obj
        for individual_values in imported_individuals_as_values:
            imported_individual = imported_individuals_as_values_id_dict[
                individual_values.get("id")
            ]
            individual = cls.merge_individual(
                imported_individual,
                individual_values,
                household,
                registration_obj,
            )
            if individual_values["relationship"] == "HEAD":
                household.head_of_household = individual
            individuals_to_add.append(individual)
        return household, individuals_to_add

    @classmethod
    def merge_individual(
        cls, imported_individual, individual_values, household, registration_obj
    ):
        del individual_values["id"]
        individual = Individual(**{**individual_values})
        individual.household = household
        individual.registration_data_import = registration_obj
        return individual

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, id):
        decode_id = decode_id_string(id)

        with transaction.atomic():
            print(
                "**********************************************************************"
            )
            obj_hub = RegistrationDataImportDatahub.objects.get(
                hct_id=decode_id,
            )

            obj_hct = RegistrationDataImport.objects.get(id=decode_id,)
            cls.validate(status=obj_hct.status)

            # move individuals and households to hct db
            imported_households = ImportedHousehold.objects.filter(
                registration_data_import=obj_hub,
            )

            def id_reducer(old, new):
                old[new.id] = new
                return old

            imported_households_id_dict = reduce(
                id_reducer, imported_households, {}
            )
            imported_households.all()
            imported_individuals = ImportedIndividual.objects.filter(
                registration_data_import=obj_hub,
            )

            imported_households_as_values = imported_households.values(
                "id",
                "consent",
                "residence_status",
                "country_origin",
                "size",
                "address",
                "country",
                "female_age_group_0_5_count",
                "female_age_group_6_11_count",
                "female_age_group_12_17_count",
                "female_adults_count",
                "pregnant_count",
                "male_age_group_0_5_count",
                "male_age_group_6_11_count",
                "male_age_group_12_17_count",
                "male_adults_count",
                "female_age_group_0_5_disabled_count",
                "female_age_group_6_11_disabled_count",
                "female_age_group_12_17_disabled_count",
                "female_adults_disabled_count",
                "male_age_group_0_5_disabled_count",
                "male_age_group_6_11_disabled_count",
                "male_age_group_12_17_disabled_count",
                "male_adults_disabled_count",
                "registration_date",
                "flex_fields",
            )
            households_to_add = []
            individuals_to_add = []
            for hh_values in imported_households_as_values:
                imported_household = imported_households_id_dict[
                    hh_values.get("id")
                ]
                (household, hh_individuals_to_add) = cls.merge_household(
                    imported_household, hh_values, obj_hct
                )
                households_to_add.append(household)
                individuals_to_add.extend(hh_individuals_to_add)
            Individual.objects.bulk_create(individuals_to_add)
            Household.objects.bulk_create(households_to_add)

            # TODO: update household head and representative

            # cleanup datahub
            # imported_households.delete()
            # imported_individuals.delete()

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
