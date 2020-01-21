import graphene
from graphene_django.debug import DjangoDebug

import core.mutations
import core.schema
import household.mutations
import household.schema
import payment.schema
import program.mutations
import program.schema
import targeting.schema


class Query(
    household.schema.Query,
    targeting.schema.Query,
    program.schema.Query,
    core.schema.Query,
    payment.schema.Query,
    graphene.ObjectType,
):
    debug = graphene.Field(DjangoDebug, name="_debug")


class Mutations(
    core.mutations.Mutations,
    household.mutations.Mutations,
    program.mutations.Mutations,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutations)
