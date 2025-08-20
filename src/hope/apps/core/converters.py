import json
from typing import Any

import graphene
from concurrency.fields import IntegerVersionField
from django.forms import MultipleChoiceField
from graphene_django.converter import convert_django_field
from graphene_django.forms.converter import convert_form_field

from hope.apps.core.scalars import BigInt


class GeoJSON(graphene.Scalar):
    @classmethod
    def serialize(cls, value: Any) -> dict:
        return json.loads(value.geojson)


@convert_form_field.register(MultipleChoiceField)
def convert_form_field_to_string_list(field: graphene.Field) -> graphene.List:
    return graphene.List(graphene.String, description=field.help_text, required=field.required)


@convert_django_field.register(IntegerVersionField)
def convert_field_to_int(field: graphene.List, registry: Any | None = None) -> graphene.Field:
    return graphene.Field(BigInt, description=field.help_text, required=not field.null)
