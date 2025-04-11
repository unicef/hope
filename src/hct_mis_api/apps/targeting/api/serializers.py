from rest_framework import serializers

from hct_mis_api.apps.payment.models import PaymentPlan


class TargetPopulationListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField(method_name="get_status")
    created_by = serializers.CharField(source="created_by.get_full_name", default="")

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "name",
            "status",
            "created_by",
            "created_at",
        )

    @staticmethod
    def get_status(obj: PaymentPlan) -> str:
        if obj.status in PaymentPlan.PRE_PAYMENT_PLAN_STATUSES:
            return obj.get_status_display()
        else:
            return "Assigned"
