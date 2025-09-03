import datetime
from typing import Any

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

from hope.apps.account.models import RoleAssignment, User
from hope.apps.account.permissions import Permissions
from hope.apps.core.models import BusinessArea, FlexibleAttribute, PeriodicFieldData
from hope.apps.periodic_data_update.models import (
    PDUOnlineEdit,
    PDUOnlineEditSentBackComment,
    PDUXlsxTemplate,
    PDUXlsxUpload,
)
from hope.apps.periodic_data_update.utils import update_rounds_covered_for_template
from hope.apps.program.models import Program

PDU_ONLINE_EDIT_RELATED_PERMISSIONS = [
    Permissions.PDU_ONLINE_SAVE_DATA,
    Permissions.PDU_ONLINE_APPROVE,
    Permissions.PDU_ONLINE_MERGE,
]


class PDUXlsxTemplateListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="combined_status_display")
    status = serializers.CharField(source="combined_status")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")
    can_export = serializers.BooleanField()

    class Meta:
        model = PDUXlsxTemplate
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


class PDUXlsxTemplateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDUXlsxTemplate
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

    def create(self, validated_data: dict[str, Any]) -> PDUXlsxTemplate:
        request = self.context["request"]
        business_area_slug = request.parser_context["kwargs"]["business_area_slug"]
        program_slug = request.parser_context["kwargs"]["program_slug"]
        validated_data["created_by"] = request.user
        business_area = get_object_or_404(BusinessArea, slug=business_area_slug)
        validated_data["business_area"] = get_object_or_404(BusinessArea, slug=business_area_slug)
        validated_data["program"] = get_object_or_404(Program, slug=program_slug, business_area=business_area)
        pdu_template = super().create(validated_data)
        update_rounds_covered_for_template(pdu_template, validated_data["rounds_data"])
        return pdu_template


class PDUXlsxTemplateDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDUXlsxTemplate
        fields = (
            "id",
            "name",
            "rounds_data",
        )


class PDUXlsxUploadListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="combined_status_display")
    status = serializers.CharField(source="combined_status")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")

    class Meta:
        model = PDUXlsxUpload
        fields = (
            "id",
            "template",
            "created_at",
            "created_by",
            "status",
            "status_display",
        )


class PDUXlsxUploadDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="combined_status_display")
    status = serializers.CharField(source="combined_status")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")
    errors_info = serializers.JSONField(source="errors")

    class Meta:
        model = PDUXlsxUpload
        fields = (
            "id",
            "template",
            "created_at",
            "created_by",
            "status",
            "status_display",
            "errors_info",
        )


class PDUXlsxUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDUXlsxUpload
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
    pdu_permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "username", "email", "pdu_permissions")

    def get_pdu_permissions(self, user: User) -> list[str]:
        # use cached role assignments if available - when used in "users_available" action
        cached_user_roles = getattr(user, "cached_relevant_role_assignments", [])
        cached_partner_roles = getattr(user.partner, "cached_relevant_role_assignments_partner", [])
        cached_roles = list(cached_user_roles) + list(cached_partner_roles)
        if cached_roles:
            perms = set()
            for ra in cached_roles:
                perms.update(
                    p for p in ra.role.permissions if p in [perm.value for perm in PDU_ONLINE_EDIT_RELATED_PERMISSIONS]
                )
            return sorted(perms)

        permissions_from_roles = (
            RoleAssignment.objects.filter(
                Q(user=user) | Q(partner=user.partner),
                Q(business_area__slug=self.context["request"].parser_context["kwargs"]["business_area_slug"])
                & (
                    Q(program__slug=self.context["request"].parser_context["kwargs"]["program_slug"])
                    | Q(program__isnull=True)
                )
                & Q(role__permissions__overlap=[perm.value for perm in PDU_ONLINE_EDIT_RELATED_PERMISSIONS]),
            )
            .exclude(expiry_date__lt=timezone.now())
            .values_list("role__permissions", flat=True)
        )

        pdu_online_related_permissions = {
            permission
            for permission_list in permissions_from_roles
            for permission in permission_list
            if permission in [perm.value for perm in PDU_ONLINE_EDIT_RELATED_PERMISSIONS]
        }
        return sorted(pdu_online_related_permissions)


class PDUOnlineEditSentBackCommentSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = PDUOnlineEditSentBackComment
        fields = ("comment", "created_by", "created_at")


class PDUOnlineEditListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="combined_status_display")
    status = serializers.CharField(source="combined_status")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")
    is_authorized = serializers.SerializerMethodField()

    class Meta:
        model = PDUOnlineEdit
        fields = (
            "id",
            "name",
            "number_of_records",
            "created_at",
            "created_by",
            "status",
            "status_display",
            "is_authorized",
        )

    def get_is_authorized(self, obj: PDUOnlineEdit) -> bool:
        request = self.context.get("request")
        user = request.user
        return user in obj.authorized_users.all()


class PDUOnlineEditDetailSerializer(PDUOnlineEditListSerializer):
    sent_back_comment = PDUOnlineEditSentBackCommentSerializer()
    authorized_users = AuthorizedUserSerializer(many=True)
    approved_by = serializers.CharField(source="approved_by.get_full_name", default="")
    is_creator = serializers.SerializerMethodField()

    class Meta:
        model = PDUOnlineEdit
        fields = PDUOnlineEditListSerializer.Meta.fields + (  # type: ignore
            "approved_by",
            "approved_at",
            "sent_back_comment",
            "edit_data",
            "authorized_users",
            "is_creator",
        )

    def get_is_creator(self, obj: PDUOnlineEdit) -> bool:
        request = self.context.get("request")
        return obj.created_by == request.user


class PDUOnlineEditCreateSerializer(serializers.ModelSerializer):
    filters = serializers.JSONField(write_only=True)
    rounds_data = serializers.ListField(child=serializers.DictField(), write_only=True)
    authorized_users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    created_by = serializers.CharField(source="created_by.get_full_name", default="")

    class Meta:
        model = PDUOnlineEdit
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
        business_area = get_object_or_404(BusinessArea, slug=business_area_slug)

        validated_data["created_by"] = request.user
        validated_data["business_area"] = business_area
        validated_data["program"] = get_object_or_404(Program, slug=program_slug, business_area=business_area)

        # Pop fields that are not on the model before creating the instance
        validated_data.pop("filters", None)
        rounds_data = validated_data.pop("rounds_data", None)

        authorized_users = validated_data.pop("authorized_users", [])

        pdu_online_edit = super().create(validated_data)
        update_rounds_covered_for_template(pdu_online_edit, rounds_data)

        if authorized_users:
            pdu_online_edit.authorized_users.set(authorized_users)

        return pdu_online_edit


class PDUOnlineEditUpdateAuthorizedUsersSerializer(serializers.ModelSerializer):
    authorized_users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=True, allow_empty=True
    )

    class Meta:
        model = PDUOnlineEdit
        fields = ("authorized_users",)


class PDUOnlineEditSaveDataSerializer(serializers.Serializer):
    individual_uuid = serializers.UUIDField()
    pdu_fields = serializers.DictField(child=serializers.DictField())

    def validate(self, data):
        individual_uuid = str(data.get("individual_uuid"))
        pdu_fields_update = data.get("pdu_fields", {})

        pdu_online_edit = self.context.get("pdu_online_edit")
        if not pdu_online_edit:
            raise serializers.ValidationError("PDU Online Edit context is required")

        # Validate pdu_fields structure
        if not isinstance(pdu_fields_update, dict):
            raise serializers.ValidationError("pdu_fields must be a dictionary")

        # Find individual in edit_data
        individual_data = next(
            (item for item in pdu_online_edit.edit_data if item.get("individual_uuid") == individual_uuid), None
        )

        if not individual_data:
            raise serializers.ValidationError(
                f"Individual with UUID {individual_uuid} not found in this PDU Online Edit"
            )

        # Validate each field in pdu_fields
        for field_name, field_data in pdu_fields_update.items():
            if not isinstance(field_data, dict):
                raise serializers.ValidationError(f"Field data for '{field_name}' must be a dictionary")

            required_keys = {"value", "subtype", "is_editable", "round_number"}
            if not required_keys.issubset(field_data.keys()):
                raise serializers.ValidationError(f"Field '{field_name}' must contain keys: {required_keys}")

            subtype = field_data.get("subtype")
            field_value = field_data.get("value")
            is_editable = field_data.get("is_editable")

            existing_pdu_fields = individual_data.get("pdu_fields", {})
            if field_name not in existing_pdu_fields:
                raise serializers.ValidationError(f"Field '{field_name}' is not within fields selected for this edit")

            # For non-editable fields, check if the value is being changed
            if not is_editable:
                existing_value = existing_pdu_fields[field_name].get("value")
                if field_value != existing_value:
                    raise serializers.ValidationError(f"Field '{field_name}' is not editable and cannot be modified")
                # Skip type validation for non-editable fields since they won't be updated
                continue

            # Skip further validation if value is None
            if field_value is None:
                continue

            # Validate value type based on subtype
            if subtype == PeriodicFieldData.BOOL and not isinstance(field_value, bool):
                raise serializers.ValidationError(
                    f"Field '{field_name}' expects a boolean value, got {type(field_value).__name__}"
                )
            if subtype == PeriodicFieldData.DECIMAL and not isinstance(field_value, int | float):
                raise serializers.ValidationError(
                    f"Field '{field_name}' expects a number value, got {type(field_value).__name__}"
                )
            if subtype == PeriodicFieldData.STRING and not isinstance(field_value, str):
                raise serializers.ValidationError(
                    f"Field '{field_name}' expects a string value, got {type(field_value).__name__}"
                )
            if subtype == PeriodicFieldData.DATE:
                if not isinstance(field_value, str):
                    raise serializers.ValidationError(
                        f"Field '{field_name}' expects a string value for date, got {type(field_value).__name__}"
                    )
                try:
                    datetime.date.fromisoformat(field_value)
                except (TypeError, ValueError):
                    raise serializers.ValidationError(
                        f"Field '{field_name}' has invalid date format. Expected YYYY-MM-DD"
                    )

        return data


class PDUOnlineEditSendBackSerializer(serializers.Serializer):
    comment = serializers.CharField(allow_blank=False, trim_whitespace=True)


class BulkSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
