from django.http import HttpResponse
from graphene_django.settings import graphene_settings

from graphql.utils import schema_printer


def homepage(request):
    return HttpResponse("", status=200)


def schema(request):
    schema = graphene_settings.SCHEMA
    my_schema_str = schema_printer.print_schema(schema)
    return HttpResponse(
        my_schema_str, content_type="application/graphlq", status=200
    )


def trigger_error(request):
    division_by_zero = 1 / 0
