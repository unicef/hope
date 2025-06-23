from typing import Any, Callable, Dict, List, Optional, Union

from rest_framework import serializers

from hct_mis_api.apps.core.models import (
    BusinessArea,
    DataCollectingType,
    FlexibleAttribute,
    FlexibleAttributeChoice,
    PeriodicFieldData,
)


class BusinessAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessArea
        fields = (
            "id",
            "name",
            "code",
            "long_name",
            "slug",
            "parent",
            "is_split",
            "active",
            "screen_beneficiary",
            "is_accountability_applicable",
        )


class DataCollectingTypeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="get_type_display")

    class Meta:
        model = DataCollectingType
        fields = (
            "id",
            "label",
            "code",
            "type",
            "household_filters_available",
            "individual_filters_available",
        )


class ChoiceSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.CharField()


class GetKoboAssetListSerializer(serializers.Serializer):
    only_deployed = serializers.BooleanField(default=False)


class KoboAssetObjectSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    sector = serializers.CharField()
    country = serializers.CharField()
    asset_type = serializers.CharField()
    date_modified = serializers.DateTimeField()
    deployment_active = serializers.BooleanField()
    has_deployment = serializers.BooleanField()
    xls_link = serializers.CharField()


def attr_resolver(attname: str, default_value: Any, obj: Any) -> Any:
    return getattr(obj, attname, default_value)


def dict_resolver(attname: str, default_value: Any, obj: Any) -> Optional[Any]:
    return obj.get(attname, default_value)


def _custom_dict_or_attr_resolver(attname: str, default_value: Any, obj: Any) -> Optional[Any]:
    resolver: Optional[Callable] = attr_resolver
    if isinstance(obj, dict):
        resolver = dict_resolver
    if not resolver:
        return None
    return resolver(attname, default_value, obj)


def resolve_label(obj: Any) -> List[Dict[str, Any]]:
    return [{"language": k, "label": v} for k, v in obj.items()]


class CoreFieldChoiceSerializer(serializers.Serializer):
    labels = serializers.SerializerMethodField()
    label_en = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    admin = serializers.CharField(default=None)
    list_name = serializers.CharField(default=None)

    def get_labels(self, obj: Any) -> Any:
        return resolve_label(_custom_dict_or_attr_resolver("label", None, obj))

    def get_value(self, obj: Any) -> Union[str, Optional[Any]]:
        if isinstance(obj, FlexibleAttributeChoice):
            return obj.name
        return _custom_dict_or_attr_resolver("value", None, obj)

    def get_label_en(self, obj: Any) -> Optional[str]:
        if data := _custom_dict_or_attr_resolver("label", None, obj):
            return data["English(EN)"]
        return None


class CollectorAttributeSerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()
    name = serializers.CharField()
    lookup = serializers.CharField()
    label = serializers.DictField()  # type: ignore
    hint = serializers.CharField()
    required = serializers.BooleanField()  # type: ignore
    choices = serializers.ListField(child=serializers.CharField())


class FieldAttributeSimpleSerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()
    name = serializers.CharField()
    label_en = serializers.SerializerMethodField()
    associated_with = serializers.SerializerMethodField()
    is_flex_field = serializers.SerializerMethodField()

    def get_label_en(self, obj: Any) -> Optional[str]:
        if data := _custom_dict_or_attr_resolver("label", None, obj):
            return data["English(EN)"]
        return None

    def get_is_flex_field(self, obj: Any) -> bool:
        if isinstance(obj, FlexibleAttribute):
            return True
        return False

    def get_associated_with(self, obj: Any) -> Optional[str]:
        resolved = _custom_dict_or_attr_resolver("associated_with", None, obj)
        if resolved == 0:
            return "Household"
        elif resolved == 1:
            return "Individual"
        else:
            return resolved


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
    pdu_data = serializers.SerializerMethodField()

    @staticmethod
    def get_pdu_data(obj: Union[Dict, FlexibleAttribute]) -> Optional[PeriodicFieldData]:
        if isinstance(obj, FlexibleAttribute):
            return obj.pdu_data
        return None

    def get_labels(self, obj: Any) -> list[dict[str, Any]]:
        return resolve_label(_custom_dict_or_attr_resolver("label", None, obj))

    def get_label_en(self, obj: Any) -> Optional[str]:
        if data := _custom_dict_or_attr_resolver("label", None, obj):
            return data["English(EN)"]
        return None

    def get_is_flex_field(self, obj: Any) -> bool:
        if isinstance(obj, FlexibleAttribute):
            return True
        return False

    def get_associated_with(self, obj: Any) -> Optional[Any]:
        resolved = _custom_dict_or_attr_resolver("associated_with", None, obj)
        if resolved == 0:
            return "Household"
        elif resolved == 1:
            return "Individual"
        else:
            return resolved
