import json

import graphene
from auditlog.models import LogEntry
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_text
from django.utils.functional import Promise
from graphene import String, DateTime, Scalar
from graphene import relay, ConnectionField, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from account.schema import UserObjectType
from core.models import Location, BusinessArea
from core.utils import decode_id_string


class ChoiceObject(graphene.ObjectType):
    name = String()
    value = String()


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


class JSONLazyString(Scalar):
    """
    Allows use of a JSON String for input / output from the GraphQL schema.

    Use of this type is *not recommended* as you lose the benefits of having a defined, static
    schema (one of the key benefits of GraphQL).
    """

    @staticmethod
    def serialize(dt):
        return json.dumps(dt, cls=LazyEncoder)

    @staticmethod
    def parse_literal(node):
        if isinstance(node, String):
            return json.loads(node.value)

    @staticmethod
    def parse_value(value):
        return json.loads(value)


class LogEntryObject(DjangoObjectType):
    timestamp = DateTime()
    changes_display_dict = JSONLazyString()
    actor = UserObjectType()

    class Meta:
        model = LogEntry
        exclude_fields = ("additional_data",)


class LogEntryObjectConnection(Connection):
    class Meta:
        node = LogEntryObject


class ExtendedConnection(graphene.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    edge_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length

    def resolve_edge_count(root, info, **kwargs):
        return len(root.edges)


class LocationNode(DjangoObjectType):
    class Meta:
        model = Location
        exclude_fields = ["geom", "point"]
        filter_fields = ["title"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class BusinessAreaNode(DjangoObjectType):
    class Meta:
        model = BusinessArea
        filter_fields = ["id"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    location = relay.Node.Field(LocationNode)
    all_locations = DjangoFilterConnectionField(LocationNode)
    all_business_areas = DjangoFilterConnectionField(BusinessAreaNode)
    all_log_entries = ConnectionField(
        LogEntryObjectConnection, object_id=graphene.String(required=True),
    )

    def resolve_all_log_entries(self, info, object_id, **kwargs):
        id = decode_id_string(object_id)
        return LogEntry.objects.filter(object_pk=id).all()
