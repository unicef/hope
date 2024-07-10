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
    Type,
    Union,
)

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import F, Q

import graphene
from constance import config
from flags.state import flag_state
from graphene import Boolean, Connection, ConnectionField, DateTime, Int, String, relay
from graphene.types.resolver import attr_resolver, dict_or_attr_resolver, dict_resolver
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hct_mis_api.apps.core.field_attributes.fields_types import FILTERABLE_TYPES, Scope
from hct_mis_api.apps.core.kobo.api import CountryCodeNotProvided, KoboAPI
from hct_mis_api.apps.core.kobo.common import reduce_asset, reduce_assets_list
from hct_mis_api.apps.core.languages import Language, Languages
from hct_mis_api.apps.core.models import (
    BusinessArea,
    DataCollectingType,
    FlexibleAttribute,
    FlexibleAttributeChoice,
    FlexibleAttributeGroup,
    PeriodicFieldData,
)
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.program.models import Program

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)


class ChoiceObject(graphene.ObjectType):
    name = String()
    value = String()


class ChoiceObjectInt(graphene.ObjectType):
    name = String()
    value = Int()


class DataCollectingTypeChoiceObject(graphene.ObjectType):
    name = String()
    value = String()
    description = String()


class PDUSubtypeChoiceObject(graphene.ObjectType):
    value = String()
    display_name = String()


class BusinessAreaNode(DjangoObjectType):
    is_accountability_applicable = graphene.Boolean()

    def resolve_is_accountability_applicable(self, info: Any) -> bool:
        return all([bool(flag_state("ALLOW_ACCOUNTABILITY_MODULE")), self.is_accountability_applicable])

    @classmethod
    def get_queryset(cls, queryset: "QuerySet", info: Any) -> "QuerySet":
        return queryset.filter(is_split=False)

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
        exclude: List = []


class FlexibleAttributeNode(DjangoObjectType):
    choices = graphene.List(FlexibleAttributeChoiceNode)
    associated_with = graphene.Int()

    @staticmethod
    def resolve_choices(parent: FlexibleAttribute, info: Any) -> "QuerySet":
        return parent.choices.all()

    @staticmethod
    def resolve_associated_with(parent: FlexibleAttribute, info: Any) -> str:
        return parent.get_associated_with_display()

    class Meta:
        model = FlexibleAttribute
        fields = [
            "id",
            "type",
            "name",
            "label",
            "hint",
            "required",
            "pdu_data",
        ]


class LabelNode(graphene.ObjectType):
    language = graphene.String()
    label = graphene.String()


def resolve_label(parent: Dict) -> List[Dict[str, Any]]:
    return [{"language": k, "label": v} for k, v in parent.items()]


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


def _custom_dict_or_attr_resolver(attname: str, default_value: Optional[str], root: Any, info: Any, **args: Any) -> Any:
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


class PeriodicFieldDataNode(DjangoObjectType):
    class Meta:
        model = PeriodicFieldData
        fields = (
            "id",
            "subtype",
            "number_of_rounds",
            "rounds_names",
        )


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
    pdu_data = graphene.Field(PeriodicFieldDataNode, required=False)

    @staticmethod
    def resolve_pdu_data(parent: Union[Dict, FlexibleAttribute], info: Any) -> Optional[PeriodicFieldData]:
        if isinstance(parent, FlexibleAttribute):
            return parent.pdu_data
        return None

    def resolve_choices(parent, info: Any) -> List:
        choices = _custom_dict_or_attr_resolver("choices", None, parent, info)

        if callable(choices) and not isinstance(choices, models.Manager):
            choices = choices()
        if isinstance(
            choices,
            Iterable,
        ):
            return sorted(choices, key=lambda elem: elem["label"]["English(EN)"])
        return choices.all()

    def resolve_is_flex_field(self, info: Any) -> bool:
        return isinstance(self, FlexibleAttribute)

    def resolve_labels(parent, info: Any) -> List[Dict[str, Any]]:
        return resolve_label(_custom_dict_or_attr_resolver("label", None, parent, info))

    def resolve_label_en(parent, info: Any) -> Any:
        return _custom_dict_or_attr_resolver("label", None, parent, info)["English(EN)"]

    def resolve_associated_with(self, info: Any) -> Any:
        resolved = _custom_dict_or_attr_resolver("associated_with", None, self, info)
        if resolved == 0:
            return "Household"
        elif resolved == 1:
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

    @staticmethod
    def resolve_label_en(parent: FlexibleAttributeGroup, info: Any) -> Any:
        return _custom_dict_or_attr_resolver("label", None, parent, info)["English(EN)"]

    @staticmethod
    def resolve_flex_attributes(parent: FlexibleAttributeGroup, info: Any) -> "QuerySet":
        return parent.flex_attributes.all()


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


class ObjectConnection(Connection):
    total_count = graphene.Int()

    def resolve_total_count(self, info: Any, **kwargs: Any) -> int:
        return len(self.iterable)

    class Meta:
        abstract = True


class KoboAssetObjectConnection(ObjectConnection):
    class Meta:
        node = KoboAssetObject


class LanguageObject(graphene.ObjectType):
    english = String()
    code = String()


class LanguageObjectConnection(ObjectConnection):
    class Meta:
        node = LanguageObject


def get_fields_attr_generators(
    flex_field: Optional[bool] = None, business_area_slug: Optional[str] = None, program_id: Optional[str] = None
) -> Generator:
    if flex_field is not False:
        yield from FlexibleAttribute.objects.filter(Q(program__isnull=True) | Q(program__id=program_id)).order_by(
            "created_at"
        )
    if flex_field is not True:
        if program_id and Program.objects.get(id=program_id).is_social_worker_program:
            yield from FieldFactory.from_only_scopes([Scope.XLSX_PEOPLE, Scope.TARGETING]).filtered_by_types(
                FILTERABLE_TYPES
            ).apply_business_area(business_area_slug=business_area_slug, program_id=program_id)
        else:
            yield from FieldFactory.from_scope(Scope.TARGETING).filtered_by_types(FILTERABLE_TYPES).apply_business_area(
                business_area_slug=business_area_slug, program_id=program_id
            )


def resolve_asset(business_area_slug: str, uid: str) -> Dict:
    try:
        assets = KoboAPI().get_single_project_data(uid)
    except ObjectDoesNotExist as e:
        logger.exception(f"Provided business area: {business_area_slug}, does not exist.")
        raise GraphQLError("Provided business area does not exist.") from e
    except AttributeError as error:  # pragma: no cover
        logger.exception(error)
        raise GraphQLError(str(error)) from error

    return reduce_asset(assets)


def resolve_assets_list(business_area_slug: str, only_deployed: bool = False) -> List:
    try:
        business_area = BusinessArea.objects.annotate(country_code=F("countries__iso_code3")).get(
            slug=business_area_slug
        )
        assets = KoboAPI().get_all_projects_data(business_area.country_code)
    except ObjectDoesNotExist as e:
        logger.exception(f"Provided business area: {business_area_slug}, does not exist.")
        raise GraphQLError("Provided business area does not exist.") from e
    except AttributeError as error:  # pragma: no cover
        logger.exception(error)
        raise GraphQLError(str(error)) from error
    except CountryCodeNotProvided:
        raise GraphQLError(f"Business area {business_area_slug} does not have a country code.")

    return reduce_assets_list(assets, only_deployed=only_deployed)


class DataCollectingTypeNode(DjangoObjectType):
    class Meta:
        model = DataCollectingType
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        exclude = [
            "compatible_types",
            "limit_to",
        ]


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
        program_id=graphene.String(required=False, description="program id"),
        description="All field datatype meta.",
    )
    all_pdu_fields = graphene.List(
        FieldAttributeNode,
        business_area_slug=graphene.String(required=True, description="The business area slug"),
        program_id=graphene.String(required=True, description="program id"),
        description="All pdu fields.",
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
    all_languages = ConnectionField(
        LanguageObjectConnection, code=graphene.String(required=False), description="All available languages"
    )
    data_collecting_type = relay.Node.Field(DataCollectingTypeNode)
    data_collection_type_choices = graphene.List(DataCollectingTypeChoiceObject)
    pdu_subtype_choices = graphene.List(PDUSubtypeChoiceObject)

    def resolve_business_area(parent, info: Any, business_area_slug: str) -> BusinessArea:
        return BusinessArea.objects.get(slug=business_area_slug)

    def resolve_cash_assist_url_prefix(parent, info: Any) -> str:
        return config.CASH_ASSIST_URL_PREFIX

    def resolve_all_pdu_fields(parent, info: Any, business_area_slug: str, program_id: str) -> Dict:
        return FlexibleAttribute.objects.filter(
            program__business_area__slug=business_area_slug,
            program_id=decode_id_string(program_id),
            type=FlexibleAttribute.PDU,
        )

    def resolve_all_fields_attributes(
        parent,
        info: Any,
        flex_field: Optional[bool] = None,
        business_area_slug: Optional[str] = None,
        program_id: Optional[str] = None,
    ) -> List[Any]:
        def is_a_killer_filter(field: Any) -> bool:
            if isinstance(field, FlexibleAttribute):
                name = field.name
                associated_with = field.get_associated_with_display()
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

        program_id = decode_id_string(info.context.headers.get("Program"))
        return sort_by_attr(
            (
                attr
                for attr in get_fields_attr_generators(flex_field, business_area_slug, program_id)
                if not is_a_killer_filter(attr)
            ),
            "label.English(EN)",
        )

    def resolve_kobo_project(self, info: Any, uid: str, business_area_slug: str, **kwargs: Any) -> Dict:
        return resolve_asset(business_area_slug=business_area_slug, uid=uid)

    def resolve_all_kobo_projects(self, info: Any, business_area_slug: str, *args: Any, **kwargs: Any) -> List:
        return resolve_assets_list(
            business_area_slug=business_area_slug,
            only_deployed=kwargs.get("only_deployed", False),
        )

    def resolve_all_groups_with_fields(self, info: Any, **kwargs: Any) -> "QuerySet[FlexibleAttributeGroup]":
        return FlexibleAttributeGroup.objects.distinct().filter(flex_attributes__isnull=False)

    def resolve_all_languages(self, info: Any, code: str, **kwargs: Any) -> List[Language]:
        return Languages.filter_by_code(code)

    def resolve_data_collection_type_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        data_collecting_types = (
            DataCollectingType.objects.filter(
                Q(Q(limit_to__slug=info.context.headers.get("Business-Area").lower()) | Q(limit_to__isnull=True)),
                active=True,
                deprecated=False,
            )
            .exclude(code__iexact="unknown")
            .only("code", "label", "description")
            .values("code", "label", "description")
        )
        result = []
        for data_collection_type in data_collecting_types:
            result.append(
                {
                    "name": data_collection_type["label"],
                    "value": data_collection_type["code"],
                    "description": data_collection_type["description"],
                }
            )
        return result

    def resolve_pdu_subtype_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return [{"value": choice[0], "display_name": choice[1]} for choice in PeriodicFieldData.TYPE_CHOICES]


class PeriodicFieldNode(DjangoObjectType):
    class Meta:
        model = FlexibleAttribute
        fields = ["name", "label", "pdu_data"]
        interfaces = (relay.Node,)
