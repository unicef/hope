import graphene
from graphene_django.debug import DjangoDebug

# DO NOT DELETE THIS IMPORT
import hope.apps.core.converters
import hope.apps.core.schema
import hope.apps.household.schema
import hope.apps.program.schema
import hope.apps.steficon.schema


class Query(
    hope.apps.household.schema.Query,
    hope.apps.program.schema.Query,
    hope.apps.core.schema.Query,
    hope.apps.steficon.schema.Query,
    graphene.ObjectType,
):
    debug = graphene.Field(DjangoDebug, name="_debug")


schema = graphene.Schema(query=Query)
