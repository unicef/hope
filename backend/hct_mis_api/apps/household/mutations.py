import graphene
from django.core.files.images import ImageFile
from django.db import transaction

from account.models import User
from core.models import Location
from core.permissions import is_authenticated
from core.utils import decode_id_string
from household.models import Household, RegistrationDataImport
from household.schema import HouseholdNode, RegistrationDataImportNode
from household.validators import HouseholdValidator


class CreateHouseholdInput(graphene.InputObjectType):
    household_ca_id = graphene.String(required=True)
    residence_status = graphene.String(required=True)
    nationality = graphene.String(required=True)
    family_size = graphene.Int()
    address = graphene.String()
    location_id = graphene.String(required=True)
    registration_data_import_id = graphene.String(required=True)


class UpdateHouseholdInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    household_ca_id = graphene.String()
    consent = graphene.String()
    residence_status = graphene.String()
    nationality = graphene.String()
    family_size = graphene.Int()
    address = graphene.String()
    location_id = graphene.String()
    registration_data_import_id = graphene.String()


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


class CreateHousehold(HouseholdValidator, graphene.Mutation):
    household = graphene.Field(HouseholdNode)

    class Arguments:
        household_data = CreateHouseholdInput()

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, household_data):
        location_id = decode_id_string(household_data.pop("location_id", None))
        registration_data_import_id = decode_id_string(
            household_data.pop("registration_data_import_id", None)
        )

        location = Location.objects.get(id=location_id)
        registration_data_import = RegistrationDataImport.objects.get(
            id=registration_data_import_id,
        )

        cls.validate(files=info.context.FILES)

        _, in_memory_files_list = info.context.FILES.popitem()

        in_memory_file = in_memory_files_list.pop()

        household = Household.objects.create(
            **household_data,
            location=location,
            registration_data_import_id=registration_data_import,
            consent=ImageFile(in_memory_file.file, name=in_memory_file.name),
        )

        return CreateHousehold(household)


class UpdateHousehold(HouseholdValidator, graphene.Mutation):
    household = graphene.Field(HouseholdNode)

    class Arguments:
        household_data = UpdateHouseholdInput()

    @classmethod
    @transaction.atomic
    @is_authenticated
    def mutate(cls, root, info, household_data):
        location_id = decode_id_string(household_data.pop("location_id", None))
        registration_data_import_id = decode_id_string(
            household_data.pop("registration_data_import_id", None)
        )
        household_id = decode_id_string(household_data.pop("id", None))

        household = Household.objects.get(id=household_id)

        if location_id:
            household.location = Location.objects.get(id=location_id)

        if registration_data_import_id:
            household.registration_data_import_id = RegistrationDataImport.objects.get(
                id=registration_data_import_id,
            )

        context_files = info.context.FILES

        if context_files:
            cls.validate(files=context_files)

        for attrib, value in household_data.items():
            if hasattr(household, attrib):
                setattr(household, attrib, value)

        if context_files:
            _, in_memory_files_list = context_files.popitem()
            in_memory_file = in_memory_files_list.pop()
            # TODO: add image unlink in future
            household.consent = ImageFile(
                in_memory_file.file, name=in_memory_file.name,
            )

        household.save()

        return UpdateHousehold(household)


class DeleteHousehold(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        household_id = graphene.String(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, **kwargs):
        decoded_id = decode_id_string(kwargs.get("household_id"))
        Household.objects.get(id=decoded_id).delete()
        return cls(ok=True)


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
    create_household = CreateHousehold.Field()
    update_household = UpdateHousehold.Field()
    delete_household = DeleteHousehold.Field()
    create_registration_data_import = CreateRegistrationDataImport.Field()
    update_registration_data_import = UpdateRegistrationDataImport.Field()
    delete_registration_data_import = DeleteRegistrationDataImport.Field()
