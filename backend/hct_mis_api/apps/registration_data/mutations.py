import graphene

from account.models import User
from core.permissions import is_authenticated
from core.utils import decode_id_string
from registration_data.models import RegistrationDataImport
from registration_data.schema import RegistrationDataImportNode


class CreateRegistrationDataImportInput(graphene.InputObjectType):
    name = graphene.String()
    status = graphene.String()
    import_date = graphene.DateTime()
    imported_by_id = graphene.String()
    data_source = graphene.String()
    number_of_individuals = graphene.Int()
    number_of_households = graphene.Int()


class UpdateRegistrationDataImportInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    name = graphene.String()
    status = graphene.String()
    import_date = graphene.DateTime()
    imported_by_id = graphene.String()
    data_source = graphene.String()
    number_of_individuals = graphene.Int()
    number_of_households = graphene.Int()


class CreateRegistrationDataImport(graphene.Mutation):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        registration_data_import_data = CreateRegistrationDataImportInput(
            required=True,
        )

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, registration_data_import_data):
        user_id = decode_id_string(
            registration_data_import_data.pop("imported_by_id", None,)
        )

        imported_by = User.objects.get(id=user_id)

        registration_data_import = RegistrationDataImport.objects.create(
            **registration_data_import_data, imported_by=imported_by,
        )

        return CreateRegistrationDataImport(registration_data_import)


class UpdateRegistrationDataImport(graphene.Mutation):
    registration_data_import = graphene.Field(RegistrationDataImportNode)

    class Arguments:
        registration_data_import_data = UpdateRegistrationDataImportInput()

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, registration_data_import_data):
        registration_data_import_id = decode_id_string(
            registration_data_import_data.pop("id", None)
        )

        user_id = decode_id_string(
            registration_data_import_data.pop("imported_by_id", None,)
        )

        registration_data_import = RegistrationDataImport.objects.get(
            id=registration_data_import_id,
        )

        if user_id:
            registration_data_import.imported_by = User.objects.get(id=user_id)

        for attrib, value in registration_data_import_data.items():
            if hasattr(registration_data_import, attrib):
                setattr(registration_data_import, attrib, value)

        return UpdateRegistrationDataImport(registration_data_import)


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
    create_registration_data_import = CreateRegistrationDataImport.Field()
    update_registration_data_import = UpdateRegistrationDataImport.Field()
    delete_registration_data_import = DeleteRegistrationDataImport.Field()
