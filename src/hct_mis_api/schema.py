import graphene
from graphene_django.debug import DjangoDebug

# DO NOT DELETE THIS IMPORT
import hct_mis_api.apps.core.converters
import hct_mis_api.apps.core.schema
import hct_mis_api.apps.grievance.schema_dashboard
import hct_mis_api.apps.household.schema
import hct_mis_api.apps.program.schema
import hct_mis_api.apps.sanction_list.schema
import hct_mis_api.apps.steficon.schema


class Query(
    hct_mis_api.apps.household.schema.Query,
    hct_mis_api.apps.program.schema.Query,
    hct_mis_api.apps.core.schema.Query,
    hct_mis_api.apps.steficon.schema.Query,
    hct_mis_api.apps.grievance.schema_dashboard.Query,
    hct_mis_api.apps.sanction_list.schema.Query,
    graphene.ObjectType,
):
    debug = graphene.Field(DjangoDebug, name="_debug")


class Mutations(
    hct_mis_api.apps.sanction_list.mutations.Mutations,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutations)
