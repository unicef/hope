from typing import Any

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from hope.apps.core.models import (
    BusinessArea,
    FlexibleAttribute,
    PeriodicFieldData,
)
from hope.apps.periodic_data_update.models import (
    PeriodicDataUpdateXlsxTemplate,
    PeriodicDataUpdateXlsxUpload,
    PeriodicDataUpdateOnlineEdit,
    PeriodicDataUpdateOnlineEditSentBackComment,
)
from hope.apps.periodic_data_update.utils import update_rounds_covered_for_template
from hope.apps.program.models import Program


class PeriodicDataUpdateXlsxTemplateListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="combined_status_display")
    status = serializers.CharField(source="combined_status")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")
    can_export = serializers.BooleanField()

    class Meta:
        model = PeriodicDataUpdateXlsxTemplate
        fields = (
            "id",
            "name",
            "number_of_records",
            "created_at",
            "created_by",
            "status",
            "status_display",
            "can_export",
        )


class PeriodicDataUpdateXlsxTemplateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicDataUpdateXlsxTemplate
        fields = (
            "id",
            "name",
            "rounds_data",
            "filters",
            "created_by",
        )
        read_only_fields = ("created_by",)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        rounds_data = data.get("rounds_data", [])
        # Check for duplicate field names
        field_names = [item["field"] for item in rounds_data]
        if len(field_names) != len(set(field_names)):
            raise serializers.ValidationError({"rounds_data": "Each Field can only be used once in the template."})
        return data

    def create(self, validated_data: dict[str, Any]) -> PeriodicDataUpdateXlsxTemplate:
        request = self.context["request"]
        business_area_slug = self.context["request"].parser_context["kwargs"]["business_area_slug"]
        program_slug = self.context["request"].parser_context["kwargs"]["program_slug"]
        validated_data["created_by"] = request.user
        business_area = get_object_or_404(BusinessArea, slug=business_area_slug)
        validated_data["business_area"] = get_object_or_404(BusinessArea, slug=business_area_slug)
        validated_data["program"] = get_object_or_404(Program, slug=program_slug, business_area=business_area)
        pdu_template = super().create(validated_data)
        update_rounds_covered_for_template(pdu_template, validated_data["rounds_data"])
        return pdu_template


class PeriodicDataUpdateXlsxTemplateDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicDataUpdateXlsxTemplate
        fields = (
            "id",
            "name",
            "rounds_data",
        )


class PeriodicDataUpdateXlsxUploadListSerializer(serializers.ModelSerializer):
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


class PeriodicDataUpdateXlsxUploadDetailSerializer(serializers.ModelSerializer):
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


class PeriodicDataUpdateXlsxUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicDataUpdateXlsxUpload
        fields = ("file",)


class PeriodicFieldDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicFieldData
        fields = ("subtype", "number_of_rounds", "rounds_names", "rounds_covered")


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


class AuthorizedUserSerializer(serializers.ModelSerializer):
    pdu_roles = serializers.SerializerMethodField()
    class Meta:
        model = get_user_model()
        fields = ("id", "first_name", "last_name", "username")

    def get_pdu_roles(self, obj: get_user_model()) -> list[str]:
        pass # TODO: PDU - add logic to retrieve PDU roles for the user


class PeriodicDataUpdateOnlineEditSentBackCommentSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = PeriodicDataUpdateOnlineEditSentBackComment
        fields = ("comment", "created_by", "created_at")


class PeriodicDataUpdateOnlineEditListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="combined_status_display")
    status = serializers.CharField(source="combined_status")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")
    is_authorized = serializers.SerializerMethodField()

    class Meta:
        model = PeriodicDataUpdateOnlineEdit
        fields = (
            "id",
            "name",
            "number_of_records",
            "created_at",
            "created_by",
            "status",
            "status_display",
        )

    def get_is_authorized(self, obj: PeriodicDataUpdateOnlineEdit) -> bool:
        request = self.context.get("request")
        user = request.user
        return user in obj.authorized_users.all()


class PeriodicDataUpdateOnlineEditDetailSerializer(PeriodicDataUpdateOnlineEditListSerializer):
    sent_back_comment = PeriodicDataUpdateOnlineEditSentBackCommentSerializer()
    authorized_users = AuthorizedUserSerializer(many=True)

    class Meta:
        model = PeriodicDataUpdateOnlineEdit
        fields = PeriodicDataUpdateOnlineEditListSerializer.Meta.fields + (  # type: ignore
            "approved_by",
            "approved_at",
            "sent_back_comment",
            "edit_data",
            "authorized_users",
        )


class PeriodicDataUpdateOnlineEditCreateSerializer(serializers.ModelSerializer):
    filters = serializers.JSONField(write_only=True)
    rounds_data = serializers.ListField(child=serializers.DictField(), write_only=True)
    authorized_users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=get_user_model().objects.all(), required=False
    )

    class Meta:
        model = PeriodicDataUpdateOnlineEdit
        fields = (
            "id",
            "name",
            "rounds_data",
            "filters",
            "created_by",
            "authorized_users",
        )
        read_only_fields = ("created_by",)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        rounds_data = data.get("rounds_data", [])
        # Check for duplicate field names
        field_names = [item["field"] for item in rounds_data]
        if len(field_names) != len(set(field_names)):
            raise serializers.ValidationError({"rounds_data": "Each Field can only be used once in the template."})
        return data

    def create(self, validated_data):
        request = self.context["request"]
        business_area_slug = request.parser_context["kwargs"]["business_area_slug"]
        program_slug = request.parser_context["kwargs"]["program_slug"]
        validated_data["created_by"] = request.user
        business_area = get_object_or_404(BusinessArea, slug=business_area_slug)
        validated_data["business_area"] = business_area
        validated_data["program"] = get_object_or_404(Program, slug=program_slug, business_area=business_area)

        authorized_users = validated_data.pop("authorized_users", [])

        pdu_online_edit = super().create(validated_data)
        update_rounds_covered_for_template(pdu_online_edit, validated_data["rounds_data"])

        if authorized_users:
            pdu_online_edit.authorized_users.set(authorized_users)

        # TODO: PDU - add logic to populate pdu_data for the fields in the template; call the task

        return pdu_online_edit


class PeriodicDataUpdateOnlineEditSaveDataSerializer(serializers.Serializer):
    individual_edit_data = serializers.JSONField()


class PeriodicDataUpdateOnlineEditSendBackSerializer(serializers.Serializer):
    comment = serializers.CharField(allow_blank=False, trim_whitespace=True)


class BulkSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)