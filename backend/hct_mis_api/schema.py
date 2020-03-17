import graphene
from graphene_django.debug import DjangoDebug

import account.schema
import core.schema
import household.schema
import payment.schema
import program.mutations
import program.schema
import registration_data.schema
import registration_datahub.schema
import registration_datahub.mutations
import targeting.schema
import targeting.mutations


class Query(
    registration_data.schema.Query,
    registration_datahub.schema.Query,
    account.schema.Query,
    household.schema.Query,
    targeting.schema.Query,
    program.schema.Query,
    core.schema.Query,
    payment.schema.Query,
    graphene.ObjectType,
):
    debug = graphene.Field(DjangoDebug, name="_debug")


class Mutations(
    registration_datahub.mutations.Mutations,
    program.mutations.Mutations,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutations)
