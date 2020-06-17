import json
from collections import Iterable
from operator import itemgetter

import graphene
from auditlog.models import LogEntry
from django.contrib.gis.db.models import GeometryField
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django_filters import FilterSet, CharFilter
from graphene import (
    String,
    DateTime,
    Scalar,
    relay,
    ConnectionField,
    Connection,
    Boolean,
)
from graphene.types.resolver import (
    dict_or_attr_resolver,
    attr_resolver,
    dict_resolver,
)
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from account.schema import UserObjectType
from core.core_fields_attributes import FILTERABLE_CORE_FIELDS_ATTRIBUTES
from core.extended_connection import ExtendedConnection
from core.kobo.api import KoboAPI
from core.kobo.common import reduce_assets_list, reduce_asset
from core.models import (
    AdminArea,
    BusinessArea,
    FlexibleAttribute,
    FlexibleAttributeChoice,
    FlexibleAttributeGroup,
)
from core.utils import decode_id_string, LazyEvalMethodsDict


class AdminAreaFilter(FilterSet):
    business_area = CharFilter(
        field_name="admin_area_type__business_area__slug",
    )

    class Meta:
        model = AdminArea
        fields = {
            "title": ["exact", "icontains"],
            "business_area": ["exact"],
        }


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


class AdminAreaNode(DjangoObjectType):
    class Meta:
        model = AdminArea
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


def resolve_label(parent):
    labels = []
    for k, v in parent.items():
        labels.append({"language": k, "label": v})
    return labels


class CoreFieldChoiceObject(graphene.ObjectType):
    labels = graphene.List(LabelNode)
    label_en = String()
    value = String()
    admin = String()
    list_name = String()

    def resolve_label_en(parent, info):
        return dict_or_attr_resolver("label", None, parent, info)["English(EN)"]

    def resolve_value(parent, info):
        if isinstance(parent, FlexibleAttributeChoice):
            return parent.name
        return dict_or_attr_resolver("value", None, parent, info)

    def resolve_labels(parent, info):
        return resolve_label(dict_or_attr_resolver("label", None, parent, info))


def _custom_dict_or_attr_resolver(attname, default_value, root, info, **args):
    resolver = attr_resolver
    if isinstance(root, (dict, LazyEvalMethodsDict)):
        resolver = dict_resolver
    return resolver(attname, default_value, root, info, **args)


class FieldAttributeNode(graphene.ObjectType):
    class Meta:
        default_resolver = _custom_dict_or_attr_resolver

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

    def resolve_choices(parent, info):
        if isinstance(
            _custom_dict_or_attr_resolver("choices", None, parent, info),
            Iterable,
        ):
            return sorted(parent["choices"], key=itemgetter("value"))
        return parent.choices.order_by("name").all()

    def resolve_is_flex_field(self, info):
        if isinstance(self, FlexibleAttribute):
            return True
        return False

    def resolve_labels(parent, info):
        return resolve_label(
            _custom_dict_or_attr_resolver("label", None, parent, info)
        )

    def resolve_label_en(parent, info):
        return _custom_dict_or_attr_resolver("label", None, parent, info)[
            "English(EN)"
        ]

    def resolve_associated_with(self, info):
        resolved = _custom_dict_or_attr_resolver(
            "associated_with", None, self, info
        )
        if resolved == 0:
            return "Household"
        elif resolved == 1:
            return "Individual"
        else:
            return resolved


class GroupAttributeNode(DjangoObjectType):
    label_en = graphene.String()

    class Meta:
        model = FlexibleAttributeGroup
        fields = [
            "id",
            "name",
            "label",
            "flex_attributes",
            "label_en"
        ]

    def resolve_label_en(self, info):
        return _custom_dict_or_attr_resolver("label", None, self, info)[
            "English(EN)"
        ]


class KoboAssetObject(graphene.ObjectType):
    id = String()
    name = String()
    sector = String()
    country = String()
    asset_type = String()
    date_modified = DateTime()
    deployment_active = Boolean()
    has_deployment = Boolean()
    xls_link = String()


class KoboAssetObjectConnection(Connection):
    total_count = graphene.Int()

    def resolve_total_count(self, info, **kwargs):
        return len(self.iterable)

    class Meta:
        node = KoboAssetObject


class GeoJSON(graphene.Scalar):
    @classmethod
    def serialize(cls, value):
        return json.loads(value.geojson)


@convert_django_field.register(GeometryField)
def convert_field_to_geojson(field, registry=None):
    return graphene.Field(
        GeoJSON, description=field.help_text, required=not field.null
    )


def get_fields_attr_generators(flex_field):
    if flex_field is not False:
        yield from FlexibleAttribute.objects.all()
    if flex_field is not True:
        yield from FILTERABLE_CORE_FIELDS_ATTRIBUTES


def resolve_assets(business_area_slug, uid: str = None, *args, **kwargs):
    if uid is not None:
        method = KoboAPI(business_area_slug).get_single_project_data(uid)
        return_method = reduce_asset
    else:
        method = KoboAPI(business_area_slug).get_all_projects_data()
        return_method = reduce_assets_list
    try:
        assets = method
    except ObjectDoesNotExist:
        raise GraphQLError("Provided business area does not exist.")
    except AttributeError as error:
        raise GraphQLError(str(error))

    return return_method(
        assets, only_deployed=kwargs.get("only_deployed", False)
    )


class Query(graphene.ObjectType):
    admin_area = relay.Node.Field(AdminAreaNode)
    all_admin_areas = DjangoFilterConnectionField(
        AdminAreaNode, filterset_class=AdminAreaFilter
    )
    all_business_areas = DjangoFilterConnectionField(BusinessAreaNode)
    all_log_entries = ConnectionField(
        LogEntryObjectConnection, object_id=graphene.String(required=True),
    )
    all_fields_attributes = graphene.List(
        FieldAttributeNode,
        flex_field=graphene.Boolean(),
        description="All field datatype meta.",
    )
    all_groups_with_fields = graphene.List(
        GroupAttributeNode,
        description="Get all groups that contains flex fields",
    )
    kobo_project = graphene.Field(
        KoboAssetObject,
        uid=graphene.String(required=True),
        business_area_slug=graphene.String(required=True),
        description="Single Kobo project/asset.",
    )
    all_kobo_projects = ConnectionField(
        KoboAssetObjectConnection,
        business_area_slug=graphene.String(required=True),
        only_deployed=graphene.Boolean(required=False),
        description="All Kobo projects/assets.",
    )

    def resolve_all_log_entries(self, info, object_id, **kwargs):
        id = decode_id_string(object_id)
        return LogEntry.objects.filter(~Q(action=0), object_pk=id).all()

    def resolve_all_fields_attributes(parent, info, flex_field=None):
        return get_fields_attr_generators(flex_field)

    def resolve_kobo_project(self, info, uid, business_area_slug, **kwargs):
        return resolve_assets(business_area_slug=business_area_slug, uid=uid)

    def resolve_all_kobo_projects(
        self, info, business_area_slug, *args, **kwargs
    ):
        return resolve_assets(
            business_area_slug=business_area_slug,
            only_deployed=kwargs.get("only_deployed", False),
        )

    def resolve_all_groups_with_fields(self, info, **kwargs):
        return FlexibleAttributeGroup.objects.filter(
            flex_attributes__isnull=False
        )
