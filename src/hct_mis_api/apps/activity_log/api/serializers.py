from typing import Optional

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from hct_mis_api.apps.activity_log.models import LogEntry


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ("model",)


class LogEntrySerializer(serializers.ModelSerializer):
    is_user_generated = serializers.SerializerMethodField()
    content_type = ContentTypeSerializer()
    action = serializers.CharField(source="get_action_display")
    user = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = (
            "object_id",
            "action",
            "changes",
            "timestamp",
            "is_user_generated",
            "content_type",
            "object_repr",
            "user",
        )

    def get_is_user_generated(self, obj: LogEntry) -> Optional[bool]:
        from hct_mis_api.apps.grievance.models import GrievanceTicket

        if isinstance(obj.content_object, GrievanceTicket):
            return obj.content_object.grievance_type_to_string() == "user"
        return None

    def get_user(self, obj: LogEntry) -> str:
        if not obj.user:
            return "-"
        return f"{obj.user.first_name} {obj.user.last_name}"
