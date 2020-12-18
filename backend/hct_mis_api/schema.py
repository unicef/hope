import graphene

# DO NOT DELETE THIS IMPORT
import core.converters

from graphene_django.debug import DjangoDebug

import account.schema
import core.schema

import grievance.schema
import grievance.mutations
import household.schema
import payment.mutations
import payment.schema
import program.mutations
import program.schema
import registration_data.schema
import registration_datahub.schema
import registration_datahub.mutations
import registration_datahub.schema
import sanction_list.mutations
import targeting.mutations
import targeting.schema
import steficon.schema
import sanction_list.schema


class Query(
    registration_data.schema.Query,
    registration_datahub.schema.Query,
    account.schema.Query,
    household.schema.Query,
    targeting.schema.Query,
    program.schema.Query,
    core.schema.Query,
    payment.schema.Query,
    steficon.schema.Query,
    grievance.schema.Query,
    sanction_list.schema.Query,
    graphene.ObjectType,
):
    debug = graphene.Field(DjangoDebug, name="_debug")


class Mutations(
    sanction_list.mutations.Mutations,
    registration_datahub.mutations.Mutations,
    program.mutations.Mutations,
    targeting.mutations.Mutations,
    payment.mutations.Mutations,
    grievance.mutations.Mutations,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutations)
