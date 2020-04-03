import json
from collections import Iterable

import graphene
from auditlog.models import LogEntry
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.utils.encoding import force_text
from django.utils.functional import Promise
from graphene import (
    String,
    DateTime,
    Scalar,
    relay,
    ConnectionField,
    Connection,
)
from graphene.types.resolver import dict_or_attr_resolver
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from account.schema import UserObjectType
from core.core_fields_attributes import CORE_FIELDS_ATTRIBUTES
from core.extended_connection import ExtendedConnection
from core.models import (
    Location,
    BusinessArea,
    FlexibleAttribute,
    FlexibleAttributeChoice,
)
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
        exclude_fields = [
            "history",
        ]


class FlexibleAttributeNode(DjangoObjectType):
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


class LabelNode(graphene.ObjectType):
    language = graphene.String()
    label = graphene.String()


def resolve_label(parrent):
    labels = []
    for k, v in parrent.items():
        labels.append({"language": k, "label": v})
    return labels


class CoreFieldChoiceObject(graphene.ObjectType):
    labels = graphene.List(LabelNode)
    label_en = String()
    value = String()
    admin = String()
    list_name = String()

    def resolve_label_en(parrent, info):
        return dict_or_attr_resolver("label", None, parrent, info)[
            "English(EN)"
        ]

    def resolve_value(parrent, info):
        if isinstance(parrent, FlexibleAttributeChoice):
            return parrent.name
        return dict_or_attr_resolver("value", None, parrent, info)

    def resolve_labels(parrent, info):
        return resolve_label(
            dict_or_attr_resolver("label", None, parrent, info)
        )


class FieldAttributeNode(graphene.ObjectType):
    id = graphene.String()
    type = graphene.String()
    name = graphene.String()
    labels = graphene.List(LabelNode)
    label_en = String()
    hint = graphene.String()
    required = graphene.Boolean()
    choices = graphene.List(CoreFieldChoiceObject)
    associated_with = graphene.String()
    is_flex_field = graphene.Boolean()

    def resolve_choices(parrent, info):
        if isinstance(
            dict_or_attr_resolver("choices", None, parrent, info), Iterable
        ):
            return parrent["choices"]
        return parrent.choices.all()

    def resolve_is_flex_field(self, info):
        if isinstance(self, FlexibleAttribute):
            return True
        return False

    def resolve_labels(parrent, info):
        return resolve_label(
            dict_or_attr_resolver("label", None, parrent, info)
        )

    def resolve_label_en(parrent, info):
        return dict_or_attr_resolver("label", None, parrent, info)[
            "English(EN)"
        ]


def get_fields_attr_generators(flex_field):
    if flex_field != False:
        for attr in FlexibleAttribute.objects.all():
            yield attr
    if flex_field != True:
        for attr in CORE_FIELDS_ATTRIBUTES:
            yield attr


class Query(graphene.ObjectType):
    location = relay.Node.Field(LocationNode)
    all_locations = DjangoFilterConnectionField(LocationNode)
    all_business_areas = DjangoFilterConnectionField(BusinessAreaNode)
    all_log_entries = ConnectionField(
        LogEntryObjectConnection, object_id=graphene.String(required=True),
    )
    all_fields_attributes = graphene.List(
        FieldAttributeNode,
        flex_field=graphene.Boolean(),
        description="All field datatype meta.",
    )

    def resolve_all_log_entries(self, info, object_id, **kwargs):
        id = decode_id_string(object_id)
        return LogEntry.objects.filter(~Q(action=0), object_pk=id).all()

    def resolve_all_fields_attributes(parrent, info, flex_field=None):
        return get_fields_attr_generators(flex_field)
