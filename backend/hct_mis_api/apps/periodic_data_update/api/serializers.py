from rest_framework import serializers

from hct_mis_api.apps.periodic_data_update.models import (
    PeriodicDataUpdateTemplate,
    PeriodicDataUpdateUpload,
)


class PeriodicDataUpdateTemplateListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")

    class Meta:
        model = PeriodicDataUpdateTemplate
        fields = (
            "id",
            "number_of_records",
            "created_at",
            "created_by",
            "status",
        )


class PeriodicDataUpdateTemplateDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicDataUpdateTemplate
        fields = (
            "id",
            "rounds_data",
        )


class PeriodicDataUpdateUploadListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")

    class Meta:
        model = PeriodicDataUpdateUpload
        fields = (
            "id",
            "template",
            "created_at",
            "created_by",
            "status",
        )


class PeriodicDataUpdateUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicDataUpdateUpload
        fields = ("file",)
