import json

import graphene
from concurrency.fields import IntegerVersionField
from django.contrib.gis.db.models import GeometryField
from django.forms import MultipleChoiceField
from graphene_django.converter import convert_django_field
from graphene_django.forms.converter import convert_form_field

from hct_mis_api.apps.core.scalars import BigInt


class GeoJSON(graphene.Scalar):
    @classmethod
    def serialize(cls, value):
        return json.loads(value.geojson)


@convert_form_field.register(MultipleChoiceField)
def convert_form_field_to_string_list(field):
    return graphene.List(graphene.String, description=field.help_text, required=field.required)


@convert_django_field.register(GeometryField)
def convert_field_to_geojson(field, registry=None):
    return graphene.Field(GeoJSON, description=field.help_text, required=not field.null)


@convert_django_field.register(IntegerVersionField)
def convert_field_to_int(field, registry=None):
    return graphene.Field(BigInt, description=field.help_text, required=not field.null)
