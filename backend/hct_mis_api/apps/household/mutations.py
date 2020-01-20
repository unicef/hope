import graphene
from django.core.files.images import ImageFile

from core.models import Location
from core.permissions import is_authenticated
from core.utils import decode_id_string
from household.models import Household, RegistrationDataImport
from household.schema import HouseholdNode
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


class CreateHousehold(HouseholdValidator, graphene.Mutation):
    household = graphene.Field(HouseholdNode)

    class Arguments:
        household_data = CreateHouseholdInput()

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, household_data):
        location_id = decode_id_string(household_data.pop('location_id', None))
        registration_data_import_id = decode_id_string(
            household_data.pop('registration_data_import_id', None)
        )

        location = Location.objects.get(id=location_id)
        registration_data_import = RegistrationDataImport.objects.get(
            id=registration_data_import_id,
        )

        cls.validate(files=info.context.FILES)

        name, image = tuple(*info.context.FILES.items())
        import ipdb; ipdb.set_trace()
        household = Household.objects.create(
            **household_data,
            location=location,
            registration_data_import_id=registration_data_import,
            consent=ImageFile(image, name=name),
        )

        return CreateHousehold(household)


class Mutations(graphene.ObjectType):
    create_household = CreateHousehold.Field()
