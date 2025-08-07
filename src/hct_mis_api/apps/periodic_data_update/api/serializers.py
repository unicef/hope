from typing import Any

from django.shortcuts import get_object_or_404

from rest_framework import serializers

from hct_mis_api.apps.core.models import (
    BusinessArea,
    FlexibleAttribute,
    PeriodicFieldData,
)
from hct_mis_api.apps.periodic_data_update.models import (
    PeriodicDataUpdateXlsxTemplate,
    PeriodicDataUpdateXlsxUpload,
)
from hct_mis_api.apps.program.models import Program


class PeriodicDataUpdateTemplateListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="combined_status_display")
    status = serializers.CharField(source="combined_status")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")
    can_export = serializers.BooleanField()

    class Meta:
        model = PeriodicDataUpdateXlsxTemplate
        fields = (
            "id",
            "number_of_records",
            "created_at",
            "created_by",
            "status",
            "status_display",
            "can_export",
        )


class PeriodicDataUpdateTemplateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicDataUpdateXlsxTemplate
        fields = (
            "id",
            "rounds_data",
            "filters",
        )

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        rounds_data = data.get("rounds_data", [])
        # Check for duplicate field names
        field_names = [item["field"] for item in rounds_data]
        if len(field_names) != len(set(field_names)):
            raise serializers.ValidationError({"rounds_data": "Each Field can only be used once in the template."})
        return data

    def create(self, validated_data: dict[str, Any]) -> PeriodicDataUpdateXlsxTemplate:
        validated_data["created_by"] = self.context["request"].user
        business_area_slug = self.context["request"].parser_context["kwargs"]["business_area_slug"]
        program_slug = self.context["request"].parser_context["kwargs"]["program_slug"]
        business_area = get_object_or_404(BusinessArea, slug=business_area_slug)
        validated_data["business_area"] = business_area
        validated_data["program"] = get_object_or_404(Program, slug=program_slug, business_area=business_area)
        return super().create(validated_data)


class PeriodicDataUpdateTemplateDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicDataUpdateXlsxTemplate
        fields = (
            "id",
            "rounds_data",
        )


class PeriodicDataUpdateUploadListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="combined_status_display")
    status = serializers.CharField(source="combined_status")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")

    class Meta:
        model = PeriodicDataUpdateXlsxUpload
        fields = (
            "id",
            "template",
            "created_at",
            "created_by",
            "status",
            "status_display",
        )


class PeriodicDataUpdateUploadDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="combined_status_display")
    status = serializers.CharField(source="combined_status")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")
    errors_info = serializers.JSONField(source="errors")

    class Meta:
        model = PeriodicDataUpdateXlsxUpload
        fields = (
            "id",
            "template",
            "created_at",
            "created_by",
            "status",
            "status_display",
            "errors_info",
        )


class PeriodicDataUpdateUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicDataUpdateXlsxUpload
        fields = ("file",)


class PeriodicFieldDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicFieldData
        fields = ("subtype", "number_of_rounds", "rounds_names")


class PeriodicFieldSerializer(serializers.ModelSerializer):
    pdu_data = PeriodicFieldDataSerializer()
    label = serializers.SerializerMethodField()  # type: ignore

    class Meta:
        model = FlexibleAttribute
        fields = (
            "id",
            "name",
            "label",
            "pdu_data",
        )

    def get_label(self, obj: FlexibleAttribute) -> str:
        return getattr(obj, "label", {}).get("English(EN)", "")
