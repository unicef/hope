import graphene
from graphene_django.debug import DjangoDebug

import account.schema
import core.schema
import program.schema
import program.mutations
import payment.schema


class Query(
    account.schema.Query,
    program.schema.Query,
    core.schema.Query,
    payment.schema.Query,
    graphene.ObjectType
):
    debug = graphene.Field(DjangoDebug, name="_debug")


class Mutations(program.mutations.Mutations, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutations)
