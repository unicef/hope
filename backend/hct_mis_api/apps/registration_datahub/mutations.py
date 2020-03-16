import graphene
import openpyxl
from graphene_file_upload.scalars import Upload

from core.models import FlexibleAttribute
from core.permissions import is_authenticated
from core.utils import decode_id_string
from core.validators import CommonValidator
from registration_data.models import RegistrationDataImport
from registration_data.schema import RegistrationDataImportNode
from registration_datahub.models import (
    ImportData,
    RegistrationDataImportDatahub,
)
from registration_datahub.schema import ImportDataNode


class CreateRegistrationDataImportExcelInput(graphene.InputObjectType):
    import_data_id = graphene.ID()
    name = graphene.String()


class CreateRegistrationDataImport(CommonValidator, graphene.Mutation):
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


class UploadImportDataXLSXFile(
    CommonValidator, graphene.Mutation,
):
    import_data = graphene.Field(ImportDataNode)

    class Arguments:
        file = Upload(required=True)

    def validate_file_with_template(self, *args, **kwargs):
        xlsx_file = kwargs.get("file")
        flex_attr_names = FlexibleAttribute.objects.values("name")
        # still don't know which core fields we will have

        core_fields = {
            "individuals": (),
            "households": (),
        }

        wb = openpyxl.load_workbook(xlsx_file)

        for name, fields in core_fields.items():
            sheet = wb[name.capitalize()]
            first_row = sheet[1]

            expected_column_names = core_fields[name] + flex_attr_names
            column_names = [cell.value for cell in first_row]

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, file):
        # cls.validate(file=file)
        created = ImportData.objects.create(
            xlsx_file=file, number_of_households=0, number_of_individuals=0,
        )

        return UploadImportDataXLSXFile(created)


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
