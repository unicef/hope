import base64
from typing import Any, Dict, Optional

from rest_framework import serializers

from hct_mis_api.apps.account.api.fields import Base64ModelField
from hct_mis_api.apps.payment.models import PaymentPlan, PaymentPlanSupportingDocument


class FollowUpPaymentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "unicef_id",
        )


class PaymentPlanSerializer(serializers.ModelSerializer):
    id = Base64ModelField(model_name="PaymentPlan")
    status = serializers.CharField(source="get_status_display")
    target_population = serializers.CharField(source="target_population.name")
    currency = serializers.CharField(source="get_currency_display")
    follow_ups = FollowUpPaymentPlanSerializer(many=True, read_only=True)
    program = serializers.CharField(source="program.name")
    program_id = Base64ModelField(model_name="Program")
    last_approval_process_by = serializers.SerializerMethodField()

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "unicef_id",
            "name",
            "status",
            "target_population",
            "total_households_count",
            "currency",
            "total_entitled_quantity",
            "total_delivered_quantity",
            "total_undelivered_quantity",
            "dispersion_start_date",
            "dispersion_end_date",
            "is_follow_up",
            "follow_ups",
            "program",
            "program_id",
            "last_approval_process_date",
            "last_approval_process_by",
        )

    def get_last_approval_process_by(self, obj: PaymentPlan) -> Optional[str]:
        return str(obj.last_approval_process_by) if obj.last_approval_process_by else None


class PaymentPlanBulkActionSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.CharField())
    action = serializers.ChoiceField(PaymentPlan.Action.choices)
    comment = serializers.CharField(required=False, allow_blank=True)


class PaymentPlanSupportingDocumentSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = PaymentPlanSupportingDocument
        fields = ["id", "title", "file", "uploaded_at", "created_by"]

    def get_id(self, obj: PaymentPlanSupportingDocument) -> str:
        return base64.b64encode(f"PaymentPlanSupportingDocumentNode:{str(obj.id)}".encode()).decode()

    def validate_file(self, file: Any) -> Any:
        if file.size > PaymentPlanSupportingDocument.FILE_SIZE_LIMIT:
            raise serializers.ValidationError("File size must be ≤ 10MB.")

        allowed_extensions = ["pdf", "xlsx", "jpg", "jpeg", "png"]
        extension = file.name.split(".")[-1].lower()
        if extension not in allowed_extensions:
            raise serializers.ValidationError("Unsupported file type.")

        return file

    def validate(self, data: Dict) -> Dict:
        payment_plan = self.context["payment_plan"]
        if payment_plan.status not in [PaymentPlan.Status.OPEN, PaymentPlan.Status.LOCKED]:
            raise serializers.ValidationError("Payment plan must be within status OPEN or LOCKED.")

        if payment_plan.documents.count() >= PaymentPlanSupportingDocument.FILE_LIMIT:
            raise serializers.ValidationError(
                f"Payment plan already has the maximum of {PaymentPlanSupportingDocument.FILE_LIMIT} supporting documents."
            )
        return data
