import graphene
from django.db import transaction

from core.models import Location
from core.permissions import is_authenticated
from core.schema import LocationNode
from core.utils import decode_id_string


class CreateLocationInput(graphene.InputObjectType):
    name = graphene.String()
    country = graphene.String()


class UpdateLocationInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    name = graphene.String()
    country = graphene.String()


class CreateLocation(graphene.Mutation):
    location = graphene.Field(LocationNode)

    class Arguments:
        location_data = CreateLocationInput(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, location_data):
        location = Location.objects.create(**location_data)

        return CreateLocation(location)


class UpdateLocation(graphene.Mutation):
    location = graphene.Field(LocationNode)

    class Arguments:
        location_data = UpdateLocationInput()

    @classmethod
    @transaction.atomic
    @is_authenticated
    def mutate(cls, root, info, location_data):
        location_id = decode_id_string(location_data.pop("id", None))

        location = Location.objects.get(id=location_id)

        for attrib, value in location_data.items():
            if hasattr(location, attrib):
                setattr(location, attrib, value)

        location.save()

        return UpdateLocation(location)


class DeleteLocation(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        location_id = graphene.String(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, **kwargs):
        decoded_id = decode_id_string(kwargs.get("location_id"))
        Location.objects.get(id=decoded_id).delete()
        return cls(ok=True)


class Mutations(graphene.ObjectType):
    create_location = CreateLocation.Field()
    update_location = UpdateLocation.Field()
    delete_location = DeleteLocation.Field()
