import graphene
from graphene_django.debug import DjangoDebug

import hct_mis_api.apps.account.schema
import hct_mis_api.apps.accountability.mutations
import hct_mis_api.apps.accountability.schema
import hct_mis_api.apps.activity_log.schema

# DO NOT DELETE THIS IMPORT
import hct_mis_api.apps.core.converters
import hct_mis_api.apps.core.schema
import hct_mis_api.apps.geo.schema
import hct_mis_api.apps.grievance.mutations
import hct_mis_api.apps.grievance.schema
import hct_mis_api.apps.grievance.schema_dashboard
import hct_mis_api.apps.household.schema
import hct_mis_api.apps.payment.mutations
import hct_mis_api.apps.payment.schema
import hct_mis_api.apps.program.mutations
import hct_mis_api.apps.program.schema
import hct_mis_api.apps.registration_data.schema
import hct_mis_api.apps.registration_datahub.mutations
import hct_mis_api.apps.registration_datahub.schema
import hct_mis_api.apps.reporting.mutations
import hct_mis_api.apps.reporting.schema
import hct_mis_api.apps.sanction_list.mutations
import hct_mis_api.apps.sanction_list.schema
import hct_mis_api.apps.steficon.schema
import hct_mis_api.apps.targeting.mutations
import hct_mis_api.apps.targeting.schema


class Query(
    hct_mis_api.apps.registration_data.schema.Query,
    hct_mis_api.apps.registration_datahub.schema.Query,
    hct_mis_api.apps.account.schema.Query,
    hct_mis_api.apps.household.schema.Query,
    hct_mis_api.apps.targeting.schema.Query,
    hct_mis_api.apps.program.schema.Query,
    hct_mis_api.apps.core.schema.Query,
    hct_mis_api.apps.payment.schema.Query,
    hct_mis_api.apps.steficon.schema.Query,
    hct_mis_api.apps.grievance.schema.Query,
    hct_mis_api.apps.grievance.schema_dashboard.Query,
    hct_mis_api.apps.sanction_list.schema.Query,
    hct_mis_api.apps.reporting.schema.Query,
    hct_mis_api.apps.activity_log.schema.Query,
    hct_mis_api.apps.geo.schema.Query,
    hct_mis_api.apps.accountability.schema.Query,
    graphene.ObjectType,
):
    debug = graphene.Field(DjangoDebug, name="_debug")


class Mutations(
    hct_mis_api.apps.sanction_list.mutations.Mutations,
    hct_mis_api.apps.registration_datahub.mutations.Mutations,
    hct_mis_api.apps.program.mutations.Mutations,
    hct_mis_api.apps.targeting.mutations.Mutations,
    hct_mis_api.apps.payment.mutations.Mutations,
    hct_mis_api.apps.grievance.mutations.Mutations,
    hct_mis_api.apps.reporting.mutations.Mutations,
    hct_mis_api.apps.accountability.mutations.Mutations,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutations)
