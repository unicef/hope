import logging
from collections.abc import Iterable
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

import graphene
from constance import config
from graphene import Boolean, Connection, ConnectionField, DateTime, Int, String, relay
from graphene.types.resolver import attr_resolver, dict_or_attr_resolver, dict_resolver
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from hct_mis_api.apps.core.core_fields_attributes import (
    FILTERABLE_TYPES,
    FieldFactory,
    Scope,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.kobo.api import KoboAPI
from hct_mis_api.apps.core.kobo.common import reduce_asset, reduce_assets_list
from hct_mis_api.apps.core.models import (
    BusinessArea,
    FlexibleAttribute,
    FlexibleAttributeChoice,
    FlexibleAttributeGroup,
)

if TYPE_CHECKING:

    from django.db.models.query import QuerySet


logger = logging.getLogger(__name__)


class ChoiceObject(graphene.ObjectType):
    name = String()
    value = String()


class ChoiceObjectInt(graphene.ObjectType):
    name = String()
    value = Int()


class BusinessAreaNode(DjangoObjectType):
    class Meta:
        model = BusinessArea
        filter_fields = ["id", "slug"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class FlexibleAttributeChoiceNode(DjangoObjectType):
    name = graphene.String()
    value = graphene.String(source="label")

    class Meta:
        model = FlexibleAttributeChoice
        interfaces = (relay.Node,)
        connection_class: Type = ExtendedConnection
        exclude_fields: List = []


class FlexibleAttributeNode(DjangoObjectType):
    choices = graphene.List(FlexibleAttributeChoiceNode)
    associated_with = graphene.Int()

    def resolve_choices(self, info: Any) -> "QuerySet":
        return self.choices.all()

    def resolve_associated_with(self, info: Any) -> str:
        associated_number: int = int(self.associated_with)  # type: ignore # FIXME: need some stubs for graphene-django
        choice: Tuple[int, str] = FlexibleAttribute.ASSOCIATED_WITH_CHOICES[associated_number]
        return str(choice[1])

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


def resolve_label(parent: Dict) -> List[Dict[str, Any]]:
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

    def resolve_label_en(parent, info: Any) -> Callable:
        return dict_or_attr_resolver("label", None, parent, info)["English(EN)"]

    def resolve_value(parent, info: Any) -> Union[str, Callable]:
        if isinstance(parent, FlexibleAttributeChoice):
            return parent.name
        return dict_or_attr_resolver("value", None, parent, info)

    def resolve_labels(parent, info: Any) -> List[Dict[str, Any]]:
        return resolve_label(dict_or_attr_resolver("label", None, parent, info))


def _custom_dict_or_attr_resolver(
    attname: str, default_value: Optional[str], root: Any, info: Any, **args: Any
) -> Callable:
    resolver = attr_resolver
    if isinstance(root, dict):
        resolver = dict_resolver
    return resolver(attname, default_value, root, info, **args)


def sort_by_attr(options: Iterable, attrs: str) -> List:
    def key_extractor(el: Any) -> Any:
        for attr in attrs.split("."):
            el = _custom_dict_or_attr_resolver(attr, None, el, None)
        return el

    return list(sorted(options, key=key_extractor))


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

    def resolve_choices(parent, info: Any) -> List:
        choices = _custom_dict_or_attr_resolver("choices", None, parent, info)

        if callable(choices) and not isinstance(choices, models.Manager):
            choices = choices()
        if isinstance(
            choices,
            Iterable,
        ):
            return sorted(choices, key=lambda elem: elem["label"]["English(EN)"])
        return choices.order_by("name").all()

    def resolve_is_flex_field(self, info: Any) -> bool:
        if isinstance(self, FlexibleAttribute):
            return True
        return False

    def resolve_labels(parent, info: Any) -> List[Dict[str, Any]]:
        return resolve_label(_custom_dict_or_attr_resolver("label", None, parent, info))  # type: ignore # FIXME: Argument 1 to "resolve_label" has incompatible type "Callable[..., Any]"; expected "Dict[Any, Any]"

    def resolve_label_en(parent, info: Any) -> Any:
        return _custom_dict_or_attr_resolver("label", None, parent, info)["English(EN)"]  # type: ignore # FIXME: Value of type "Callable[..., Any]" is not indexable

    def resolve_associated_with(self, info: Any) -> Any:
        resolved = _custom_dict_or_attr_resolver("associated_with", None, self, info)
        if resolved == 0:  # type: ignore # FIXME: Non-overlapping equality check (left operand type: "Callable[..., Any]", right operand type: "Literal[0]")
            return "Household"
        elif resolved == 1:  # type: ignore # FIXME: Non-overlapping equality check (left operand type: "Callable[..., Any]", right operand type: "Literal[1]")
            return "Individual"
        else:
            return resolved


class GroupAttributeNode(DjangoObjectType):
    label_en = graphene.String()
    flex_attributes = graphene.List(
        FieldAttributeNode,
        flex_field=graphene.Boolean(),
        description="All field datatype meta.",
    )

    class Meta:
        model = FlexibleAttributeGroup
        fields = ["id", "name", "label", "flex_attributes", "label_en"]

    def resolve_label_en(self, info: Any) -> Any:
        return _custom_dict_or_attr_resolver("label", None, self, info)["English(EN)"]  # type: ignore # FIXME: Value of type "Callable[..., Any]" is not indexable

    def resolve_flex_attributes(self, info: Any) -> "QuerySet":
        return self.flex_attributes.all()


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

    def resolve_total_count(self, info: Any, **kwargs: Any) -> int:
        return len(self.iterable)

    class Meta:
        node = KoboAssetObject


def get_fields_attr_generators(flex_field: bool, business_area_slug: Optional[str] = None) -> Generator:
    if flex_field is not False:
        yield from FlexibleAttribute.objects.order_by("created_at")
    if flex_field is not True:
        yield from FieldFactory.from_scope(Scope.TARGETING).filtered_by_types(FILTERABLE_TYPES).apply_business_area(
            business_area_slug  # type: ignore # FIXME: Argument 1 to "apply_business_area" of "FieldFactory" has incompatible type "Optional[str]"; expected "str"
        )


def resolve_assets(business_area_slug: str, uid: Optional[str] = None, *args: Any, **kwargs: Any) -> Tuple:
    method: Optional[Union[List[Any], Dict[Any, Any]]]
    return_method: Callable
    method, return_method = (
        (  # type: ignore # FIXME: Incompatible types in assignment (expression has type "function", variable has type "Callable[..., Any]")
            KoboAPI(business_area_slug).get_single_project_data(uid),
            reduce_asset,
        )
        if uid is not None
        else (
            KoboAPI(business_area_slug).get_all_projects_data(),
            reduce_assets_list,
        )
    )
    try:
        assets = method
    except ObjectDoesNotExist:
        logger.exception(f"Provided business area: {business_area_slug}, does not exist.")
        raise GraphQLError("Provided business area does not exist.")
    except AttributeError as error:
        logger.exception(error)
        raise GraphQLError(str(error))

    return return_method(assets, **{"only_deployed": kwargs.get("only_deployed", False)})


class Query(graphene.ObjectType):
    business_area = graphene.Field(
        BusinessAreaNode,
        business_area_slug=graphene.String(required=True, description="The business area slug"),
        description="Single business area",
    )
    all_business_areas = DjangoFilterConnectionField(BusinessAreaNode)
    all_fields_attributes = graphene.List(
        FieldAttributeNode,
        flex_field=graphene.Boolean(),
        business_area_slug=graphene.String(required=False, description="The business area slug"),
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
    cash_assist_url_prefix = graphene.String()

    def resolve_business_area(parent, info: Any, business_area_slug: str) -> BusinessArea:
        return BusinessArea.objects.get(slug=business_area_slug)

    def resolve_all_business_areas(parent, info: Any) -> "QuerySet[BusinessArea]":
        return BusinessArea.objects.filter(is_split=False)

    def resolve_cash_assist_url_prefix(parent, info: Any) -> str:
        return config.CASH_ASSIST_URL_PREFIX

    def resolve_all_fields_attributes(
        parent, info: Any, flex_field: Optional[bool] = None, business_area_slug: Optional[str] = None
    ) -> List[Any]:
        def is_a_killer_filter(field: Any) -> bool:
            if isinstance(field, FlexibleAttribute):
                name = field.name
                associated_with = FlexibleAttribute.ASSOCIATED_WITH_CHOICES[field.associated_with][1]
            else:
                name = field["name"]
                associated_with = field["associated_with"]

            return name in {
                "Household": ["address", "deviceid"],
                "Individual": [
                    "full_name",
                    "family_name",
                    "given_name",
                    "middle_name",
                    "phone_no",
                    "phone_no_alternative",
                    "electoral_card_no",
                    "drivers_license_no",
                    "national_passport",
                    "national_id_no",
                ],
            }.get(associated_with, [])

        return sort_by_attr(
            (
                attr
                for attr in get_fields_attr_generators(flex_field, business_area_slug)  # type: ignore # FIXME: Argument 1 to "get_fields_attr_generators" has incompatible type "Optional[bool]"; expected "bool"
                if not is_a_killer_filter(attr)
            ),
            "label.English(EN)",
        )

    def resolve_kobo_project(self, info: Any, uid: str, business_area_slug: str, **kwargs: Any) -> Tuple:
        return resolve_assets(business_area_slug=business_area_slug, uid=uid)

    def resolve_all_kobo_projects(self, info: Any, business_area_slug: str, *args: Any, **kwargs: Any) -> Tuple:
        return resolve_assets(
            business_area_slug=business_area_slug,
            only_deployed=kwargs.get("only_deployed", False),
        )

    def resolve_all_groups_with_fields(self, info: Any, **kwargs: Any) -> "QuerySet[FlexibleAttributeGroup]":
        return FlexibleAttributeGroup.objects.distinct().filter(flex_attributes__isnull=False)
