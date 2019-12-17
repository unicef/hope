import graphene
from graphene_django.debug import DjangoDebug

import core.schema
import program.schema
import payment.schema


class Query(
    program.schema.Query,
    core.schema.Query,
    payment.schema.Query,
    graphene.ObjectType,
):
    debug = graphene.Field(DjangoDebug, name="_debug")


class Mutations(graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)