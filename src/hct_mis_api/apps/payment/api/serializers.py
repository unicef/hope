import json
from decimal import Decimal
from typing import Any

from django.db.models import Count, Prefetch, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from django.db import transaction

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.core.api.mixins import AdminUrlSerializerMixin
from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.core.utils import (
    check_concurrency_version_in_mutation,
    to_choice_object,
)
from hct_mis_api.apps.household.api.serializers.household import (
    HouseholdDetailSerializer,
    HouseholdSmallSerializer,
)
from hct_mis_api.apps.household.api.serializers.individual import (
    IndividualDetailSerializer,
    IndividualListSerializer,
    IndividualSmallSerializer,
)
from hct_mis_api.apps.household.models import (
    STATUS_ACTIVE,
    STATUS_INACTIVE,
    Household,
    Individual,
)
from hct_mis_api.apps.payment.models import (
    Approval,
    ApprovalProcess,
    FinancialServiceProvider,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
    PaymentPlanSupportingDocument,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
)
from hct_mis_api.apps.payment.models.payment import (
    DeliveryMechanism,
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProviderXlsxTemplate,
)
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.payment.xlsx.xlsx_error import XlsxError
from hct_mis_api.apps.program.api.serializers import (
    ProgramCycleSmallSerializer,
    ProgramSmallSerializer,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.steficon.api.serializers import RuleCommitSerializer
from hct_mis_api.apps.targeting.api.serializers import TargetingCriteriaRuleSerializer
from hct_mis_api.contrib.api.serializers.vision import FundsCommitmentSerializer
from hct_mis_api.contrib.vision.models import FundsCommitmentGroup, FundsCommitmentItem


class PaymentPlanSupportingDocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(use_url=False)

    class Meta:
        model = PaymentPlanSupportingDocument
        fields = ["id", "title", "file", "uploaded_at", "created_by"]

    def validate_file(self, file: Any) -> Any:
        if file.size > PaymentPlanSupportingDocument.FILE_SIZE_LIMIT:
            raise serializers.ValidationError("File size must be ≤ 10MB.")

        allowed_extensions = ["pdf", "xlsx", "jpg", "jpeg", "png"]
        extension = file.name.split(".")[-1].lower()
        if extension not in allowed_extensions:
            raise serializers.ValidationError("Unsupported file type.")

        return file

    def validate(self, data: dict) -> dict:
        payment_plan_id = self.context["request"].parser_context["kwargs"]["payment_plan_id"]
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        data["payment_plan"] = payment_plan
        data["created_by"] = self.context["request"].user
        if payment_plan.status not in [PaymentPlan.Status.OPEN, PaymentPlan.Status.LOCKED]:
            raise serializers.ValidationError("Payment plan must be within status OPEN or LOCKED.")

        if payment_plan.documents.count() >= PaymentPlanSupportingDocument.FILE_LIMIT:
            raise serializers.ValidationError(
                f"Payment plan already has the maximum of {PaymentPlanSupportingDocument.FILE_LIMIT} supporting documents."
            )
        return data

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> PaymentPlanSupportingDocument:
        return super().create(validated_data)


class XlsxErrorSerializer(serializers.Serializer):
    sheet = serializers.CharField()
    coordinates = serializers.CharField()
    message = serializers.CharField()

    @staticmethod
    def get_sheet(parent: XlsxError) -> str:
        return parent.sheet

    @staticmethod
    def get_coordinates(parent: XlsxError) -> str | None:
        return parent.coordinates

    @staticmethod
    def get_message(parent: XlsxError) -> str:
        return parent.message


class AcceptanceProcessSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False)


class PaymentPlanExportAuthCodeSerializer(serializers.Serializer):
    fsp_xlsx_template_id = serializers.CharField(required=True)


class SplitPaymentPlanSerializer(serializers.Serializer):
    split_type = serializers.ChoiceField(required=True, choices=PaymentPlanSplit.SplitType)
    payments_no = serializers.IntegerField(required=False)


class PaymentPlanImportFileSerializer(serializers.Serializer):
    file = serializers.FileField(use_url=False, required=True)

    def validate_file(self, file: Any) -> Any:
        allowed_extensions = ["xlsx"]
        extension = file.name.split(".")[-1].lower()
        if extension not in allowed_extensions:
            raise serializers.ValidationError(f"Unsupported file type ({extension}).")
        return file


class PaymentVerificationSummarySerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")
    number_of_verification_plans = serializers.SerializerMethodField()

    class Meta:
        model = PaymentVerificationSummary
        fields = ("id", "status", "activation_date", "completion_date", "number_of_verification_plans")

    def get_number_of_verification_plans(self, obj: PaymentVerificationSummary) -> int:
        return obj.payment_plan.payment_verification_plans.count()


class PaymentVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentVerification
        fields = ("id", "status", "status_date", "received_amount")


class PaymentVerificationPlanSmallSerializer(serializers.ModelSerializer):
    # status = serializers.CharField(source="get_status_display")
    # verification_channel = serializers.CharField(source="get_verification_channel_display")

    class Meta:
        model = PaymentVerificationPlan
        fields = (
            "id",
            "status",
            # "verification_channel",
            "activation_date",
            "completion_date",
        )


class PaymentVerificationPlanSerializer(AdminUrlSerializerMixin, serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display")
    verification_channel = serializers.CharField(source="get_verification_channel_display")
    sampling = serializers.CharField(source="get_sampling_display")
    has_xlsx_file = serializers.SerializerMethodField()
    xlsx_file_was_downloaded = serializers.SerializerMethodField()
    age_filter_min = serializers.SerializerMethodField()
    age_filter_max = serializers.SerializerMethodField()

    class Meta:
        model = PaymentVerificationPlan
        fields = (
            "id",
            "unicef_id",
            "status",
            "status_display",
            "verification_channel",
            "sampling",
            "sex_filter",
            "activation_date",
            "completion_date",
            "sample_size",
            "responded_count",
            "received_count",
            "not_received_count",
            "received_with_problems_count",
            "confidence_interval",
            "margin_of_error",
            "xlsx_file_exporting",
            "xlsx_file_imported",
            "has_xlsx_file",
            "xlsx_file_was_downloaded",
            "error",
            "age_filter_min",
            "age_filter_max",
            "excluded_admin_areas_filter",
            "rapid_pro_flow_id",
            "admin_url",
        )

    def get_has_xlsx_file(self, obj: PaymentVerificationPlan) -> bool:
        return obj.has_xlsx_payment_verification_plan_file

    def get_xlsx_file_was_downloaded(self, obj: PaymentVerificationPlan) -> bool:
        return obj.xlsx_payment_verification_plan_file_was_downloaded

    def get_age_filter_min(self, obj: PaymentVerificationPlan) -> int | None:
        return obj.age_filter.get("min") if obj.age_filter else None

    def get_age_filter_max(self, obj: PaymentVerificationPlan) -> int | None:
        return obj.age_filter.get("max") if obj.age_filter else None


class FollowUpPaymentPlanSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "unicef_id",
            "status",
            "dispersion_start_date",
            "dispersion_end_date",
            "is_follow_up",
            "name",
        )


class PaymentVerificationPlanDetailsSerializer(serializers.ModelSerializer):
    payment_verification_plans = PaymentVerificationPlanSerializer(many=True)
    payment_verification_summary = PaymentVerificationSummarySerializer()
    program_cycle_start_date = serializers.DateField(source="program_cycle.start_date")
    program_cycle_end_date = serializers.DateField(source="program_cycle.start_date")
    program_name = serializers.CharField(source="program_cycle.program.name")
    program_id = serializers.CharField(source="program_cycle.program_id")
    available_payment_records_count = serializers.SerializerMethodField()
    eligible_payments_count = serializers.SerializerMethodField()
    bank_reconciliation_success = serializers.IntegerField()
    bank_reconciliation_error = serializers.IntegerField()
    can_create_payment_verification_plan = serializers.BooleanField()
    # verificationPlansTotalCount

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "unicef_id",
            "program_name",
            "program_id",
            "program_cycle_start_date",
            "program_cycle_end_date",
            "available_payment_records_count",
            "eligible_payments_count",
            "bank_reconciliation_success",
            "bank_reconciliation_error",
            "can_create_payment_verification_plan",
            "payment_verification_plans",
            "payment_verification_summary",
            "is_follow_up",
            "version",
        )

    def get_available_payment_records_count(self, payment_plan: PaymentPlan) -> int:
        return payment_plan.payment_items.filter(
            status__in=Payment.ALLOW_CREATE_VERIFICATION, delivered_quantity__gt=0
        ).count()

    def get_eligible_payments_count(self, obj: PaymentPlan) -> int:
        return obj.eligible_payments.count()


class PaymentVerificationPlanListSerializer(serializers.ModelSerializer):
    program_cycle_start_date = serializers.DateField(source="program_cycle.start_date")
    program_cycle_end_date = serializers.DateField(source="program_cycle.start_date")
    verification_status = serializers.CharField(source="payment_verification_summary.status")

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "unicef_id",
            "currency",
            "total_delivered_quantity",
            "program_cycle_start_date",
            "program_cycle_end_date",
            "verification_status",
            "updated_at",
        )


class PaymentPlanSerializer(AdminUrlSerializerMixin, serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display")
    follow_ups = FollowUpPaymentPlanSerializer(many=True, read_only=True)
    program = serializers.CharField(source="program_cycle.program.name")
    screen_beneficiary = serializers.BooleanField(source="program_cycle.program.screen_beneficiary", read_only=True)
    program_id = serializers.UUIDField(source="program_cycle.program.id", read_only=True)
    program_cycle_id = serializers.UUIDField(source="program_cycle.id", read_only=True)
    last_approval_process_by = serializers.SerializerMethodField()

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "unicef_id",
            "name",
            "status",
            "status_display",
            "total_households_count",
            "currency",
            "total_entitled_quantity",
            "total_entitled_quantity_usd",
            "total_delivered_quantity",
            "total_undelivered_quantity",
            "dispersion_start_date",
            "dispersion_end_date",
            "is_follow_up",
            "follow_ups",
            "program",
            "program_id",
            "program_cycle_id",
            "last_approval_process_date",
            "last_approval_process_by",
            "admin_url",
            "screen_beneficiary",
        )

    @staticmethod
    def get_last_approval_process_by(obj: PaymentPlan) -> str | None:
        return str(obj.last_approval_process_by) if obj.last_approval_process_by else None


class PaymentPlanListSerializer(serializers.ModelSerializer):
    follow_ups = FollowUpPaymentPlanSerializer(many=True, read_only=True)
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "unicef_id",
            "name",
            "status",
            "total_households_count",
            "total_individuals_count",
            "currency",
            "excluded_ids",
            "total_entitled_quantity",
            "total_delivered_quantity",
            "total_undelivered_quantity",
            "dispersion_start_date",
            "dispersion_end_date",
            "is_follow_up",
            "follow_ups",
            "created_by",
            "created_at",
            "updated_at",
        )

    @staticmethod
    def get_created_by(obj: PaymentPlan) -> str:
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"


class FinancialServiceProviderSerializer(serializers.ModelSerializer):
    is_payment_gateway = serializers.BooleanField()

    class Meta:
        model = FinancialServiceProvider
        fields = (
            "id",
            "name",
            "communication_channel",
            "is_payment_gateway",
        )


class ApprovalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Approval
        fields = (
            "type",
            "info",
            "comment",
            "created_at",
        )


class FilteredActionsListSerializer(serializers.Serializer):
    approval = ApprovalInfoSerializer(read_only=True, many=True)
    authorization = ApprovalInfoSerializer(read_only=True, many=True)
    finance_release = ApprovalInfoSerializer(read_only=True, many=True)
    reject = ApprovalInfoSerializer(read_only=True, many=True)


class ApprovalProcessSerializer(serializers.ModelSerializer):
    sent_for_approval_by = serializers.SerializerMethodField()
    sent_for_finance_release_by = serializers.SerializerMethodField()
    sent_for_authorization_by = serializers.SerializerMethodField()
    rejected_on = serializers.SerializerMethodField()
    actions = serializers.SerializerMethodField()

    class Meta:
        model = ApprovalProcess
        fields = (
            "sent_for_approval_by",
            "sent_for_authorization_by",
            "sent_for_finance_release_by",
            "sent_for_approval_date",
            "sent_for_authorization_date",
            "sent_for_finance_release_date",
            "approval_number_required",
            "authorization_number_required",
            "finance_release_number_required",
            "rejected_on",
            "actions",
        )

    def get_sent_for_approval_by(self, obj: PaymentPlan) -> str:
        return (
            f"{obj.sent_for_approval_by.first_name} {obj.sent_for_approval_by.last_name}"
            if obj.sent_for_approval_by
            else ""
        )

    def get_sent_for_authorization_by(self, obj: PaymentPlan) -> str:
        return (
            f"{obj.sent_for_authorization_by.first_name} {obj.sent_for_authorization_by.last_name}"
            if obj.sent_for_authorization_by
            else ""
        )

    def get_sent_for_finance_release_by(self, obj: PaymentPlan) -> str:
        return (
            f"{obj.sent_for_finance_release_by.first_name} {obj.sent_for_finance_release_by.last_name}"
            if obj.sent_for_finance_release_by
            else ""
        )

    def get_rejected_on(self, obj: ApprovalProcess) -> str | None:
        if obj.approvals.filter(type=Approval.REJECT).exists():
            if obj.sent_for_finance_release_date:
                return "IN_REVIEW"
            if obj.sent_for_authorization_date:
                return "IN_AUTHORIZATION"
            if obj.sent_for_approval_date:
                return "IN_APPROVAL"
        return None

    def get_actions(self, obj: ApprovalProcess) -> dict[str, Any]:
        actions_data = {
            "approval": obj.approvals.filter(type=Approval.APPROVAL),
            "authorization": obj.approvals.filter(type=Approval.AUTHORIZATION),
            "finance_release": obj.approvals.filter(type=Approval.FINANCE_RELEASE),
            "reject": obj.approvals.filter(type=Approval.REJECT),
        }

        return FilteredActionsListSerializer(actions_data).data


class DeliveryMechanismPerPaymentPlanSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="delivery_mechanism.name", read_only=True)
    code = serializers.CharField(source="delivery_mechanism.code", read_only=True)
    order = serializers.CharField(source="delivery_mechanism_order", read_only=True)
    fsp = FinancialServiceProviderSerializer(read_only=True)

    class Meta:
        model = DeliveryMechanismPerPaymentPlan
        fields = (
            "id",
            "name",
            "code",
            "order",
            "fsp",
        )


def _calculate_volume(payment_plan: "PaymentPlan", field: str) -> Decimal | None:
    if not payment_plan.financial_service_provider:
        return None
    return payment_plan.eligible_payments.aggregate(entitlement_sum=Coalesce(Sum(field), Decimal(0.0)))[
        "entitlement_sum"
    ]


class DeliveryMechanismSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryMechanism
        fields = (
            "id",
            "name",
            "code",
            "is_active",
            "transfer_type",
            "account_type",
        )


class VolumeByDeliveryMechanismSerializer(serializers.ModelSerializer):
    delivery_mechanism = DeliveryMechanismSerializer(read_only=True)
    volume = serializers.SerializerMethodField()
    volume_usd = serializers.SerializerMethodField()

    def get_volume(self, obj: DeliveryMechanismPerPaymentPlan) -> Decimal | None:  # non-usd
        return _calculate_volume(obj.payment_plan, "entitlement_quantity")

    def get_volume_usd(self, obj: DeliveryMechanismPerPaymentPlan) -> Decimal | None:
        return _calculate_volume(obj.payment_plan, "entitlement_quantity_usd")

    class Meta:
        model = DeliveryMechanismPerPaymentPlan
        fields = (
            "id",
            "delivery_mechanism",
            "volume",
            "volume_usd",
        )


class PaymentPlanExcludeBeneficiariesSerializer(serializers.Serializer):
    excluded_households_ids = serializers.ListField(child=serializers.CharField(), required=True)
    exclusion_reason = serializers.CharField(required=False)

    def validate_excluded_households_ids(self, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate IDs are not allowed.")
        return value


class RevertMarkPaymentAsFailedSerializer(serializers.Serializer):
    delivered_quantity = serializers.FloatField(required=True)
    delivery_date = serializers.DateField(required=True)


class PaymentPlanCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    target_population_id = serializers.UUIDField()
    dispersion_start_date = serializers.DateField(required=True)
    dispersion_end_date = serializers.DateField(required=True)
    currency = serializers.ChoiceField(required=True, choices=CURRENCY_CHOICES)
    version = serializers.IntegerField(required=False, read_only=True)

    def validate_version(self, value: int | None) -> int | None:
        payment_plan = self.context.get("payment_plan")
        if payment_plan and value:
            check_concurrency_version_in_mutation(value, payment_plan)
        return value

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "target_population_id",
            "dispersion_start_date",
            "dispersion_end_date",
            "currency",
            "version",
        )


class PaymentPlanCreateFollowUpSerializer(serializers.Serializer):
    dispersion_start_date = serializers.DateField(required=True)
    dispersion_end_date = serializers.DateField(required=True)


class PaymentPlanDetailSerializer(AdminUrlSerializerMixin, PaymentPlanListSerializer):
    background_action_status_display = serializers.CharField(source="get_background_action_status_display")
    program = ProgramSmallSerializer(read_only=True, source="program_cycle.program")
    program_cycle = ProgramCycleSmallSerializer()
    has_payment_list_export_file = serializers.BooleanField(source="has_export_file")
    has_fsp_delivery_mechanism_xlsx_template = serializers.SerializerMethodField()
    imported_file_name = serializers.CharField()
    payments_conflicts_count = serializers.SerializerMethodField()
    volume_by_delivery_mechanism = serializers.SerializerMethodField()
    delivery_mechanism = DeliveryMechanismSerializer(read_only=True)
    financial_service_provider = FinancialServiceProviderSerializer(read_only=True)
    delivery_mechanism_per_payment_plan = DeliveryMechanismPerPaymentPlanSerializer(read_only=True)
    bank_reconciliation_success = serializers.IntegerField()
    bank_reconciliation_error = serializers.IntegerField()
    can_create_payment_verification_plan = serializers.BooleanField()
    available_payment_records_count = serializers.SerializerMethodField()
    reconciliation_summary = serializers.SerializerMethodField()
    excluded_households = serializers.SerializerMethodField()
    excluded_individuals = serializers.SerializerMethodField()
    can_create_follow_up = serializers.SerializerMethodField()
    total_withdrawn_households_count = serializers.SerializerMethodField()
    unsuccessful_payments_count = serializers.SerializerMethodField()
    can_send_to_payment_gateway = serializers.BooleanField()
    can_split = serializers.SerializerMethodField()
    supporting_documents = PaymentPlanSupportingDocumentSerializer(many=True, read_only=True)
    total_households_count_with_valid_phone_no = serializers.SerializerMethodField()
    can_create_xlsx_with_fsp_auth_code = serializers.BooleanField()
    fsp_communication_channel = serializers.CharField()
    can_export_xlsx = serializers.SerializerMethodField()
    can_download_xlsx = serializers.SerializerMethodField()
    can_send_xlsx_password = serializers.SerializerMethodField()
    split_choices = serializers.SerializerMethodField()
    approval_process = ApprovalProcessSerializer(read_only=True, many=True)
    steficon_rule = RuleCommitSerializer(read_only=True)
    source_payment_plan = FollowUpPaymentPlanSerializer(read_only=True)
    eligible_payments_count = serializers.SerializerMethodField()
    funds_commitments = serializers.SerializerMethodField()
    available_funds_commitments = serializers.SerializerMethodField()
    payment_verification_plans = PaymentVerificationPlanSerializer(many=True, read_only=True)

    class Meta(PaymentPlanListSerializer.Meta):
        fields = PaymentPlanListSerializer.Meta.fields + (  # type: ignore
            "version",
            "background_action_status",
            "background_action_status_display",
            "start_date",
            "end_date",
            "program",
            "program_cycle",
            "has_payment_list_export_file",
            "has_fsp_delivery_mechanism_xlsx_template",
            "imported_file_name",
            "imported_file_date",
            "payments_conflicts_count",
            "delivery_mechanism",
            "delivery_mechanism_per_payment_plan",
            "volume_by_delivery_mechanism",
            "split_choices",
            "exclusion_reason",
            "exclude_household_error",
            "bank_reconciliation_success",
            "bank_reconciliation_error",
            "can_create_payment_verification_plan",
            "available_payment_records_count",
            "reconciliation_summary",
            "excluded_households",
            "excluded_individuals",
            "can_create_follow_up",
            "total_withdrawn_households_count",
            "unsuccessful_payments_count",
            "can_send_to_payment_gateway",
            "can_split",
            "supporting_documents",
            "total_households_count_with_valid_phone_no",
            "can_create_xlsx_with_fsp_auth_code",
            "fsp_communication_channel",
            "financial_service_provider",
            "can_export_xlsx",
            "can_download_xlsx",
            "can_send_xlsx_password",
            "approval_process",
            "total_entitled_quantity_usd",
            "total_entitled_quantity_revised_usd",
            "total_delivered_quantity_usd",
            "total_undelivered_quantity_usd",
            "male_children_count",
            "female_children_count",
            "male_adults_count",
            "female_adults_count",
            "steficon_rule",
            "source_payment_plan",
            "exchange_rate",
            "eligible_payments_count",
            "funds_commitments",
            "available_funds_commitments",
            "payment_verification_plans",
            "admin_url",
        )

    @staticmethod
    def _has_fsp_delivery_mechanism_xlsx_template(payment_plan: PaymentPlan) -> bool:
        delivery_mechanism = getattr(payment_plan, "delivery_mechanism", None)
        financial_service_provider = getattr(payment_plan, "financial_service_provider", None)
        if not delivery_mechanism or not financial_service_provider:
            return False
        if not payment_plan.financial_service_provider.get_xlsx_template(payment_plan.delivery_mechanism):
            return False
        return True

    def get_has_fsp_delivery_mechanism_xlsx_template(self, payment_plan: PaymentPlan) -> bool:
        return self._has_fsp_delivery_mechanism_xlsx_template(payment_plan)

    def get_payments_conflicts_count(self, payment_plan: PaymentPlan) -> int:
        return payment_plan.payment_items.filter(excluded=False, payment_plan_hard_conflicted=True).count()

    def get_available_payment_records_count(self, payment_plan: PaymentPlan) -> int:
        return payment_plan.payment_items.filter(
            status__in=Payment.ALLOW_CREATE_VERIFICATION, delivered_quantity__gt=0
        ).count()

    @staticmethod
    def get_reconciliation_summary(obj: PaymentPlan) -> dict[str, int]:
        return obj.eligible_payments.aggregate(
            delivered_fully=Count("id", filter=Q(status=Payment.STATUS_DISTRIBUTION_SUCCESS)),
            delivered_partially=Count("id", filter=Q(status=Payment.STATUS_DISTRIBUTION_PARTIAL)),
            not_delivered=Count("id", filter=Q(status=Payment.STATUS_NOT_DISTRIBUTED)),
            unsuccessful=Count(
                "id",
                filter=Q(status__in=Payment.FAILED_STATUSES),
            ),
            pending=Count("id", filter=Q(status__in=Payment.PENDING_STATUSES)),
            reconciled=Count("id", filter=~Q(status__in=Payment.PENDING_STATUSES)),
            number_of_payments=Count("id"),
        )

    @staticmethod
    def get_excluded_households(obj: PaymentPlan) -> dict[str, Any]:
        qs = (
            Household.objects.filter(unicef_id__in=obj.excluded_beneficiaries_ids)
            if not obj.is_social_worker_program
            else Household.objects.none()
        )
        return HouseholdSmallSerializer(qs, many=True).data

    @staticmethod
    def get_excluded_individuals(obj: PaymentPlan) -> dict[str, Any]:
        qs = (
            Individual.objects.filter(unicef_id__in=obj.excluded_beneficiaries_ids)
            if obj.is_social_worker_program
            else Individual.objects.none()
        )
        return IndividualSmallSerializer(qs, many=True).data

    @staticmethod
    def get_can_create_follow_up(parent: PaymentPlan) -> bool:
        # Check there are payments in error/not distributed status and excluded withdrawn households
        if parent.is_follow_up:
            return False

        qs = parent.unsuccessful_payments_for_follow_up()

        # Check if all payments are used in FPPs
        follow_up_payment = parent.payments_used_in_follow_payment_plans()

        return qs.exists() and set(follow_up_payment.values_list("source_payment_id", flat=True)) != set(
            qs.values_list("id", flat=True)
        )

    @staticmethod
    def get_total_withdrawn_households_count(parent: PaymentPlan) -> int:
        return (
            parent.eligible_payments.filter(household__withdrawn=True)
            .exclude(
                # Exclude beneficiaries who are currently in different follow-up Payment Plan within the same cycle
                household_id__in=Payment.objects.filter(
                    is_follow_up=True,
                    parent__source_payment_plan=parent,
                    parent__program_cycle=parent.program_cycle,
                    excluded=False,
                )
                .exclude(parent=parent)
                .values_list("household_id", flat=True)
            )
            .count()
        )

    @staticmethod
    def get_unsuccessful_payments_count(parent: PaymentPlan) -> int:
        return parent.unsuccessful_payments_for_follow_up().count()

    @staticmethod
    def get_can_split(parent: PaymentPlan) -> bool:
        if parent.status != PaymentPlan.Status.ACCEPTED:
            return False

        if parent.splits.filter(
            sent_to_payment_gateway=True,
        ).exists():
            return False

        return True

    @staticmethod
    def get_total_households_count_with_valid_phone_no(parent: PaymentPlan) -> int:
        return parent.eligible_payments.exclude(
            household__head_of_household__phone_no_valid=False,
            household__head_of_household__phone_no_alternative_valid=False,
        ).count()

    def get_can_export_xlsx(self, obj: PaymentPlan) -> bool:
        if obj.status in [PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED]:
            user = self.context.get("request").user
            if obj.fsp_communication_channel == FinancialServiceProvider.COMMUNICATION_CHANNEL_API:
                if not user.has_perm(Permissions.PM_DOWNLOAD_FSP_AUTH_CODE.value, obj.business_area):
                    return False
                return obj.can_create_xlsx_with_fsp_auth_code

            if obj.fsp_communication_channel == FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX:
                if not user.has_perm(Permissions.PM_EXPORT_XLSX_FOR_FSP.value, obj.business_area):
                    return False
                return self._has_fsp_delivery_mechanism_xlsx_template(obj)

        return False

    def get_can_download_xlsx(self, obj: PaymentPlan) -> bool:
        if obj.status in [PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED]:
            user = self.context.get("request").user
            if obj.fsp_communication_channel == FinancialServiceProvider.COMMUNICATION_CHANNEL_API:
                if not user.has_perm(Permissions.PM_DOWNLOAD_FSP_AUTH_CODE.value, obj.business_area):
                    return False
                return obj.has_export_file

            if obj.fsp_communication_channel == FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX:
                if not user.has_perm(Permissions.PM_DOWNLOAD_XLSX_FOR_FSP.value, obj.business_area):
                    return False
                return obj.has_export_file

        return False

    def get_can_send_xlsx_password(self, obj: PaymentPlan) -> bool:
        if obj.status in [PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED]:
            user = self.context.get("request").user
            if obj.fsp_communication_channel == FinancialServiceProvider.COMMUNICATION_CHANNEL_API:
                if not user.has_perm(Permissions.PM_SEND_XLSX_PASSWORD.value, obj.business_area):
                    return False
                return obj.has_export_file
        return False

    def get_split_choices(self, obj: PaymentPlan) -> list[dict[str, Any]]:
        return to_choice_object(PaymentPlanSplit.SplitType.choices)

    def get_volume_by_delivery_mechanism(self, obj: PaymentPlan) -> dict[str, Any]:
        qs = DeliveryMechanismPerPaymentPlan.objects.filter(payment_plan=obj).order_by("delivery_mechanism_order")
        return VolumeByDeliveryMechanismSerializer(qs, many=True).data

    def get_eligible_payments_count(self, obj: PaymentPlan) -> int:
        return obj.eligible_payments.count()

    def get_payment_verification_plans_count(self, obj: PaymentPlan) -> int:
        return obj.payment_verification_plans.count()

    def get_funds_commitments(self, obj: PaymentPlan) -> dict[str, Any] | None:
        available_items_qs = FundsCommitmentItem.objects.filter(payment_plan=obj, office=obj.business_area)
        # Prefetch related items grouped by `funds_commitment_group`
        group = (
            FundsCommitmentGroup.objects.filter(funds_commitment_items__in=available_items_qs)
            .distinct()
            .prefetch_related(Prefetch("funds_commitment_items", queryset=available_items_qs, to_attr="filtered_items"))
        ).first()

        if group:
            return FundsCommitmentSerializer(
                {
                    "funds_commitment_number": group.funds_commitment_number,
                    "funds_commitment_items": group.filtered_items,
                }
            ).data
        return None

    def get_available_funds_commitments(self, obj: PaymentPlan) -> list[dict[str, Any]]:
        available_items_qs = FundsCommitmentItem.objects.filter(
            Q(payment_plan__isnull=True) | Q(payment_plan=obj), office=obj.business_area
        )

        # Prefetch related items grouped by `funds_commitment_group`
        groups = (
            FundsCommitmentGroup.objects.filter(funds_commitment_items__in=available_items_qs)
            .distinct()
            .prefetch_related(Prefetch("funds_commitment_items", queryset=available_items_qs, to_attr="filtered_items"))
        )

        return [
            FundsCommitmentSerializer(
                {
                    "funds_commitment_number": group.funds_commitment_number,
                    "funds_commitment_items": group.filtered_items,
                }
            ).data
            for group in groups
        ]


class PaymentPlanBulkActionSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.CharField())
    action = serializers.ChoiceField(PaymentPlan.Action.choices)
    comment = serializers.CharField(required=False, allow_blank=True)


class TargetPopulationDetailSerializer(AdminUrlSerializerMixin, PaymentPlanListSerializer):
    background_action_status = serializers.CharField(source="get_background_action_status_display")
    program = ProgramSmallSerializer(read_only=True, source="program_cycle.program")
    program_cycle = ProgramCycleSmallSerializer()
    rules = TargetingCriteriaRuleSerializer(many=True, read_only=True)
    steficon_rule_targeting = RuleCommitSerializer(read_only=True)
    delivery_mechanism = DeliveryMechanismSerializer(read_only=True)
    financial_service_provider = FinancialServiceProviderSerializer(read_only=True)
    failed_wallet_validation_collectors_ids = serializers.SerializerMethodField()
    screen_beneficiary = serializers.BooleanField(source="program_cycle.program.screen_beneficiary", read_only=True)

    class Meta(PaymentPlanListSerializer.Meta):
        fields = PaymentPlanListSerializer.Meta.fields + (  # type: ignore
            "background_action_status",
            "status",
            "start_date",
            "end_date",
            "program",
            "program_cycle",
            "exclusion_reason",
            "male_children_count",
            "female_children_count",
            "male_adults_count",
            "female_adults_count",
            "rules",
            "steficon_rule_targeting",
            "vulnerability_score_min",
            "vulnerability_score_max",
            "delivery_mechanism",
            "financial_service_provider",
            "failed_wallet_validation_collectors_ids",
            "version",
            "admin_url",
            "screen_beneficiary",
            "flag_exclude_if_on_sanction_list",
            "flag_exclude_if_active_adjudication_ticket",
            "build_status",
        )

    @staticmethod
    def get_failed_wallet_validation_collectors_ids(obj: PaymentPlan) -> list[str]:
        fsp = getattr(obj, "financial_service_provider", None)
        dm = getattr(obj, "delivery_mechanism", None)
        if not fsp or not dm:
            return []
        return list(
            obj.payment_items.select_related("collector")
            .filter(
                has_valid_wallet=False,
            )
            .values_list("collector__unicef_id", flat=True)
        )

    @staticmethod
    def get_status_display(obj: PaymentPlan) -> str:
        return obj.get_status_display().upper() if obj.status in PaymentPlan.PRE_PAYMENT_PLAN_STATUSES else "ASSIGNED"


class PaymentVerificationDetailsSerializer(AdminUrlSerializerMixin, serializers.ModelSerializer):
    payment_verification_plan_unicef_id = serializers.CharField(source="payment_verification_plan.unicef_id")
    verification_channel = serializers.CharField(source="payment_verification_plan.verification_channel")

    class Meta:
        model = PaymentVerification
        fields = (
            "id",
            "received_amount",
            "status",
            "payment_verification_plan_unicef_id",
            "verification_channel",
            "admin_url",
            "version",
        )


class PaymentListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    household_id = serializers.UUIDField(read_only=True)
    collector_id = serializers.UUIDField(read_only=True)
    household_unicef_id = serializers.CharField(source="household.unicef_id")
    household_size = serializers.IntegerField(source="household.size")
    household_status = serializers.SerializerMethodField()
    hoh_full_name = serializers.CharField(source="head_of_household.full_name")
    hoh_phone_no = serializers.CharField(source="head_of_household.phone_no")
    hoh_phone_no_alternative = serializers.CharField(source="head_of_household.phone_no_alternative")
    collector_phone_no = serializers.CharField(source="collector.phone_no")
    collector_phone_no_alt = serializers.CharField(source="collector.phone_no_alternative")
    snapshot_collector_full_name = serializers.SerializerMethodField(help_text="Get from Household Snapshot")
    fsp_name = serializers.SerializerMethodField()
    fsp_auth_code = serializers.SerializerMethodField()
    verification = serializers.SerializerMethodField()
    payment_plan_hard_conflicted = serializers.SerializerMethodField()
    payment_plan_hard_conflicted_data = serializers.SerializerMethodField()
    payment_plan_soft_conflicted = serializers.SerializerMethodField()
    payment_plan_soft_conflicted_data = serializers.SerializerMethodField()
    people_individual = IndividualListSerializer(read_only=True)
    program_name = serializers.CharField(source="parent.program.name")

    status_display = serializers.CharField(
        source="get_status_display",  # <- metoda modelu
        read_only=True,
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "unicef_id",
            "household_id",
            "household_unicef_id",
            "household_size",
            "household_admin2",
            "household_status",
            "hoh_phone_no",
            "hoh_phone_no_alternative",
            "snapshot_collector_full_name",
            "fsp_name",
            "entitlement_quantity",
            "entitlement_quantity_usd",
            "delivered_quantity",
            "delivered_quantity_usd",
            "delivery_date",
            "delivery_type",
            "status",
            "status_display",
            "currency",
            "fsp_auth_code",
            "hoh_full_name",
            "collector_id",
            "collector_phone_no",
            "collector_phone_no_alt",
            "verification",
            "payment_plan_hard_conflicted",
            "payment_plan_hard_conflicted_data",
            "payment_plan_soft_conflicted",
            "payment_plan_soft_conflicted_data",
            "people_individual",
            "program_name",
        )

    @classmethod
    def get_collector_field(cls, payment: "Payment", field_name: str) -> str | None:
        """return primary_collector or alternate_collector field value or None"""
        if household_snapshot := getattr(payment, "household_snapshot", None):
            household_snapshot_data = household_snapshot.snapshot_data
            collector_data = (
                household_snapshot_data.get("primary_collector")
                or household_snapshot_data.get("alternate_collector")
                or {}
            )
            return collector_data.get(field_name)
        return None

    def get_snapshot_collector_full_name(self, obj: Payment) -> Any:
        return PaymentListSerializer.get_collector_field(obj, "full_name")

    def get_fsp_name(self, obj: Payment) -> str:
        return obj.financial_service_provider.name if obj.financial_service_provider else ""

    def get_fsp_auth_code(self, obj: Payment) -> str:
        if "request" not in self.context:
            return ""
        user = self.context["request"].user
        if not user.has_perm(
            Permissions.PM_VIEW_FSP_AUTH_CODE.value,
            obj.program or obj.business_area,
        ):
            return ""
        return obj.fsp_auth_code or ""

    def get_verification(self, obj: Payment) -> dict[str, Any]:
        # TODO: only one Verification per Payment?
        return PaymentVerificationDetailsSerializer(obj.payment_verifications.first()).data

    def get_household_status(self, obj: Payment) -> str:
        return STATUS_ACTIVE if not obj.household.withdrawn else STATUS_INACTIVE

    def get_payment_plan_hard_conflicted(self, obj: Payment) -> bool:
        return obj.parent.status == PaymentPlan.Status.OPEN and getattr(obj, "payment_plan_hard_conflicted", False)

    def get_payment_plan_soft_conflicted(self, obj: Payment) -> bool:
        return obj.parent.status == PaymentPlan.Status.OPEN and getattr(obj, "payment_plan_soft_conflicted", False)

    def get_payment_plan_hard_conflicted_data(self, obj: Payment) -> list[Any]:
        if obj.parent.status != PaymentPlan.Status.OPEN:
            return []
        conflicts_data = getattr(obj, "payment_plan_hard_conflicted_data", [])
        return [json.loads(conflict) for conflict in conflicts_data]

    def get_payment_plan_soft_conflicted_data(self, obj: Payment) -> list[Any]:
        if obj.parent.status != PaymentPlan.Status.OPEN:
            return []
        conflicts_data = getattr(obj, "payment_plan_soft_conflicted_data", [])
        return [json.loads(conflict) for conflict in conflicts_data]


class PaymentDetailSerializer(AdminUrlSerializerMixin, PaymentListSerializer):
    parent = PaymentPlanDetailSerializer()
    source_payment = PaymentListSerializer()
    household = HouseholdDetailSerializer()
    delivery_mechanism = DeliveryMechanismSerializer(source="parent.delivery_mechanism")
    collector = IndividualDetailSerializer()
    snapshot_collector_account_data = serializers.SerializerMethodField()

    class Meta(PaymentListSerializer.Meta):
        fields = PaymentListSerializer.Meta.fields + (  # type: ignore
            "parent",
            "admin_url",
            "source_payment",
            "household",
            "delivery_mechanism",
            "collector",
            "reason_for_unsuccessful_payment",
            "additional_document_number",
            "additional_document_type",
            "additional_collector_name",
            "transaction_reference_id",
            "snapshot_collector_account_data",
        )

    @staticmethod
    def collector_field(payment: "Payment", field_name: str) -> None | str | dict:
        """return primary_collector or alternate_collector field value or None"""
        if household_snapshot := getattr(payment, "household_snapshot", None):
            household_snapshot_data = household_snapshot.snapshot_data
            collector_data = (
                household_snapshot_data.get("primary_collector")
                or household_snapshot_data.get("alternate_collector")
                or {}
            )
            return collector_data.get(field_name)
        return None

    def get_snapshot_collector_account_data(self, obj: Payment) -> Any:
        return PaymentListSerializer.get_collector_field(obj, "account_data")


class PaymentSmallSerializer(serializers.ModelSerializer):
    verification = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            "id",
            "unicef_id",
            "entitlement_quantity",
            "delivered_quantity",
            "parent_id",
            "verification",
        )

    def get_verification(self, obj: Payment) -> str | None:
        verification = obj.payment_verifications.first()
        return getattr(verification, "id", None)


class VerificationDetailSerializer(AdminUrlSerializerMixin, serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")
    payment_verification_plan = PaymentVerificationPlanSerializer()

    class Meta:
        model = PaymentVerification
        fields = (
            "id",
            "admin_url",
            "status",
            "received_amount",
            "payment",
            "payment_verification_plan",
        )


class VerificationListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")
    verification_channel = serializers.CharField(source="payment_verification_plan.verification_channel")
    verification_plan_unicef_id = serializers.CharField(source="payment_verification_plan.unief_id")
    household_unicef_id = serializers.CharField(source="payment.household.unicef_id")
    household_size = serializers.IntegerField(source="household.size")
    snapshot_collector_full_name = serializers.SerializerMethodField(help_text="Get from Household Snapshot")
    payment = PaymentListSerializer(read_only=True)

    class Meta:
        model = PaymentVerification
        fields = (
            "id",
            "status",
            "verification_channel",
            "verification_plan_unicef_id",
            "received_amount",
        )

    @classmethod
    def get_collector_field(cls, payment: "Payment", field_name: str) -> str | None:
        """return primary_collector or alternate_collector field value or None"""
        if household_snapshot := getattr(payment, "household_snapshot", None):
            household_snapshot_data = household_snapshot.snapshot_data
            collector_data = (
                household_snapshot_data.get("primary_collector")
                or household_snapshot_data.get("alternate_collector")
                or {}
            )
            return collector_data.get(field_name)
        return None

    def get_snapshot_collector_full_name(self, obj: Payment) -> Any:
        return PaymentListSerializer.get_collector_field(obj, "full_name")


class FullListSerializer(serializers.Serializer):
    excluded_admin_areas = serializers.ListField(child=serializers.CharField())


class AgeSerializer(serializers.Serializer):
    min = serializers.IntegerField()
    max = serializers.IntegerField()


class RandomSamplingSerializer(serializers.Serializer):
    confidence_interval = serializers.FloatField(required=True)
    margin_of_error = serializers.FloatField(required=True)
    excluded_admin_areas = serializers.ListField(child=serializers.CharField())
    age = AgeSerializer()
    sex = serializers.CharField()


class RapidProSerializer(serializers.Serializer):
    flow_id = serializers.CharField(required=True)


class PaymentVerificationPlanCreateSerializer(serializers.Serializer):
    sampling = serializers.CharField(required=True)
    verification_channel = serializers.CharField(required=True)
    full_list_arguments = FullListSerializer()
    random_sampling_arguments = RandomSamplingSerializer(allow_null=True)
    rapid_pro_arguments = RapidProSerializer(allow_null=True)


class PaymentVerificationPlanActivateSerializer(serializers.Serializer):
    version = serializers.IntegerField(required=False)


class PaymentVerificationPlanImportSerializer(serializers.Serializer):
    file = serializers.FileField(use_url=False, required=True)
    version = serializers.IntegerField(required=False)

    def validate_file(self, file: Any) -> Any:
        allowed_extensions = ["xlsx"]
        extension = file.name.split(".")[-1].lower()
        if extension not in allowed_extensions:
            raise serializers.ValidationError(f"Unsupported file type ({extension}).")
        return file


class PaymentVerificationUpdateSerializer(serializers.Serializer):
    received_amount = serializers.FloatField(required=False)
    received = serializers.BooleanField(required=True)
    version = serializers.IntegerField(required=False)


class PendingPaymentSerializer(serializers.ModelSerializer):
    household_unicef_id = serializers.CharField(source="household.unicef_id")
    hoh_full_name = serializers.SerializerMethodField()
    household_size = serializers.IntegerField(source="household.size")
    household_id = serializers.CharField(source="household.id")

    class Meta:
        model = Payment
        fields = (
            "id",
            "household_id",
            "household_unicef_id",
            "hoh_full_name",
            "household_size",
            "household_admin2",
            "vulnerability_score",
        )

    def get_hoh_full_name(self, obj: Payment) -> str:
        return obj.head_of_household.full_name if obj.head_of_household else ""


class TargetPopulationCreateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(required=True)
    program_cycle_id = serializers.UUIDField(required=True)
    rules = TargetingCriteriaRuleSerializer(many=True, required=True)
    excluded_ids = serializers.CharField(required=False, allow_blank=True)
    exclusion_reason = serializers.CharField(required=False, allow_blank=True)
    fsp_id = serializers.UUIDField(required=False, allow_null=True)
    delivery_mechanism_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vulnerability_score_min = serializers.DecimalField(required=False, max_digits=6, decimal_places=3)
    vulnerability_score_max = serializers.DecimalField(required=False, max_digits=6, decimal_places=3)
    version = serializers.IntegerField(required=False, read_only=True)
    flag_exclude_if_on_sanction_list = serializers.BooleanField()
    flag_exclude_if_active_adjudication_ticket = serializers.BooleanField()

    class Meta:
        model = PaymentPlan
        fields = (
            "id",
            "version",
            "name",
            "program_cycle_id",
            "rules",
            "excluded_ids",
            "exclusion_reason",
            "fsp_id",
            "delivery_mechanism_code",
            "vulnerability_score_min",
            "vulnerability_score_max",
            "flag_exclude_if_on_sanction_list",
            "flag_exclude_if_active_adjudication_ticket",
        )

    def get_program(self) -> Program:
        request = self.context["request"]
        business_area_slug = request.parser_context["kwargs"]["business_area_slug"]
        program_slug = request.parser_context["kwargs"]["program_slug"]
        return get_object_or_404(Program, business_area__slug=business_area_slug, slug=program_slug)

    @transaction.atomic
    def create(self, data: dict) -> PaymentPlan:
        request = self.context["request"]
        program = self.get_program()
        data["program"] = program
        data["created_by"] = request.user
        business_area = program.business_area

        payment_plan = PaymentPlanService.create(
            input_data=data, user=request.user, business_area_slug=business_area.slug
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=str(program.pk),
            new_object=payment_plan,
        )
        return payment_plan

    def update(self, payment_plan: PaymentPlan, validated_data: dict) -> PaymentPlan:
        request = self.context["request"]
        check_concurrency_version_in_mutation(validated_data.get("version"), payment_plan)
        old_payment_plan = copy_model_object(payment_plan)
        payment_plan = PaymentPlanService(payment_plan=payment_plan).update(input_data=validated_data)
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return payment_plan


class TargetPopulationCopySerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    target_population_id = serializers.CharField(required=True)
    program_cycle_id = serializers.CharField(required=True)


class ApplyEngineFormulaSerializer(serializers.Serializer):
    engine_formula_rule_id = serializers.CharField(required=True)
    version = serializers.IntegerField(required=False)


class FspChoiceSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = FinancialServiceProvider
        fields = (
            "id",
            "name",
        )


class DeliveryMechanismChoiceSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    code = serializers.CharField(required=True)


class FspChoicesSerializer(serializers.Serializer):
    delivery_mechanism = DeliveryMechanismChoiceSerializer()
    fsps = FspChoiceSerializer(many=True)


class FSPXlsxTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialServiceProviderXlsxTemplate
        fields = (
            "id",
            "name",
        )


class AssignFundsCommitmentsSerializer(serializers.Serializer):
    fund_commitment_items_ids = serializers.ListSerializer(child=serializers.CharField(), required=False)
