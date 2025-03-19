import base64
from typing import Any, Dict, Optional

from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from apps.payment.models import Payment
from hct_mis_api.apps.account.api.fields import Base64ModelField
from hct_mis_api.apps.core.utils import decode_id_string
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
    currency = serializers.CharField(source="get_currency_display")
    follow_ups = FollowUpPaymentPlanSerializer(many=True, read_only=True)
    program = serializers.CharField(source="program_cycle.program.name")
    program_id = Base64ModelField(model_name="Program", source="program_cycle.program.id")
    last_approval_process_by = serializers.SerializerMethodField()

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "unicef_id",
            "name",
            "status",
            "targeting_criteria",
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


class PaymentPlanListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")
    currency = serializers.CharField(source="get_currency_display")
    follow_ups = FollowUpPaymentPlanSerializer(many=True, read_only=True)

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "unicef_id",
            "name",
            "status",
            "total_households_count",
            "currency",
            "excluded_ids",
            "total_entitled_quantity",
            "total_delivered_quantity",
            "total_undelivered_quantity",
            "dispersion_start_date",
            "dispersion_end_date",
            "is_follow_up",
            "follow_ups",
        )


class PaymentPlanDetailSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")
    background_action_status = serializers.CharField(source="get_background_action_status_display")
    currency = serializers.CharField(source="get_currency_display")
    follow_ups = FollowUpPaymentPlanSerializer(many=True, read_only=True)
    program = serializers.CharField(source="program_cycle.program.name")
    has_payment_list_export_file = serializers.BooleanField(source="has_export_file")
    has_fsp_delivery_mechanism_xlsx_template = serializers.SerializerMethodField()
    imported_file_name = serializers.CharField(source="imported_file_name")
    payments_conflicts_count = serializers.SerializerMethodField()
    # delivery_mechanisms = DeliveryMechanismPerPaymentPlanSerializer(many=True, read_only=True)
    bank_reconciliation_success = serializers.IntegerField(source="bank_reconciliation_success")
    bank_reconciliation_error = serializers.IntegerField(source="bank_reconciliation_error")
    can_create_payment_verification_plan = serializers.BooleanField(source="can_create_payment_verification_plan")
    available_payment_records_count = serializers.SerializerMethodField()

    # TODO: add payment list

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "unicef_id",
            "name",
            "status",
            "created_by",
            "background_action_status",
            "total_households_count",
            "total_individuals_count",
            "currency",
            "total_entitled_quantity",
            "total_delivered_quantity",
            "total_undelivered_quantity",
            "start_date",
            "end_date",
            "dispersion_start_date",
            "dispersion_end_date",
            "is_follow_up",
            "follow_ups",
            "program",
            "has_payment_list_export_file",
            "has_fsp_delivery_mechanism_xlsx_template",
            "imported_file_name",
            "payments_conflicts_count",
            # "delivery_mechanisms",  # TODO: add soon
            # "volume_by_delivery_mechanism", # TODO: add soon
            # "split_choices", # TODO: add soon if needed
            "bank_reconciliation_success",
            "bank_reconciliation_error",
            "can_create_payment_verification_plan",
            "available_payment_records_count",
            #     reconciliation_summary = graphene.Field(ReconciliationSummaryNode)
            #     excluded_households = graphene.List(HouseholdNode, description="For non-social worker DCT, returns Household IDs")
            #     excluded_individuals = graphene.List(IndividualNode, description="For social worker DCT, returns Individual IDs")
            #     can_create_follow_up = graphene.Boolean()
            #     total_withdrawn_households_count = graphene.Int()
            #     unsuccessful_payments_count = graphene.Int()
            #     name = graphene.String()
            #     can_send_to_payment_gateway = graphene.Boolean()
            #     can_split = graphene.Boolean()
            #     supporting_documents = graphene.List(PaymentPlanSupportingDocumentNode)
            #     program = graphene.Field(ProgramNode)
            #     total_households_count_with_valid_phone_no = graphene.Int()
            #     can_create_xlsx_with_fsp_auth_code = graphene.Boolean()
            #     fsp_communication_channel = graphene.String()
            #     can_export_xlsx = graphene.Boolean()
            #     can_download_xlsx = graphene.Boolean()
            #     can_send_xlsx_password = graphene.Boolean()
        )

    @staticmethod
    def _has_fsp_delivery_mechanism_xlsx_template(payment_plan: PaymentPlan) -> bool:
        if (
            not payment_plan.delivery_mechanisms.exists()
            or payment_plan.delivery_mechanisms.filter(
                Q(financial_service_provider__isnull=True) | Q(delivery_mechanism__isnull=True)
            ).exists()
        ):
            return False
        else:
            for dm_per_payment_plan in payment_plan.delivery_mechanisms.all():
                if not dm_per_payment_plan.financial_service_provider.get_xlsx_template(
                    dm_per_payment_plan.delivery_mechanism
                ):
                    return False
            return True

    def get_has_fsp_delivery_mechanism_xlsx_template(self, payment_plan: PaymentPlan) -> bool:
        return self._has_fsp_delivery_mechanism_xlsx_template(payment_plan)

    def get_payments_conflicts_count(self, payment_plan: PaymentPlan) -> int:
        return payment_plan.payment_items.filter(excluded=False, payment_plan_hard_conflicted=True).count()

    def get_available_payment_records_count(self, payment_plan: PaymentPlan) -> int:
        return payment_plan.payment_items.filter(status__in=Payment.ALLOW_CREATE_VERIFICATION, delivered_quantity__gt=0).count()




class PaymentPlanBulkActionSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.CharField())
    action = serializers.ChoiceField(PaymentPlan.Action.choices)
    comment = serializers.CharField(required=False, allow_blank=True)


class PaymentPlanSupportingDocumentSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    file = serializers.FileField(use_url=False)

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
        payment_plan_id = self.context["request"].parser_context["kwargs"]["payment_plan_id"]
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan_id))
        data["payment_plan"] = payment_plan
        data["created_by"] = self.context["request"].user
        if payment_plan.status not in [PaymentPlan.Status.OPEN, PaymentPlan.Status.LOCKED]:
            raise serializers.ValidationError("Payment plan must be within status OPEN or LOCKED.")

        if payment_plan.documents.count() >= PaymentPlanSupportingDocument.FILE_LIMIT:
            raise serializers.ValidationError(
                f"Payment plan already has the maximum of {PaymentPlanSupportingDocument.FILE_LIMIT} supporting documents."
            )
        return data

    def create(self, validated_data: Dict[str, Any]) -> PaymentPlanSupportingDocument:
        return super().create(validated_data)
