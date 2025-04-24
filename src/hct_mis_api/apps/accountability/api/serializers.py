from typing import Optional

from rest_framework import serializers

from hct_mis_api.apps.accountability.models import Feedback, FeedbackMessage
from hct_mis_api.apps.core.api.mixins import AdminUrlSerializerMixin


class FeedbackMessageSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackMessage
        fields = (
            "id",
            "description",
            "created_by",
            "created_at",
        )


class FeedbackListSerializer(serializers.ModelSerializer):
    issue_type = serializers.CharField(source="get_issue_type_display")
    household_unicef_id = serializers.SerializerMethodField()
    household_id = serializers.SerializerMethodField()
    individual_unicef_id = serializers.SerializerMethodField()
    individual_id = serializers.SerializerMethodField()
    linked_grievance_unicef_id = serializers.SerializerMethodField()
    program_name = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    feedback_messages = FeedbackMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "unicef_id",
            "issue_type",
            "household_unicef_id",
            "household_id",
            "individual_unicef_id",
            "individual_id",
            "linked_grievance_id",
            "linked_grievance_unicef_id",
            "program_name",
            "program_id",
            "created_by",
            "created_at",
            "feedback_messages",
        )

    def get_created_by(self, obj: Feedback) -> str:
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"

    def get_household_unicef_id(self, obj: Feedback) -> Optional[str]:
        return getattr(obj.household_lookup, "unicef_id", None)

    def get_household_id(self, obj: Feedback) -> Optional[str]:
        return getattr(obj.household_lookup, "id", None)

    def get_individual_unicef_id(self, obj: Feedback) -> Optional[str]:
        return getattr(obj.individual_lookup, "unicef_id", None)

    def get_individual_id(self, obj: Feedback) -> Optional[str]:
        return getattr(obj.individual_lookup, "id", None)

    def get_linked_grievance_unicef_id(self, obj: Feedback) -> Optional[str]:
        return getattr(obj.linked_grievance, "unicef_id", None)

    def get_program_name(self, obj: Feedback) -> Optional[str]:
        return getattr(obj.program, "name", None)


class FeedbackDetailSerializer(AdminUrlSerializerMixin, FeedbackListSerializer):
    admin2_name = serializers.SerializerMethodField()

    class Meta(FeedbackListSerializer.Meta):
        fields = FeedbackListSerializer.Meta.fields + (  # type: ignore
            "description",
            "area",
            "language",
            "comments",
            "consent",
            "updated_at",
            "admin2_name",
        )

    def get_admin2_name(self, obj: Feedback) -> Optional[str]:
        return getattr(obj.admin2, "name", None)


class FeedbackCreateSerializer(serializers.ModelSerializer):
    issue_type = serializers.ChoiceField(required=True, choices=Feedback.ISSUE_TYPE_CHOICES)
    household_lookup = serializers.UUIDField(allow_null=True, required=False)
    individual_lookup = serializers.UUIDField(allow_null=True, required=False)
    program_id = serializers.UUIDField(allow_null=True, required=False)
    area = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    admin2 = serializers.UUIDField(allow_null=True, required=False)
    description = serializers.CharField(required=True)
    language = serializers.CharField(allow_blank=True, required=False)
    comments = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    consent = serializers.BooleanField(default=True)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "issue_type",
            "household_lookup",
            "individual_lookup",
            "program_id",
            "area",
            "admin2",
            "description",
            "language",
            "comments",
            "consent",
        )


class FeedbackUpdateSerializer(serializers.ModelSerializer):
    issue_type = serializers.ChoiceField(required=True, choices=Feedback.ISSUE_TYPE_CHOICES)
    household_lookup = serializers.UUIDField(allow_null=True, required=False)
    individual_lookup = serializers.UUIDField(allow_null=True, required=False)
    description = serializers.CharField(required=True)
    comments = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    area = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    admin2 = serializers.UUIDField(allow_null=True, required=False)
    language = serializers.CharField(allow_blank=True, required=False)
    consent = serializers.BooleanField(required=False)

    class Meta:
        model = Feedback
        fields = (
            "issue_type",
            "household_lookup",
            "individual_lookup",
            "area",
            "admin2",
            "description",
            "language",
            "comments",
            "consent",
        )
