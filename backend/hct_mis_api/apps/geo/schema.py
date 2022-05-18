from django.db.models.functions import Lower

import graphene
from django_filters import CharFilter, FilterSet
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.filters import IntegerFilter
from hct_mis_api.apps.geo.models import Area, AreaType


class AreaFilter(FilterSet):
    business_area = CharFilter(method="business_area_filter")
    level = IntegerFilter(
        field_name="area_type__area_level",
    )

    class Meta:
        model = Area
        fields = {
            "name": ["exact", "istartswith"],
        }

    def business_area_filter(self, qs, name, value):
        return qs.filter(area_type__country__name__iexact=value)


class AreaNode(DjangoObjectType):
    class Meta:
        model = Area
        exclude_fields = ["geom", "point"]
        filter_fields = ["name"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class AreaTypeNode(DjangoObjectType):
    class Meta:
        model = AreaType
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    admin_area = relay.Node.Field(AreaNode)
    all_admin_areas = DjangoFilterConnectionField(AreaNode, filterset_class=AreaFilter)
