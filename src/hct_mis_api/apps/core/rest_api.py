import logging
from typing import TYPE_CHECKING, Any, Callable

from django.core.cache import cache

from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from hct_mis_api.apps.core.models import FlexibleAttribute, FlexibleAttributeChoice
from hct_mis_api.apps.core.schema import get_fields_attr_generators, sort_by_attr

if TYPE_CHECKING:
    from rest_framework.request import Request


logger = logging.getLogger(__name__)


def attr_resolver(attname: str, default_value: Any, obj: Any) -> Any:
    return getattr(obj, attname, default_value)


def dict_resolver(attname: str, default_value: Any, obj: Any) -> Any | None:
    return obj.get(attname, default_value)


def _custom_dict_or_attr_resolver(attname: str, default_value: Any, obj: Any) -> Any | None:
    resolver: Callable | None = attr_resolver
    if isinstance(obj, dict):
        resolver = dict_resolver
    if not resolver:
        return None
    return resolver(attname, default_value, obj)


def resolve_label(obj: Any) -> list[dict[str, Any]]:
    return [{"language": k, "label": v} for k, v in obj.items()]


class CoreFieldChoiceSerializer(serializers.Serializer):
    labels = serializers.SerializerMethodField()
    label_en = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    admin = serializers.CharField(default=None)
    list_name = serializers.CharField(default=None)

    def get_labels(self, obj: Any) -> Any:
        return resolve_label(_custom_dict_or_attr_resolver("label", None, obj))

    def get_value(self, obj: Any) -> str | Any | None:
        if isinstance(obj, FlexibleAttributeChoice):
            return obj.name
        return _custom_dict_or_attr_resolver("value", None, obj)

    def get_label_en(self, obj: Any) -> str | None:
        if data := _custom_dict_or_attr_resolver("label", None, obj):
            return data["English(EN)"]
        return None


class FieldAttributeSerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()
    name = serializers.CharField()
    labels = serializers.SerializerMethodField()
    label_en = serializers.SerializerMethodField()
    hint = serializers.CharField()
    choices = CoreFieldChoiceSerializer(many=True)
    associated_with = serializers.SerializerMethodField()
    is_flex_field = serializers.SerializerMethodField()

    def get_labels(self, obj: Any) -> list[dict[str, Any]]:
        return resolve_label(_custom_dict_or_attr_resolver("label", None, obj))

    def get_label_en(self, obj: Any) -> str | None:
        if data := _custom_dict_or_attr_resolver("label", None, obj):
            return data["English(EN)"]
        return None

    def get_is_flex_field(self, obj: Any) -> bool:
        return bool(isinstance(obj, FlexibleAttribute))

    def get_associated_with(self, obj: Any) -> Any | None:
        resolved = _custom_dict_or_attr_resolver("associated_with", None, obj)
        if resolved == 0:
            return "Household"
        if resolved == 1:
            return "Individual"
        return resolved


@api_view()
def all_fields_attributes(request: "Request") -> "Response":
    business_area_slug = request.data.get("business_area_slug")

    records = cache.get(business_area_slug)
    if records:
        return Response(records)

    records = sort_by_attr(get_fields_attr_generators(True, business_area_slug), "label.English(EN)")
    serializer = FieldAttributeSerializer(records, many=True)
    data = serializer.data

    cache.set(business_area_slug, data)
    return Response(data)
