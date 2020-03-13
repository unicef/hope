import graphene
import openpyxl
from graphene_file_upload.scalars import Upload

from core.models import FlexibleAttribute
from core.permissions import is_authenticated
from core.utils import decode_id_string
from core.validators import CommonValidator
from registration_data.models import RegistrationDataImport
from registration_datahub.models import ImportData
from registration_datahub.schema import ImportDataNode


class ValidateAndCreateRegistrationDataImportInput(graphene.InputObjectType):
    name = graphene.String()
    status = graphene.String()
    data_source = graphene.String()
    number_of_individuals = graphene.Int()
    number_of_households = graphene.Int()


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
