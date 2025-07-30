from typing import Optional

from rest_framework import serializers

from hct_mis_api.apps.activity_log.models import LogEntry
from hct_mis_api.apps.program.models import Program


class LogEntrySerializer(serializers.ModelSerializer):
    is_user_generated = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    action = serializers.CharField(source="get_action_display")
    user = serializers.SerializerMethodField()
    program_slug = serializers.SerializerMethodField()

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
            "program_slug",
        )

    def get_is_user_generated(self, obj: LogEntry) -> bool | None:
        from hct_mis_api.apps.grievance.models import GrievanceTicket

        if isinstance(obj.content_object, GrievanceTicket):
            return obj.content_object.grievance_type_to_string() == "user"
        return None

    def get_user(self, obj: LogEntry) -> str:
        if not obj.user:
            return "-"
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_content_type(self, obj: LogEntry) -> str:
        if obj.content_type:
            return obj.content_type.name
        return ""

    def get_program_slug(self, obj: LogEntry) -> Optional[str]:
        if obj.content_type and obj.content_type.model  == Program._meta.model_name:
            return Program.objects.get(id=obj.object_id).slug
        return None
