import logging

from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers


from hct_mis_api.apps.core.models import (
    FlexibleAttribute,
    FlexibleAttributeChoice
)
from hct_mis_api.apps.core.schema import sort_by_attr, get_fields_attr_generators

logger = logging.getLogger(__name__)


def get_label(obj):
    labels = []
    if isinstance(obj, FlexibleAttribute):
        obj_labels = getattr(obj, "label")
    else:
        obj_labels = obj.get("label")
    for k, v in obj_labels.items():
        labels.append({"language": k, "label": v})
    return labels


class LabelSerializer(serializers.Serializer):
    label = serializers.CharField()
    language = serializers.CharField()


class CoreFieldChoiceSerializer(serializers.Serializer):
    labels = serializers.SerializerMethodField()
    label_en = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    admin = serializers.CharField(default=None)
    list_name = serializers.CharField(default=None)

    def get_labels(self, obj):
        return get_label(obj)

    def get_value(self, obj):
        if isinstance(obj, FlexibleAttributeChoice):
            return getattr(obj, "name", None)
        return obj.get("value", None)

    def get_label_en(self, obj):
        if isinstance(obj, FlexibleAttributeChoice):
            return getattr(obj, "label", None)
        else:
            labels = obj.get("labels")
            if labels:
               obj_list = obj["labels"]
               my_key = [obj for obj in obj_list if obj["name"] == "English(EN)"]
               return my_key[0]["English(EN)"]
            else:
                return obj["label"]["English(EN)"]


class FieldAttributeSerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()
    name = serializers.CharField()
    labels = serializers.SerializerMethodField()
    label_en = serializers.SerializerMethodField()
    hint = serializers.CharField()
    choices = CoreFieldChoiceSerializer(many=True)
    associated_with = serializers.CharField()
    is_flex_field = serializers.SerializerMethodField()

    def get_labels(self, obj):
        return get_label(obj)

    def get_label_en(self, obj):
        if isinstance(obj, FlexibleAttribute):
            labels = get_label(obj)
            my_key = [obj for obj in labels if obj["language"] == "English(EN)"]
            return my_key[0]["label"]
        else:
           obj_list = get_label(obj)
           my_key = [obj for obj in obj_list if obj["language"] == "English(EN)"]
           logger.info(my_key)
           return my_key[0]["label"]

    def get_is_flex_field(self, obj):
        if isinstance(obj, FlexibleAttribute):
            return True
        return False


@api_view()
def all_fields_attributes(request):
    flex_field = request.data.get("flex_field", False)
    business_area_slug = request.data.get("business_area_slug")

    # logger.info("**********")
    # logger.info(cache.keys("*"))
    #
    # records = cache.get(business_area_slug)
    # if records:
    #     return Response(records)

    records = sort_by_attr(get_fields_attr_generators(flex_field, business_area_slug), "label.English(EN)")
    serializer = FieldAttributeSerializer(records, many=True)
    data = serializer.data

    # cache.set(business_area_slug, data)

    return Response(data)
