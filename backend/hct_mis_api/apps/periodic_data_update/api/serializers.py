from rest_framework import serializers

from hct_mis_api.apps.periodic_data_update.models import (
    PeriodicDataUpdateTemplate,
    PeriodicDataUpdateUpload,
)


class PeriodicDataUpdateTemplateListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display")
    status = serializers.CharField(source="combined_status")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")

    class Meta:
        model = PeriodicDataUpdateTemplate
        fields = (
            "id",
            "number_of_records",
            "created_at",
            "created_by",
            "status",
            "status_display",
        )


class PeriodicDataUpdateTemplateDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicDataUpdateTemplate
        fields = (
            "id",
            "rounds_data",
        )


class PeriodicDataUpdateUploadListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display")
    status = serializers.CharField(source="combined_status")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")

    class Meta:
        model = PeriodicDataUpdateUpload
        fields = (
            "id",
            "template",
            "created_at",
            "created_by",
            "status",
            "status_display",
        )


class PeriodicDataUpdateUploadDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display")
    status = serializers.CharField(source="combined_status")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")
    errors = serializers.JSONField()

    class Meta:
        model = PeriodicDataUpdateUpload
        fields = (
            "id",
            "template",
            "created_at",
            "created_by",
            "status",
            "status_display",
            "errors",
        )


class PeriodicDataUpdateUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicDataUpdateUpload
        fields = ("file",)
