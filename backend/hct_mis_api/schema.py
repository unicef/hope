import graphene
from django.forms import MultipleChoiceField
from graphene_django.debug import DjangoDebug
from graphene_django.forms.converter import convert_form_field

import account.schema
import core.schema
import graphene

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


# proper multi choice conversion
@convert_form_field.register(MultipleChoiceField)
def convert_form_field_to_string_list(field):
    return graphene.List(graphene.String, description=field.help_text, required=field.required)


class Query(
    registration_data.schema.Query,
    registration_datahub.schema.Query,
    account.schema.Query,
    household.schema.Query,
    targeting.schema.Query,
    program.schema.Query,
    core.schema.Query,
    payment.schema.Query,
    grievance.schema.Query,
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
