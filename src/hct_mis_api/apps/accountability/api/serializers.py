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
    household_unicef_id = serializers.CharField(source="household_lookup.unicef_id")
    household_id = serializers.CharField(source="household_lookup.id")
    individual_unicef_id = serializers.CharField(source="individual_lookup.unicef_id")
    individual_id = serializers.CharField(source="individual_lookup.id")
    linked_grievance_id = serializers.CharField(source="linked_grievance.id")
    linked_grievance_unicef_id = serializers.CharField(source="linked_grievance.unicef_id")
    program_name = serializers.CharField(source="program.name")
    program_id = serializers.CharField(source="program.id")
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
            "program_name",
            "program_id",
            "created_by",
            "created_at",
        )

    def get_created_by(self, obj: Feedback) -> str:
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"


class FeedbackDetailSerializer(AdminUrlSerializerMixin, FeedbackListSerializer):
    admin2_name = serializers.CharField(source="admin2.name")

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


class FeedbackCreateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    issue_type = serializers.ChoiceField(required=True, choices=Feedback.ISSUE_TYPE_CHOICES)
    household__lookup = serializers.CharField(allow_null=True, allow_blank=True)
    individual_lookup = serializers.CharField(allow_null=True, allow_blank=True)
    program_id = serializers.CharField(allow_null=True, allow_blank=True)
    area = serializers.CharField(allow_null=True, allow_blank=True)
    admin2 = serializers.CharField(allow_null=True, allow_blank=True)
    description = serializers.CharField(required=True)
    language = serializers.CharField(allow_blank=True)
    comments = serializers.CharField(allow_null=True, allow_blank=True)
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
    id = serializers.CharField(read_only=True)
    description = serializers.CharField(required=True)
    comments = serializers.CharField(allow_null=True, allow_blank=True)
    area = serializers.CharField(allow_null=True, allow_blank=True)
    admin2 = serializers.CharField(allow_null=True, allow_blank=True)
    language = serializers.CharField(allow_blank=True)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "area",
            "admin2",
            "description",
            "language",
            "comments",
        )
