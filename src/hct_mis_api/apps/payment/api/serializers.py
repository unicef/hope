import base64
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from hct_mis_api.apps.account.api.fields import Base64ModelField
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.api.mixins import AdminUrlSerializerMixin
from hct_mis_api.apps.core.api.serializers import ChoiceSerializer
from hct_mis_api.apps.core.utils import decode_id_string, to_choice_object
from hct_mis_api.apps.household.api.serializers.household import (
    HouseholdDetailSerializer,
)
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.payment.models import (
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProvider,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
    PaymentPlanSupportingDocument,
)

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


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
    id = Base64ModelField(model_name="PaymentPlan")
    status = serializers.CharField(source="get_status_display")
    currency = serializers.CharField(source="get_currency_display")
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

    def get_created_by(self, obj: PaymentPlan) -> str:
        if not obj.created_by:
            return "-"
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


class DeliveryMechanismPerPaymentPlanSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="delivery_mechanism.name")
    code = serializers.CharField(source="delivery_mechanism.code")
    order = serializers.CharField(source="delivery_mechanism_order")
    fsp = FinancialServiceProviderSerializer(read_only=True)

    class Meta:
        model = DeliveryMechanismPerPaymentPlan
        fields = (
            "id",
            "name",
            "code",
            "order",
            "chosen_configuration",
            "fsp",
        )


class ReconciliationSummarySerializer(serializers.Serializer):
    delivered_fully = serializers.IntegerField()
    delivered_partially = serializers.IntegerField()
    not_delivered = serializers.IntegerField()
    unsuccessful = serializers.IntegerField()
    pending = serializers.IntegerField()
    force_failed = serializers.IntegerField()
    number_of_payments = serializers.IntegerField()
    reconciled = serializers.IntegerField()


def _calculate_volume(
    delivery_mechanism_per_payment_plan: "DeliveryMechanismPerPaymentPlan", field: str
) -> Optional[Decimal]:
    if not delivery_mechanism_per_payment_plan.financial_service_provider:
        return None
    payments = delivery_mechanism_per_payment_plan.payment_plan.eligible_payments.filter(
        financial_service_provider=delivery_mechanism_per_payment_plan.financial_service_provider,
    )
    return payments.aggregate(entitlement_sum=Coalesce(Sum(field), Decimal(0.0)))["entitlement_sum"]


class VolumeByDeliveryMechanismSerializer(serializers.ModelSerializer):
    delivery_mechanism = DeliveryMechanismPerPaymentPlanSerializer(read_only=True)
    volume = serializers.FloatField()
    volume_usd = serializers.FloatField()

    def get_delivery_mechanism(self, info: Any) -> "VolumeByDeliveryMechanismSerializer":
        return self

    def get_volume(self, info: Any) -> Optional[Decimal]:  # non-usd
        return _calculate_volume(self, "entitlement_quantity")  # type: ignore

    def get_volume_usd(self, info: Any) -> Optional[Decimal]:
        return _calculate_volume(self, "entitlement_quantity_usd")  # type: ignore

    class Meta:
        model = DeliveryMechanismPerPaymentPlan
        fields = (
            "id",
            "delivery_mechanism",
            "volume",
            "volume_usd",
        )


class PaymentPlanDetailSerializer(AdminUrlSerializerMixin, PaymentPlanListSerializer):
    background_action_status = serializers.CharField(source="get_background_action_status_display")
    program = serializers.CharField(source="program_cycle.program.name")
    has_payment_list_export_file = serializers.BooleanField(source="has_export_file")
    has_fsp_delivery_mechanism_xlsx_template = serializers.SerializerMethodField()
    imported_file_name = serializers.CharField()
    payments_conflicts_count = serializers.SerializerMethodField()
    volume_by_delivery_mechanism = VolumeByDeliveryMechanismSerializer(many=True, read_only=True)
    delivery_mechanisms = DeliveryMechanismPerPaymentPlanSerializer(many=True, read_only=True)
    bank_reconciliation_success = serializers.IntegerField()
    bank_reconciliation_error = serializers.IntegerField()
    can_create_payment_verification_plan = serializers.BooleanField()
    available_payment_records_count = serializers.SerializerMethodField()
    reconciliation_summary = ReconciliationSummarySerializer(read_only=True)
    excluded_households = HouseholdDetailSerializer(many=True, read_only=True)
    # excluded_individuals = IndividualDetailSerializer(many=True, read_only=True)
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
    split_choices = ChoiceSerializer(many=True, read_only=True)

    class Meta(PaymentPlanListSerializer.Meta):
        fields = PaymentPlanListSerializer.Meta.fields + (  # type: ignore
            "background_action_status",
            "start_date",
            "end_date",
            "program",
            "has_payment_list_export_file",
            "has_fsp_delivery_mechanism_xlsx_template",
            "imported_file_name",
            "payments_conflicts_count",
            "delivery_mechanisms",
            "volume_by_delivery_mechanism",
            "split_choices",
            "bank_reconciliation_success",
            "bank_reconciliation_error",
            "can_create_payment_verification_plan",
            "available_payment_records_count",
            "reconciliation_summary",
            "excluded_households",
            # "excluded_individuals",
            "can_create_follow_up",
            "total_withdrawn_households_count",
            "unsuccessful_payments_count",
            "can_send_to_payment_gateway",
            "can_split",
            "supporting_documents",
            "total_households_count_with_valid_phone_no",
            "can_create_xlsx_with_fsp_auth_code",
            "fsp_communication_channel",
            "can_export_xlsx",
            "can_download_xlsx",
            "can_send_xlsx_password",
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
        return payment_plan.payment_items.filter(
            status__in=Payment.ALLOW_CREATE_VERIFICATION, delivered_quantity__gt=0
        ).count()

    @staticmethod
    def get_reconciliation_summary(parent: PaymentPlan) -> Dict[str, int]:
        return parent.eligible_payments.aggregate(
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
    def get_excluded_households(parent: PaymentPlan) -> "QuerySet [Household]":
        return (
            Household.objects.filter(unicef_id__in=parent.excluded_beneficiaries_ids)
            if not parent.is_social_worker_program
            else Household.objects.none()
        )

    @staticmethod
    def get_excluded_individuals(parent: PaymentPlan) -> "QuerySet [Individual]":
        return (
            Individual.objects.filter(unicef_id__in=parent.excluded_beneficiaries_ids)
            if parent.is_social_worker_program
            else Individual.objects.none()
        )

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

    @staticmethod
    def get_split_choices(parent: PaymentPlan, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentPlanSplit.SplitType.choices)

    @staticmethod
    def get_volume_by_delivery_mechanism(parent: PaymentPlan, info: Any) -> "QuerySet[DeliveryMechanismPerPaymentPlan]":
        return DeliveryMechanismPerPaymentPlan.objects.filter(payment_plan=parent).order_by("delivery_mechanism_order")


class PaymentPlanBulkActionSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.CharField())
    action = serializers.ChoiceField(PaymentPlan.Action.choices)
    comment = serializers.CharField(required=False, allow_blank=True)


class TargetPopulationDetailSerializer(AdminUrlSerializerMixin, PaymentPlanListSerializer):
    background_action_status = serializers.CharField(source="get_background_action_status_display")
    program = serializers.CharField(source="program_cycle.program.name")
    program_cycle = serializers.CharField(source="program_cycle.title")
    # TODO: add Steficon formula
    # TODO: add Targeting Criteria

    class Meta(PaymentPlanListSerializer.Meta):
        fields = PaymentPlanListSerializer.Meta.fields + (  # type: ignore
            "background_action_status",
            "start_date",
            "end_date",
            "program",
            "program_cycle",
            "male_children_count",
            "female_children_count",
            "male_adults_count",
            "female_adults_count",
        )


class PaymentListSerializer(serializers.ModelSerializer):
    id = Base64ModelField(model_name="Payment")
    status = serializers.CharField(source="get_status_display")
    household_unicef_id = serializers.CharField(source="household.unicef_id")
    household_size = serializers.IntegerField(source="household.size")
    snapshot_collector_full_name = serializers.SerializerMethodField(help_text="Get from Household Snapshot")
    fsp_name = serializers.SerializerMethodField()
    fsp_auth_code = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            "id",
            "unicef_id",
            "household_unicef_id",
            "household_size",
            "household_admin2",
            "snapshot_collector_full_name",
            "fsp_name",
            "entitlement_quantity",
            "delivered_quantity",
            "status",
            "fsp_auth_code",
        )

    @classmethod
    def get_collector_field(cls, payment: "Payment", field_name: str) -> Union[None, str, Dict]:
        """return primary_collector or alternate_collector field value or None"""
        if household_snapshot := getattr(payment, "household_snapshot", None):
            household_snapshot_data = household_snapshot.snapshot_data
            collector_data = (
                household_snapshot_data.get("primary_collector")
                or household_snapshot_data.get("alternate_collector")
                or dict()
            )
            return collector_data.get(field_name)
        return None

    def get_snapshot_collector_full_name(self, obj: Payment) -> Any:
        return PaymentListSerializer.get_collector_field(obj, "full_name")

    def get_fsp_name(self, obj: Payment) -> str:
        return obj.financial_service_provider.name if obj.financial_service_provider else ""

    def get_fsp_auth_code(self, obj: Payment) -> str:
        user = self.context.get("request").user

        if not user.has_perm(
            Permissions.PM_VIEW_FSP_AUTH_CODE.value,
            obj.program or obj.business_area,
        ):
            return ""
        return obj.fsp_auth_code or ""


class TPHouseholdListSerializer(serializers.ModelSerializer):
    id = Base64ModelField(model_name="Payment")
    household_unicef_id = serializers.CharField(source="household.unicef_id")
    hoh_full_name = serializers.SerializerMethodField()
    household_size = serializers.IntegerField(source="household.size")

    class Meta:
        model = Payment
        fields = (
            "id",
            "household_unicef_id",
            "hoh_full_name",
            "household_size",
            "household_admin2",
            "vulnerability_score",
        )

    def get_hoh_full_name(self, obj: Payment) -> str:
        return obj.head_of_household.full_name if obj.head_of_household else ""
