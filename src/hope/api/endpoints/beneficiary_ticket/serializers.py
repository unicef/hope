from typing import Any

from rest_framework import serializers

from hope.apps.grievance.constants import PRIORITY_CHOICES, URGENCY_CHOICES
from hope.apps.grievance.models import GrievanceTicket
from hope.models import Program, User


class BeneficiaryTicketCreateSerializer(serializers.Serializer):
    description = serializers.CharField(required=True)
    program = serializers.PrimaryKeyRelatedField(
        queryset=Program.objects.all(),
        required=False,
        allow_null=True,
    )
    priority = serializers.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
    )
    urgency = serializers.ChoiceField(
        choices=URGENCY_CHOICES,
        required=False,
    )
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )


class BeneficiaryTicketResponseSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="unicef_id")
    category = serializers.SerializerMethodField()
    business_area = serializers.SerializerMethodField()
    assigned_to = serializers.SerializerMethodField()

    class Meta:
        model = GrievanceTicket
        fields = (
            "id",
            "code",
            "category",
            "business_area",
            "description",
            "priority",
            "urgency",
            "assigned_to",
        )

    def get_category(self, obj: GrievanceTicket) -> str:
        return "Beneficiary"

    def get_business_area(self, obj: GrievanceTicket) -> dict[str, Any]:
        return {
            "slug": obj.business_area.slug,
            "name": obj.business_area.name,
        }

    def get_assigned_to(self, obj: GrievanceTicket) -> dict[str, Any] | None:
        if obj.assigned_to:
            return {
                "id": str(obj.assigned_to.id),
                "email": obj.assigned_to.email,
                "first_name": obj.assigned_to.first_name,
                "last_name": obj.assigned_to.last_name,
            }
        return None
