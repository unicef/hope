import json

import graphene
from account.schema import UserObjectType
from auditlog.models import LogEntry
from core.extended_connection import ExtendedConnection
from core.models import (
    Location,
    BusinessArea,
    CoreAttribute,
    FlexibleAttribute,
    FlexibleAttributeChoice,
)
from core.utils import decode_id_string
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.utils.encoding import force_text
from django.utils.functional import Promise
from graphene import String, DateTime, Scalar
from graphene import relay, ConnectionField, Connection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from household.models import Household


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
    total_count = graphene.Int()

    def resolve_total_count(self, info, **kwargs):
        return self.iterable.count()

    class Meta:
        node = LogEntryObject


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


class FlexibleAttributeChoiceNode(DjangoObjectType):
    name = graphene.String()
    value = graphene.String(source="label")

    class Meta:
        model = FlexibleAttributeChoice
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        fields = ["name", "label"]


class FlexFieldNode(DjangoObjectType):
    choices = graphene.List(FlexibleAttributeChoiceNode)
    associated_with = graphene.String()

    def resolve_choices(self, info):
        return self.choices.all()

    def resolve_associated_with(self, info):
        return str(
            FlexibleAttribute.ASSOCIATED_WITH_CHOICES[self.associated_with][1]
        )

    class Meta:
        model = FlexibleAttribute
        fields = [
            "id",
            "type",
            "name",
            "label",
            "hint",
            "required",
        ]


class CoreFieldNode(graphene.ObjectType):
    id = graphene.String()
    type = graphene.String()
    name = graphene.String()
    label = graphene.JSONString()
    hint = graphene.String()
    required = graphene.Boolean()
    choices = graphene.List(ChoiceObject)
    associated_with = graphene.String()


class Query(graphene.ObjectType):
    location = relay.Node.Field(LocationNode)
    all_locations = DjangoFilterConnectionField(LocationNode)
    all_business_areas = DjangoFilterConnectionField(BusinessAreaNode)
    all_log_entries = ConnectionField(
        LogEntryObjectConnection, object_id=graphene.String(required=True),
    )
    all_core_field_attributes = graphene.List(
        CoreFieldNode, description="core field datatype meta.",
    )
    all_flex_field_attributes = graphene.List(
        FlexFieldNode, description="flex field datatype meta."
    )

    def resolve_all_log_entries(self, info, object_id, **kwargs):
        id = decode_id_string(object_id)
        return LogEntry.objects.filter(~Q(action=0), object_pk=id).all()

    def resolve_all_core_field_attributes(self, info):
        return CoreAttribute.get_core_fields(Household)

    def resolve_all_flex_field_attributes(self, info):
        return FlexibleAttribute.objects.all()
